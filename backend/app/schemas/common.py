from datetime import date

from pydantic import BaseModel

from app.models.enums import GoldUnitEnum, IncomeCategoryEnum, InvestmentTypeEnum, RegionEnum


class BaseRegionModel(BaseModel):
    region: RegionEnum


class IncomeCreate(BaseModel):
    category: IncomeCategoryEnum
    amount: float
    entry_date: date
    notes: str | None = None


class IncomeRead(IncomeCreate):
    id: int

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    category: str
    amount: float
    entry_date: date
    notes: str | None = None


class ExpenseRead(ExpenseCreate):
    id: int

    class Config:
        from_attributes = True


class LoanCreate(BaseModel):
    loan_name: str
    emi_amount: float
    emi_date: int
    remaining_months: int
    interest_rate: float | None = None
    start_date: date | None = None


class LoanRead(LoanCreate):
    id: int
    outstanding_amount: float


class LoanEmiHistoryItem(BaseModel):
    month: int
    year: int
    status: str
    completed_at: str | None = None


class LoanDetailsResponse(BaseModel):
    id: int
    loan_name: str
    emi_amount: float
    emi_date: int
    remaining_months: int
    outstanding_amount: float
    interest_rate: float | None = None
    mark_emi_enabled: bool
    current_month_status: str
    next_due_month: int
    next_due_year: int
    next_due_month_name: str
    next_action_label: str
    emi_history: list[LoanEmiHistoryItem]


class EmiMarkResponse(BaseModel):
    loan_id: int
    remaining_months: int
    outstanding_amount: float
    month: int
    year: int
    month_name: str
    status: str


class SubscriptionCreate(BaseModel):
    subscription_name: str
    monthly_cost: float
    billing_date: int
    category: str
    notes: str | None = None


class SubscriptionRead(SubscriptionCreate):
    id: int

    class Config:
        from_attributes = True


class SubscriptionPaymentHistoryItem(BaseModel):
    month: int
    year: int
    status: str
    paid_at: str | None = None


class SubscriptionDetailsResponse(BaseModel):
    id: int
    subscription_name: str
    monthly_cost: float
    billing_date: int
    category: str
    notes: str | None = None
    mark_paid_enabled: bool
    current_month_status: str
    history: list[SubscriptionPaymentHistoryItem]


class SubscriptionMarkPaidResponse(BaseModel):
    subscription_id: int
    month: int
    year: int
    status: str


class DebtCreate(BaseModel):
    lender_name: str
    amount: float
    due_date: date
    notes: str | None = None


class DebtRepaymentCreate(BaseModel):
    amount: float
    payment_date: date


class DebtRead(DebtCreate):
    id: int
    total_repaid: float
    outstanding_amount: float


class InvestmentCreate(BaseModel):
    name: str
    investment_type: InvestmentTypeEnum
    invested_value: float
    current_value: float
    entry_date: date


class InvestmentRead(InvestmentCreate):
    id: int
    profit_or_loss: float


class GoldCreate(BaseModel):
    quantity: float
    unit: GoldUnitEnum
    price_per_gram: float
    entry_date: date


class GoldRead(GoldCreate):
    id: int
    grams_total: float
    current_value: float


class SummaryItem(BaseModel):
    month: str
    value: float


class UserSettingsRead(BaseModel):
    dark_mode: bool
    monthly_summary_notifications: bool


class UserSettingsUpdate(BaseModel):
    dark_mode: bool | None = None
    monthly_summary_notifications: bool | None = None
