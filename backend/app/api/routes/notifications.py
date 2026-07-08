from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import RegionEnum
from app.models.finance import UserSettings
from app.models.user import User
from app.services.finance_calculations import expense_total, income_total

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/monthly-summary")
def monthly_summary_notification(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if settings and not settings.monthly_summary_notifications:
        return {"enabled": False, "message": "Monthly summary notifications are disabled"}

    india_income = income_total(db, user.id, RegionEnum.india)
    india_expense = expense_total(db, user.id, RegionEnum.india)
    uae_income = income_total(db, user.id, RegionEnum.uae)
    uae_expense = expense_total(db, user.id, RegionEnum.uae)

    month_label = date.today().strftime("%B %Y")
    return {
      "enabled": True,
      "month": month_label,
      "message": f"{month_label}: India net cash {india_income - india_expense:.2f}, UAE net cash {uae_income - uae_expense:.2f}",
      "india": {"income": india_income, "expenses": india_expense, "net_cash": india_income - india_expense},
      "uae": {"income": uae_income, "expenses": uae_expense, "net_cash": uae_income - uae_expense}
    }
