import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from models.otp_code import OtpCode
from models.user import User
from repositories.interfaces.i_auth_repository import IAuthRepository
from repositories.interfaces.i_otp_repository import IOtpRepository
from schemas.auth_schema import AuthResponse
from schemas.response_schema import MessageResponse
from schemas.user_schema import UserCreate, UserLogin, UserUpdate
from services.interfaces.i_auth_service import IAuthService
from utils.auth import verify_password, create_access_token, hash_password
from utils.email import send_otp_email


class AuthService(IAuthService):
    def __init__(self, repo: IAuthRepository, otp_repo: IOtpRepository):
        self.repo = repo
        self.otp_repo = otp_repo

    def login(self, data: UserLogin) -> AuthResponse:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        token = create_access_token({"user_id": user.user_id})
        return AuthResponse(access_token=token, user_id=user.user_id)
    
    def send_otp(self, email: str) -> MessageResponse:
        existing = self.repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        otp_code = str(secrets.randbelow(900000) + 100000)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        otp = OtpCode(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        self.otp_repo.create_or_replace(otp)
        success = send_otp_email(email, otp_code)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send verification email")
        return MessageResponse(message="Verification email sent")

    def register(self, data: UserCreate) -> MessageResponse:
        otp = self.otp_repo.get_by_email(data.email)
        if not otp:
            raise HTTPException(status_code=404, detail="No verification code found for this email")
        if datetime.now(timezone.utc) > otp.expires_at:
            self.otp_repo.delete(otp)
            raise HTTPException(status_code=400, detail="Verification code expired")
        if otp.otp_code != data.otp_code:
            raise HTTPException(status_code=401, detail="Incorrect otp code")
        
        new_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password)
        )
        self.repo.create(new_user)
        self.otp_repo.delete(otp)
        return MessageResponse(message="User created successfully")

    def reset_password(self, user_id: int, data: UserUpdate) -> MessageResponse:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self.repo.update_password(user_id, hash_password(data.password))
        return MessageResponse(message="Password updated successfully")
