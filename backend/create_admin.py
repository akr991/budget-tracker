from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.finance import UserSettings
from app.models.user import User


def main() -> None:
    email = "admin@budgettracker.com"
    full_name = "admin"
    password = "@run@162991!"

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash(password),
                is_active=True,
            )
            db.add(user)
            db.flush()
            db.add(UserSettings(user_id=user.id, dark_mode=False, monthly_summary_notifications=True))
            db.commit()
            print(f"CREATED:{email}")
        else:
            user.full_name = full_name
            user.hashed_password = get_password_hash(password)
            user.is_active = True
            settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
            if settings is None:
                db.add(UserSettings(user_id=user.id, dark_mode=False, monthly_summary_notifications=True))
            db.commit()
            print(f"UPDATED:{email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
