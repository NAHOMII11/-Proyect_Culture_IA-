from app.infrastructure.database import SessionLocal
from app.infrastructure.user_repository import UserRepository
from app.domain.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_default_user():
    db = SessionLocal()
    try:
        user_repo = UserRepository()

        default_email = "admin@culturalroute.ai"

        user_exists = user_repo.exists_by_email(db, default_email)
        if user_exists:
            return

        default_user = User(
            full_name="Administrador",
            email=default_email,
            password_hash=pwd_context.hash("Admin123*"),
            role="admin",
            is_active=True
        )

        user_repo.create(db, default_user)

    finally:
        db.close()