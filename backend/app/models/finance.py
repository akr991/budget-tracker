from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import GoldUnitEnum, IncomeCategoryEnum, InvestmentTypeEnum, RegionEnum


class IncomeEntry(Base):
    __tablename__ = "income_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), index=True)
    category: Mapped[IncomeCategoryEnum] = mapped_column(Enum(IncomeCategoryEnum), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExpenseEntry(Base):
    __tablename__ = "expense_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), index=True)
    loan_name: Mapped[str] = mapped_column(String(150), nullable=False)
    emi_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    emi_date: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    remaining_months: Mapped[int] = mapped_column(Integer, nullable=False)
    interest_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    emi_history = relationship("LoanEmiHistory", back_populates="loan", cascade="all,delete")


class LoanEmiHistory(Base):
    __tablename__ = "loan_emi_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id", ondelete="CASCADE"), index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    loan = relationship("Loan", back_populates="emi_history")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), index=True)
    subscription_name: Mapped[str] = mapped_column(String(160), nullable=False)
    monthly_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    billing_date: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    payment_history = relationship("SubscriptionPaymentHistory", back_populates="subscription", cascade="all,delete")


class SubscriptionPaymentHistory(Base):
    __tablename__ = "subscription_payment_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id", ondelete="CASCADE"), index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="paid")
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subscription = relationship("Subscription", back_populates="payment_history")


class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), index=True)
    lender_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    repayments = relationship("DebtRepayment", back_populates="debt", cascade="all,delete")


class DebtRepayment(Base):
    __tablename__ = "debt_repayments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    debt_id: Mapped[int] = mapped_column(ForeignKey("debts.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)

    debt = relationship("Debt", back_populates="repayments")


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    investment_type: Mapped[InvestmentTypeEnum] = mapped_column(Enum(InvestmentTypeEnum), nullable=False)
    invested_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    current_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GoldHolding(Base):
    __tablename__ = "gold_holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[RegionEnum] = mapped_column(Enum(RegionEnum), index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[GoldUnitEnum] = mapped_column(Enum(GoldUnitEnum), nullable=False)
    price_per_gram: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    dark_mode: Mapped[bool] = mapped_column(default=False)
    monthly_summary_notifications: Mapped[bool] = mapped_column(default=True)

    user = relationship("User", back_populates="settings")
