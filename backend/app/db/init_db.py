from sqlalchemy import inspect, text

from app.db.session import engine
from app.models.base import Base
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
    UserSettings,
)
from app.models.user import User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    loan_columns = [column["name"] for column in inspector.get_columns("loans")]

    with engine.begin() as connection:
        if "emi_date" not in loan_columns:
            connection.execute(text("ALTER TABLE loans ADD COLUMN emi_date INTEGER DEFAULT 1 NOT NULL"))
