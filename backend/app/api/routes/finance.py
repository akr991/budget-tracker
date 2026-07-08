import calendar
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import GoldUnitEnum, RegionEnum
from app.models.finance import (
    Debt,
    DebtRepayment,
    ExpenseEntry,
    GoldHolding,
    IncomeEntry,
    Investment,
    Loan,
    LoanEmiHistory,
    Subscription,
    SubscriptionPaymentHistory,
)
from app.models.user import User
from app.schemas.common import (
    DebtCreate,
    DebtRead,
    DebtRepaymentCreate,
    EmiMarkResponse,
    ExpenseCreate,
    ExpenseRead,
    GoldCreate,
    GoldRead,
    IncomeCreate,
    IncomeRead,
    InvestmentCreate,
    InvestmentRead,
    LoanCreate,
    LoanDetailsResponse,
    LoanEmiHistoryItem,
    LoanRead,
    SubscriptionCreate,
    SubscriptionDetailsResponse,
    SubscriptionMarkPaidResponse,
    SubscriptionPaymentHistoryItem,
    SubscriptionRead,
    SummaryItem,
)
from app.services.gold_price import fetch_live_gold_price_inr_per_gram

router = APIRouter(prefix="/regions", tags=["finance"])


def _month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def _add_months(value: date, months: int) -> date:
    month_index = (value.month - 1) + months
    year = value.year + (month_index // 12)
    month = (month_index % 12) + 1
    return date(year, month, 1)


def _loan_anchor_month(loan: Loan) -> date:
    if loan.start_date:
        return date(loan.start_date.year, loan.start_date.month, 1)
    created = loan.created_at.date() if loan.created_at else date.today()
    return date(created.year, created.month, 1)


def _next_due_reference(loan: Loan, history: list[LoanEmiHistory]) -> date:
    completed_count = sum(1 for item in history if item.status == "completed")
    anchor = _loan_anchor_month(loan)
    sequential_due = _add_months(anchor, completed_count)
    current_month = _month_start(datetime.now(timezone.utc).year, datetime.now(timezone.utc).month)
    return current_month if current_month > sequential_due else sequential_due


def _loan_read(loan: Loan) -> LoanRead:
    return LoanRead(
        id=loan.id,
        loan_name=loan.loan_name,
        emi_amount=float(loan.emi_amount),
        emi_date=loan.emi_date,
        remaining_months=loan.remaining_months,
        interest_rate=loan.interest_rate,
        start_date=loan.start_date,
        outstanding_amount=float(loan.emi_amount) * loan.remaining_months,
    )


def _history_item(item: LoanEmiHistory) -> LoanEmiHistoryItem:
    completed_at = item.completed_at.isoformat() if item.completed_at else None
    return LoanEmiHistoryItem(month=item.month, year=item.year, status=item.status, completed_at=completed_at)


def _loan_details_response(loan: Loan, history: list[LoanEmiHistory]) -> LoanDetailsResponse:
    due_ref = _next_due_reference(loan, history)
    current_month_completed = any(record.month == due_ref.month and record.year == due_ref.year and record.status == "completed" for record in history)
    is_due_or_pending = loan.remaining_months > 0 and not current_month_completed
    month_name = calendar.month_name[due_ref.month]

    timeline: list[LoanEmiHistoryItem] = [_history_item(item) for item in history]
    if loan.remaining_months > 0 and not current_month_completed:
        timeline.insert(0, LoanEmiHistoryItem(month=due_ref.month, year=due_ref.year, status="pending", completed_at=None))

    return LoanDetailsResponse(
        id=loan.id,
        loan_name=loan.loan_name,
        emi_amount=float(loan.emi_amount),
        emi_date=loan.emi_date,
        remaining_months=loan.remaining_months,
        outstanding_amount=float(loan.emi_amount) * loan.remaining_months,
        interest_rate=loan.interest_rate,
        mark_emi_enabled=is_due_or_pending,
        current_month_status="completed" if current_month_completed else "pending",
        next_due_month=due_ref.month,
        next_due_year=due_ref.year,
        next_due_month_name=month_name,
        next_action_label=f"Mark EMI for {month_name} as Completed",
        emi_history=timeline,
    )


def _debt_read(debt: Debt) -> DebtRead:
    total_repaid = float(sum(float(item.amount) for item in debt.repayments))
    outstanding = max(float(debt.amount) - total_repaid, 0.0)
    return DebtRead(
        id=debt.id,
        lender_name=debt.lender_name,
        amount=float(debt.amount),
        due_date=debt.due_date,
        notes=debt.notes,
        total_repaid=total_repaid,
        outstanding_amount=outstanding,
    )


def _gold_read(holding: GoldHolding) -> GoldRead:
    grams_total = holding.quantity if holding.unit == GoldUnitEnum.grams else holding.quantity * 8
    current_value = grams_total * float(holding.price_per_gram)
    return GoldRead(
        id=holding.id,
        quantity=float(holding.quantity),
        unit=holding.unit,
        price_per_gram=float(holding.price_per_gram),
        entry_date=holding.entry_date,
        grams_total=float(grams_total),
        current_value=float(current_value),
    )


def _subscription_read(item: Subscription) -> SubscriptionRead:
    return SubscriptionRead(
        id=item.id,
        subscription_name=item.subscription_name,
        monthly_cost=float(item.monthly_cost),
        billing_date=item.billing_date,
        category=item.category,
        notes=item.notes,
    )


def _subscription_history_item(item: SubscriptionPaymentHistory) -> SubscriptionPaymentHistoryItem:
    return SubscriptionPaymentHistoryItem(
        month=item.month,
        year=item.year,
        status=item.status,
        paid_at=item.paid_at.isoformat() if item.paid_at else None,
    )


def _subscription_details_response(subscription: Subscription, history: list[SubscriptionPaymentHistory]) -> SubscriptionDetailsResponse:
    now = datetime.now(timezone.utc)
    current_month_paid = any(item.month == now.month and item.year == now.year and item.status == "paid" for item in history)
    due_or_pending = now.day >= subscription.billing_date and not current_month_paid

    timeline: list[SubscriptionPaymentHistoryItem] = [_subscription_history_item(item) for item in history]
    if due_or_pending:
        timeline.insert(0, SubscriptionPaymentHistoryItem(month=now.month, year=now.year, status="pending", paid_at=None))

    return SubscriptionDetailsResponse(
        id=subscription.id,
        subscription_name=subscription.subscription_name,
        monthly_cost=float(subscription.monthly_cost),
        billing_date=subscription.billing_date,
        category=subscription.category,
        notes=subscription.notes,
        mark_paid_enabled=due_or_pending,
        current_month_status="paid" if current_month_paid else "pending",
        history=timeline,
    )


@router.get("/{region}/incomes", response_model=list[IncomeRead])
def list_incomes(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = (
        db.query(IncomeEntry)
        .filter(IncomeEntry.user_id == user.id, IncomeEntry.region == region)
        .order_by(IncomeEntry.entry_date.desc())
        .all()
    )
    return [IncomeRead.model_validate(i) for i in items]


@router.post("/{region}/incomes", response_model=IncomeRead)
def create_income(region: RegionEnum, payload: IncomeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = IncomeEntry(user_id=user.id, region=region, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return IncomeRead.model_validate(item)


@router.put("/{region}/incomes/{income_id}", response_model=IncomeRead)
def update_income(region: RegionEnum, income_id: int, payload: IncomeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(IncomeEntry)
        .filter(IncomeEntry.id == income_id, IncomeEntry.user_id == user.id, IncomeEntry.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Income not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return IncomeRead.model_validate(item)


@router.delete("/{region}/incomes/{income_id}")
def delete_income(region: RegionEnum, income_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(IncomeEntry)
        .filter(IncomeEntry.id == income_id, IncomeEntry.user_id == user.id, IncomeEntry.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Income not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.get("/{region}/incomes/summary/monthly", response_model=list[SummaryItem])
def monthly_income_summary(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(
            extract("year", IncomeEntry.entry_date).label("year"),
            extract("month", IncomeEntry.entry_date).label("month"),
            func.coalesce(func.sum(IncomeEntry.amount), 0.0).label("total"),
        )
        .filter(IncomeEntry.user_id == user.id, IncomeEntry.region == region)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    return [SummaryItem(month=f"{int(row.year)}-{int(row.month):02d}", value=float(row.total)) for row in rows]


@router.get("/{region}/incomes/summary/yearly", response_model=list[SummaryItem])
def yearly_income_summary(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(
            extract("year", IncomeEntry.entry_date).label("year"),
            func.coalesce(func.sum(IncomeEntry.amount), 0.0).label("total"),
        )
        .filter(IncomeEntry.user_id == user.id, IncomeEntry.region == region)
        .group_by("year")
        .order_by("year")
        .all()
    )
    return [SummaryItem(month=str(int(row.year)), value=float(row.total)) for row in rows]


@router.get("/{region}/expenses", response_model=list[ExpenseRead])
def list_expenses(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = (
        db.query(ExpenseEntry)
        .filter(ExpenseEntry.user_id == user.id, ExpenseEntry.region == region)
        .order_by(ExpenseEntry.entry_date.desc())
        .all()
    )
    return [ExpenseRead.model_validate(i) for i in items]


@router.post("/{region}/expenses", response_model=ExpenseRead)
def create_expense(region: RegionEnum, payload: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = ExpenseEntry(user_id=user.id, region=region, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return ExpenseRead.model_validate(item)


@router.delete("/{region}/expenses/{expense_id}")
def delete_expense(region: RegionEnum, expense_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(ExpenseEntry)
        .filter(ExpenseEntry.id == expense_id, ExpenseEntry.user_id == user.id, ExpenseEntry.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.get("/{region}/loans", response_model=list[LoanRead])
def list_loans(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Loan).filter(Loan.user_id == user.id, Loan.region == region).all()
    return [_loan_read(loan) for loan in rows]


@router.post("/{region}/loans", response_model=LoanRead)
def create_loan(region: RegionEnum, payload: LoanCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.emi_date < 1 or payload.emi_date > 31:
        raise HTTPException(status_code=400, detail="EMI date must be between 1 and 31")

    loan = Loan(user_id=user.id, region=region, **payload.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return _loan_read(loan)


@router.put("/{region}/loans/{loan_id}", response_model=LoanRead)
def update_loan(region: RegionEnum, loan_id: int, payload: LoanCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.emi_date < 1 or payload.emi_date > 31:
        raise HTTPException(status_code=400, detail="EMI date must be between 1 and 31")

    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == user.id, Loan.region == region).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    for key, value in payload.model_dump().items():
        setattr(loan, key, value)
    db.commit()
    db.refresh(loan)
    return _loan_read(loan)


@router.get("/{region}/loans/{loan_id}/details", response_model=LoanDetailsResponse)
def loan_details(region: RegionEnum, loan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == user.id, Loan.region == region).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    history = (
        db.query(LoanEmiHistory)
        .filter(LoanEmiHistory.loan_id == loan.id)
        .order_by(LoanEmiHistory.year.desc(), LoanEmiHistory.month.desc(), LoanEmiHistory.id.desc())
        .all()
    )
    return _loan_details_response(loan, history)


@router.get("/{region}/loans/{loan_id}/emi-history", response_model=list[LoanEmiHistoryItem])
def loan_emi_history(region: RegionEnum, loan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == user.id, Loan.region == region).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    history = (
        db.query(LoanEmiHistory)
        .filter(LoanEmiHistory.loan_id == loan.id)
        .order_by(LoanEmiHistory.year.desc(), LoanEmiHistory.month.desc(), LoanEmiHistory.id.desc())
        .all()
    )
    return [_history_item(item) for item in history]


@router.post("/{region}/loans/{loan_id}/mark-emi-completed", response_model=EmiMarkResponse)
def mark_emi_completed(region: RegionEnum, loan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == user.id, Loan.region == region).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.remaining_months <= 0:
        raise HTTPException(status_code=400, detail="Loan is already completed")

    now = datetime.now(timezone.utc)
    history_rows = (
        db.query(LoanEmiHistory)
        .filter(LoanEmiHistory.loan_id == loan.id)
        .order_by(LoanEmiHistory.year.desc(), LoanEmiHistory.month.desc(), LoanEmiHistory.id.desc())
        .all()
    )
    due_ref = _next_due_reference(loan, history_rows)
    duplicate = (
        db.query(LoanEmiHistory)
        .filter(
            LoanEmiHistory.loan_id == loan.id,
            LoanEmiHistory.month == due_ref.month,
            LoanEmiHistory.year == due_ref.year,
            LoanEmiHistory.status == "completed",
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="EMI already marked completed for this month")

    history = LoanEmiHistory(
        loan_id=loan.id,
        month=due_ref.month,
        year=due_ref.year,
        status="completed",
        completed_at=now,
    )
    db.add(history)

    loan.remaining_months = max(loan.remaining_months - 1, 0)
    db.commit()
    db.refresh(loan)

    return EmiMarkResponse(
        loan_id=loan.id,
        remaining_months=loan.remaining_months,
        outstanding_amount=float(loan.emi_amount) * loan.remaining_months,
        month=due_ref.month,
        year=due_ref.year,
        month_name=calendar.month_name[due_ref.month],
        status="completed",
    )


@router.get("/{region}/loans/summary")
def loan_summary(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Loan).filter(Loan.user_id == user.id, Loan.region == region).all()
    total_outstanding = float(sum(float(row.emi_amount) * row.remaining_months for row in rows))
    return {"loan_count": len(rows), "total_outstanding": total_outstanding}


@router.get("/{region}/loans/alerts")
def loan_alerts(region: RegionEnum, threshold_months: int = 3, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(Loan)
        .filter(
            Loan.user_id == user.id,
            Loan.region == region,
            Loan.remaining_months <= threshold_months,
        )
        .all()
    )
    return [
        {
            "loan_id": row.id,
            "loan_name": row.loan_name,
            "remaining_months": row.remaining_months,
            "message": f"Loan {row.loan_name} is close to completion",
        }
        for row in rows
    ]


@router.delete("/{region}/loans/{loan_id}")
def delete_loan(region: RegionEnum, loan_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.user_id == user.id, Loan.region == region).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    db.delete(loan)
    db.commit()
    return {"deleted": True}


@router.get("/{region}/subscriptions", response_model=list[SubscriptionRead])
def list_subscriptions(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.region == region)
        .order_by(Subscription.created_at.desc())
        .all()
    )
    return [_subscription_read(row) for row in rows]


@router.post("/{region}/subscriptions", response_model=SubscriptionRead)
def create_subscription(region: RegionEnum, payload: SubscriptionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.billing_date < 1 or payload.billing_date > 31:
        raise HTTPException(status_code=400, detail="Billing date must be between 1 and 31")

    item = Subscription(user_id=user.id, region=region, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _subscription_read(item)


@router.put("/{region}/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def update_subscription(region: RegionEnum, subscription_id: int, payload: SubscriptionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.billing_date < 1 or payload.billing_date > 31:
        raise HTTPException(status_code=400, detail="Billing date must be between 1 and 31")

    item = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id, Subscription.user_id == user.id, Subscription.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")

    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _subscription_read(item)


@router.delete("/{region}/subscriptions/{subscription_id}")
def delete_subscription(region: RegionEnum, subscription_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id, Subscription.user_id == user.id, Subscription.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.get("/{region}/subscriptions/{subscription_id}/details", response_model=SubscriptionDetailsResponse)
def subscription_details(region: RegionEnum, subscription_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id, Subscription.user_id == user.id, Subscription.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")

    history = (
        db.query(SubscriptionPaymentHistory)
        .filter(SubscriptionPaymentHistory.subscription_id == item.id)
        .order_by(SubscriptionPaymentHistory.year.desc(), SubscriptionPaymentHistory.month.desc(), SubscriptionPaymentHistory.id.desc())
        .all()
    )
    return _subscription_details_response(item, history)


@router.get("/{region}/subscriptions/{subscription_id}/history", response_model=list[SubscriptionPaymentHistoryItem])
def subscription_history(region: RegionEnum, subscription_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id, Subscription.user_id == user.id, Subscription.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")

    rows = (
        db.query(SubscriptionPaymentHistory)
        .filter(SubscriptionPaymentHistory.subscription_id == item.id)
        .order_by(SubscriptionPaymentHistory.year.desc(), SubscriptionPaymentHistory.month.desc(), SubscriptionPaymentHistory.id.desc())
        .all()
    )
    return [_subscription_history_item(row) for row in rows]


@router.post("/{region}/subscriptions/{subscription_id}/mark-paid", response_model=SubscriptionMarkPaidResponse)
def mark_subscription_paid(region: RegionEnum, subscription_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id, Subscription.user_id == user.id, Subscription.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")

    now = datetime.now(timezone.utc)
    duplicate = (
        db.query(SubscriptionPaymentHistory)
        .filter(
            SubscriptionPaymentHistory.subscription_id == item.id,
            SubscriptionPaymentHistory.month == now.month,
            SubscriptionPaymentHistory.year == now.year,
            SubscriptionPaymentHistory.status == "paid",
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="Subscription already marked paid for this month")

    payment = SubscriptionPaymentHistory(
        subscription_id=item.id,
        month=now.month,
        year=now.year,
        status="paid",
        paid_at=now,
    )
    db.add(payment)
    db.commit()

    return SubscriptionMarkPaidResponse(subscription_id=item.id, month=now.month, year=now.year, status="paid")


@router.get("/{region}/debts", response_model=list[DebtRead])
def list_debts(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    debts = db.query(Debt).filter(Debt.user_id == user.id, Debt.region == region).all()
    return [_debt_read(debt) for debt in debts]


@router.post("/{region}/debts", response_model=DebtRead)
def create_debt(region: RegionEnum, payload: DebtCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    debt = Debt(user_id=user.id, region=region, **payload.model_dump())
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return _debt_read(debt)


@router.post("/{region}/debts/{debt_id}/repayments")
def add_debt_repayment(region: RegionEnum, debt_id: int, payload: DebtRepaymentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    debt = db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == user.id, Debt.region == region).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    repayment = DebtRepayment(debt_id=debt.id, **payload.model_dump())
    db.add(repayment)
    db.commit()
    return {"created": True}


@router.get("/{region}/debts/summary")
def debt_summary(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    debts = db.query(Debt).filter(Debt.user_id == user.id, Debt.region == region).all()
    outstanding = 0.0
    for debt in debts:
        repaid = sum(float(item.amount) for item in debt.repayments)
        outstanding += max(float(debt.amount) - repaid, 0.0)
    return {"debt_count": len(debts), "outstanding_total": float(outstanding)}


@router.delete("/{region}/debts/{debt_id}")
def delete_debt(region: RegionEnum, debt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    debt = db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == user.id, Debt.region == region).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    db.delete(debt)
    db.commit()
    return {"deleted": True}


@router.get("/{region}/investments", response_model=list[InvestmentRead])
def list_investments(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(Investment).filter(Investment.user_id == user.id, Investment.region == region).all()
    return [
        InvestmentRead(
            id=item.id,
            name=item.name,
            investment_type=item.investment_type,
            invested_value=float(item.invested_value),
            current_value=float(item.current_value),
            entry_date=item.entry_date,
            profit_or_loss=float(item.current_value) - float(item.invested_value),
        )
        for item in items
    ]


@router.post("/{region}/investments", response_model=InvestmentRead)
def create_investment(region: RegionEnum, payload: InvestmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = Investment(user_id=user.id, region=region, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return InvestmentRead(
        id=item.id,
        name=item.name,
        investment_type=item.investment_type,
        invested_value=float(item.invested_value),
        current_value=float(item.current_value),
        entry_date=item.entry_date,
        profit_or_loss=float(item.current_value) - float(item.invested_value),
    )


@router.get("/{region}/investments/trends", response_model=list[SummaryItem])
def investment_trends(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(
            extract("year", Investment.entry_date).label("year"),
            extract("month", Investment.entry_date).label("month"),
            func.coalesce(func.sum(Investment.current_value), 0.0).label("total"),
        )
        .filter(Investment.user_id == user.id, Investment.region == region)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    return [SummaryItem(month=f"{int(row.year)}-{int(row.month):02d}", value=float(row.total)) for row in rows]


@router.delete("/{region}/investments/{investment_id}")
def delete_investment(region: RegionEnum, investment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = (
        db.query(Investment)
        .filter(Investment.id == investment_id, Investment.user_id == user.id, Investment.region == region)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Investment not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.get("/{region}/gold", response_model=list[GoldRead])
def list_gold(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(GoldHolding).filter(GoldHolding.user_id == user.id, GoldHolding.region == region).all()
    return [_gold_read(item) for item in items]


@router.post("/{region}/gold", response_model=GoldRead)
def create_gold(region: RegionEnum, payload: GoldCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = GoldHolding(user_id=user.id, region=region, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _gold_read(item)


@router.get("/{region}/gold/live-price")
async def live_gold_price(region: RegionEnum):
    price = await fetch_live_gold_price_inr_per_gram()
    return {"region": region, "price_per_gram": price, "source": "configured-api" if price else "not-configured"}


@router.get("/{region}/gold/summary")
def gold_summary(region: RegionEnum, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(GoldHolding).filter(GoldHolding.user_id == user.id, GoldHolding.region == region).all()
    grams = 0.0
    value = 0.0
    for item in items:
        item_grams = item.quantity if item.unit == GoldUnitEnum.grams else item.quantity * 8
        grams += item_grams
        value += item_grams * float(item.price_per_gram)
    return {"holdings": len(items), "grams": float(grams), "current_value": float(value)}


@router.delete("/{region}/gold/{gold_id}")
def delete_gold(region: RegionEnum, gold_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(GoldHolding).filter(GoldHolding.id == gold_id, GoldHolding.user_id == user.id, GoldHolding.region == region).first()
    if not item:
        raise HTTPException(status_code=404, detail="Gold entry not found")
    db.delete(item)
    db.commit()
    return {"deleted": True}


@router.get("/{region}/monthly-summary")
def monthly_summary(region: RegionEnum, month: int | None = None, year: int | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year

    income = db.query(func.coalesce(func.sum(IncomeEntry.amount), 0.0)).filter(
        IncomeEntry.user_id == user.id,
        IncomeEntry.region == region,
        extract("month", IncomeEntry.entry_date) == target_month,
        extract("year", IncomeEntry.entry_date) == target_year,
    ).scalar()

    expenses = db.query(func.coalesce(func.sum(ExpenseEntry.amount), 0.0)).filter(
        ExpenseEntry.user_id == user.id,
        ExpenseEntry.region == region,
        extract("month", ExpenseEntry.entry_date) == target_month,
        extract("year", ExpenseEntry.entry_date) == target_year,
    ).scalar()

    loans = db.query(func.coalesce(func.sum(Loan.emi_amount), 0.0)).filter(
        Loan.user_id == user.id,
        Loan.region == region,
    ).scalar()

    subscriptions = db.query(func.coalesce(func.sum(Subscription.monthly_cost), 0.0)).filter(
        Subscription.user_id == user.id,
        Subscription.region == region,
    ).scalar()

    return {
        "region": region,
        "month": f"{target_year}-{target_month:02d}",
        "income": float(income or 0.0),
        "expenses": float(expenses or 0.0),
        "monthly_emi_total": float(loans or 0.0),
        "monthly_subscription_total": float(subscriptions or 0.0),
        "net_cash_flow": float(income or 0.0)
        - float(expenses or 0.0)
        - float(loans or 0.0)
        - float(subscriptions or 0.0),
    }
