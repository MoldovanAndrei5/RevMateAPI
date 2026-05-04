from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.user import User
from repositories.auth_repository import AuthRepository
from schemas.user_schema import UserCreate, UserLogin, UserUpdate
from utils.auth import verify_password, create_access_token, hash_password

class AuthService:
    def __init__(self, db: Session):
        self.repo = AuthRepository(db)

    def login(self, data: UserLogin) -> dict:
        user = self.repo.get_by_email(data.email)
        if not user:
            raise HTTPException(status_code=404, detail="There is no user with this email")
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=404, detail="Incorrect password")
        token = create_access_token({"user_id": user.user_id})
        return {
            "access_token": token,
            "user_id": user.user_id
        }

    def register(self, data: UserCreate) -> dict:
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        new_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password)
        )
        self.repo.create(new_user)
        return {"message": "User created successfully"}

    def reset_password(self, user_id: int, data: UserUpdate) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        updated = self.repo.update_password(user_id, hash_password(data.password))
        return updated