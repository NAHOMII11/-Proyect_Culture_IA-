from sqlalchemy.orm import Session
from app.domain.user import User

class UserRepository:

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id):
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def exists_by_email(self, db: Session, email: str) -> bool:
        return db.query(User).filter(User.email == email).first() is not None