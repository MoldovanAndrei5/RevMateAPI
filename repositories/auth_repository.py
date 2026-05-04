from sqlalchemy.orm import Session
from models.user import User

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user_id: int, hashed_password: str) -> User | None:
        db_query = self.db.query(User).filter(User.user_id == user_id)
        if not db_query.first():
            return None
        db_query.update({"hashed_password": hashed_password})
        self.db.commit()
        return db_query.first()