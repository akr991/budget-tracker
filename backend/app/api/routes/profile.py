from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.finance import UserSettings
from app.models.user import User
from app.schemas.common import UserSettingsRead, UserSettingsUpdate
from app.schemas.profile import ProfileResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(user: User = Depends(get_current_user)):
    """Get current user profile"""
    return user


@router.get("/settings", response_model=UserSettingsRead)
def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user settings"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return UserSettingsRead(
        dark_mode=settings.dark_mode,
        monthly_summary_notifications=settings.monthly_summary_notifications,
    )


@router.put("/settings", response_model=UserSettingsRead)
def update_settings(
    payload: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.add(settings)

    if payload.dark_mode is not None:
        settings.dark_mode = payload.dark_mode
    if payload.monthly_summary_notifications is not None:
        settings.monthly_summary_notifications = payload.monthly_summary_notifications

    db.commit()
    db.refresh(settings)
    return UserSettingsRead(
        dark_mode=settings.dark_mode,
        monthly_summary_notifications=settings.monthly_summary_notifications,
    )
