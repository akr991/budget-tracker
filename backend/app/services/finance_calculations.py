from datetime import date

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.enums import GoldUnitEnum, RegionEnum
from app.models.finance import Debt, DebtRepayment, ExpenseEntry, GoldHolding, IncomeEntry, Investment, Loan, Subscription


def loan_outstanding_total(db: Session, user_id: int, region: RegionEnum) -> float:
    rows = db.query(Loan).filter(Loan.user_id == user_id, Loan.region == region).all()
    return float(sum(float(row.emi_amount) * row.remaining_months for row in rows))


def debt_outstanding_total(db: Session, user_id: int, region: RegionEnum) -> float:
    debts = db.query(Debt).filter(Debt.user_id == user_id, Debt.region == region).all()
    total = 0.0
    for debt in debts:
        repaid = sum(float(item.amount) for item in debt.repayments)
        total += max(float(debt.amount) - repaid, 0.0)
    return total


def investments_current_total(db: Session, user_id: int, region: RegionEnum) -> float:
    value = db.query(func.coalesce(func.sum(Investment.current_value), 0.0)).filter(
        Investment.user_id == user_id,
        Investment.region == region,
    ).scalar()
    return float(value or 0.0)


def gold_current_total(db: Session, user_id: int, region: RegionEnum) -> float:
    holdings = db.query(GoldHolding).filter(GoldHolding.user_id == user_id, GoldHolding.region == region).all()
    total = 0.0
    for holding in holdings:
        grams = holding.quantity if holding.unit == GoldUnitEnum.grams else holding.quantity * 8
        total += grams * float(holding.price_per_gram)
    return float(total)


def income_total(db: Session, user_id: int, region: RegionEnum) -> float:
    value = db.query(func.coalesce(func.sum(IncomeEntry.amount), 0.0)).filter(
        IncomeEntry.user_id == user_id,
        IncomeEntry.region == region,
    ).scalar()
    return float(value or 0.0)


def expense_total(db: Session, user_id: int, region: RegionEnum) -> float:
    value = db.query(func.coalesce(func.sum(ExpenseEntry.amount), 0.0)).filter(
        ExpenseEntry.user_id == user_id,
        ExpenseEntry.region == region,
    ).scalar()

    subscription_value = db.query(func.coalesce(func.sum(Subscription.monthly_cost), 0.0)).filter(
        Subscription.user_id == user_id,
        Subscription.region == region,
    ).scalar()
    return float(value or 0.0) + float(subscription_value or 0.0)


def monthly_income_series(db: Session, user_id: int, region: RegionEnum):
    rows = (
        db.query(
            extract("year", IncomeEntry.entry_date).label("year"),
            extract("month", IncomeEntry.entry_date).label("month"),
            func.coalesce(func.sum(IncomeEntry.amount), 0.0).label("total"),
        )
        .filter(IncomeEntry.user_id == user_id, IncomeEntry.region == region)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    return [{"month": f"{int(r.year)}-{int(r.month):02d}", "value": float(r.total)} for r in rows]


def current_month_net_worth(db: Session, user_id: int, region: RegionEnum, ref_date: date) -> float:
    year = ref_date.year
    month = ref_date.month

    income = db.query(func.coalesce(func.sum(IncomeEntry.amount), 0.0)).filter(
        IncomeEntry.user_id == user_id,
        IncomeEntry.region == region,
        extract("year", IncomeEntry.entry_date) == year,
        extract("month", IncomeEntry.entry_date) == month,
    ).scalar()

    expenses = db.query(func.coalesce(func.sum(ExpenseEntry.amount), 0.0)).filter(
        ExpenseEntry.user_id == user_id,
        ExpenseEntry.region == region,
        extract("year", ExpenseEntry.entry_date) == year,
        extract("month", ExpenseEntry.entry_date) == month,
    ).scalar()

    subscription_monthly = db.query(func.coalesce(func.sum(Subscription.monthly_cost), 0.0)).filter(
        Subscription.user_id == user_id,
        Subscription.region == region,
    ).scalar()

    return float(income or 0.0) - float(expenses or 0.0) - float(subscription_monthly or 0.0)
