from fastapi import HTTPException
from models.user import User
from repositories.interfaces.i_auth_repository import IAuthRepository
from schemas.auth_schema import AuthResponse
from schemas.response_schema import MessageResponse
from schemas.user_schema import UserCreate, UserLogin, UserUpdate
from services.interfaces.i_auth_service import IAuthService
from utils.auth import verify_password, create_access_token, hash_password

class AuthService(IAuthService):
    def __init__(self, repo: IAuthRepository):
        self.repo = repo

    def login(self, data: UserLogin) -> AuthResponse:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        token = create_access_token({"user_id": user.user_id})
        return AuthResponse(access_token=token, user_id=user.user_id)

    def register(self, data: UserCreate) -> MessageResponse:
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
        return MessageResponse(message="User created successfully")

    def reset_password(self, user_id: int, data: UserUpdate) -> MessageResponse:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self.repo.update_password(user_id, hash_password(data.password))
        return MessageResponse(message="Password updated successfully")
