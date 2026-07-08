from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import RegionEnum
from app.models.finance import Loan, LoanEmiHistory, Subscription, SubscriptionPaymentHistory
from app.models.user import User
from app.services.finance_calculations import (
    current_month_net_worth,
    debt_outstanding_total,
    expense_total,
    gold_current_total,
    income_total,
    investments_current_total,
    loan_outstanding_total,
)

router = APIRouter(prefix="/net-worth", tags=["net-worth"])


def monthly_emi_summary(db: Session, user_id: int, region: RegionEnum, ref_date: date) -> dict:
    month = ref_date.month
    year = ref_date.year

    loans = db.query(Loan).filter(Loan.user_id == user_id, Loan.region == region, Loan.remaining_months > 0).all()
    subscriptions = db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.region == region).all()

    paid_loan_rows = (
        db.query(LoanEmiHistory)
        .join(Loan, Loan.id == LoanEmiHistory.loan_id)
        .filter(
            Loan.user_id == user_id,
            Loan.region == region,
            LoanEmiHistory.month == month,
            LoanEmiHistory.year == year,
            LoanEmiHistory.status == "completed",
        )
        .all()
    )

    paid_subscription_rows = (
        db.query(SubscriptionPaymentHistory)
        .join(Subscription, Subscription.id == SubscriptionPaymentHistory.subscription_id)
        .filter(
            Subscription.user_id == user_id,
            Subscription.region == region,
            SubscriptionPaymentHistory.month == month,
            SubscriptionPaymentHistory.year == year,
            SubscriptionPaymentHistory.status == "paid",
        )
        .all()
    )

    total_due_count = len(loans) + len(subscriptions)
    paid_count = len(paid_loan_rows) + len(paid_subscription_rows)
    remaining_count = max(total_due_count - paid_count, 0)

    total_loan_amount_due = float(sum(float(loan.emi_amount) for loan in loans))
    total_subscription_amount_due = float(sum(float(item.monthly_cost) for item in subscriptions))
    total_due_amount = total_loan_amount_due + total_subscription_amount_due

    paid_loan_amount = float(
        db.query(func.coalesce(func.sum(Loan.emi_amount), 0.0))
        .join(LoanEmiHistory, Loan.id == LoanEmiHistory.loan_id)
        .filter(
            Loan.user_id == user_id,
            Loan.region == region,
            LoanEmiHistory.month == month,
            LoanEmiHistory.year == year,
            LoanEmiHistory.status == "completed",
        )
        .scalar()
        or 0.0
    )

    paid_subscription_amount = float(
        db.query(func.coalesce(func.sum(Subscription.monthly_cost), 0.0))
        .join(SubscriptionPaymentHistory, Subscription.id == SubscriptionPaymentHistory.subscription_id)
        .filter(
            Subscription.user_id == user_id,
            Subscription.region == region,
            SubscriptionPaymentHistory.month == month,
            SubscriptionPaymentHistory.year == year,
            SubscriptionPaymentHistory.status == "paid",
        )
        .scalar()
        or 0.0
    )

    total_paid_amount = paid_loan_amount + paid_subscription_amount
    total_remaining_amount = max(total_due_amount - total_paid_amount, 0.0)

    return {
        "region": region,
        "month": ref_date.strftime("%B %Y"),
        "total_emis_paid_count": paid_count,
        "total_emis_remaining_count": remaining_count,
        "total_emi_amount_paid": total_paid_amount,
        "total_emi_amount_remaining": total_remaining_amount,
        "all_completed": total_due_count > 0 and paid_count == total_due_count and abs(total_remaining_amount) < 0.0001,
    }


def region_breakdown(db: Session, user_id: int, region: RegionEnum) -> dict:
    income = income_total(db, user_id, region)
    expenses = expense_total(db, user_id, region)
    loans = loan_outstanding_total(db, user_id, region)
    debts = debt_outstanding_total(db, user_id, region)
    investments = investments_current_total(db, user_id, region)
    gold = gold_current_total(db, user_id, region)

    net_worth = income - expenses - loans - debts + investments + gold
    return {
        "region": region,
        "income": income,
        "expenses": expenses,
        "loan_outstanding": loans,
        "debt_outstanding": debts,
        "investments_value": investments,
        "gold_value": gold,
        "net_worth": net_worth,
    }


@router.get("/summary")
def total_net_worth_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    india = region_breakdown(db, user.id, RegionEnum.india)
    uae = region_breakdown(db, user.id, RegionEnum.uae)

    total = india["net_worth"] + uae["net_worth"]

    today = date.today()
    this_month = current_month_net_worth(db, user.id, RegionEnum.india, today) + current_month_net_worth(db, user.id, RegionEnum.uae, today)
    india_monthly_emi = monthly_emi_summary(db, user.id, RegionEnum.india, today)
    uae_monthly_emi = monthly_emi_summary(db, user.id, RegionEnum.uae, today)

    prev_month_ref = date(today.year - 1, 12, 1) if today.month == 1 else date(today.year, today.month - 1, 1)
    prev_month = current_month_net_worth(db, user.id, RegionEnum.india, prev_month_ref) + current_month_net_worth(
        db,
        user.id,
        RegionEnum.uae,
        prev_month_ref,
    )

    return {
        "india": india,
        "uae": uae,
        "monthly_emi_summary": {
            "india": india_monthly_emi,
            "uae": uae_monthly_emi,
        },
        "total_net_worth": total,
        "monthly_change": this_month - prev_month,
        "breakdown_chart": [
            {"name": "India", "value": india["net_worth"]},
            {"name": "UAE", "value": uae["net_worth"]},
        ],
    }
