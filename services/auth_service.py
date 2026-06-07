from datetime import datetime, timezone
from fastapi import HTTPException

from models.otp_code import OtpCode
from models.user import User
from repositories.interfaces.i_user_repository import IUserRepository
from repositories.interfaces.i_otp_repository import IOtpRepository
from schemas.user_schema import UserCreate, UserLogin, UserResetPassword
from services.interfaces.i_auth_service import IAuthService
from services.interfaces.i_email_proxy_service import IEmailProxyService
from utils.auth import verify_password, create_access_token, hash_password
from utils.otp import generate_otp
from utils.logger import get_logger


logger = get_logger(__name__)

class AuthService(IAuthService):
    def __init__(self, repo: IUserRepository, otp_repo: IOtpRepository, email_proxy_service: IEmailProxyService):
        self.repo = repo
        self.otp_repo = otp_repo
        self.email_proxy_service = email_proxy_service
        
    def _validate_otp(self, email: str, otp_code: str) -> OtpCode:
        otp = self.otp_repo.get_by_email(email)
        if not otp:
            logger.warning(f"No verification code for {email}")
            raise HTTPException(status_code=404, detail="No verification code found for this email")
        if datetime.now(timezone.utc) > otp.expires_at:
            logger.warning(f"OTP expired for {email}")
            self.otp_repo.delete(otp)
            raise HTTPException(status_code=400, detail="Verification code expired")
        if otp.otp_code != otp_code:
            logger.warning(f"OTP code mismatch for {email}")
            raise HTTPException(status_code=401, detail="Incorrect otp code")
        return otp

    def login(self, data: UserLogin) -> dict:
        logger.info(f"Login attempt for {data.email}")
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            logger.warning("Incorrect email or password")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        token = create_access_token({"user_id": user.user_id})
        logger.info(f"Successful login for user {data.email}")
        return {"access_token": token, "user_id": user.user_id}
    
    def _send_otp(self, email: str) -> None:
        otp = generate_otp(email)
        self.otp_repo.create_or_replace(otp)
        self.email_proxy_service.send_otp(email, otp.otp_code)
        logger.info(f"OTP successfully sent to {email}")
    
    def send_register_otp(self, email: str) -> dict:
        logger.info(f"Sending OTP to {email}")
        existing = self.repo.get_by_email(email)
        if existing:
            logger.warning(f"User {email} already exists")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        self._send_otp(email)
        return {"message": "Verification code sent"}

    def register(self, data: UserCreate) -> dict:
        logger.info(f"Registration attempt for user {data.email}")
        otp = self._validate_otp(data.email, data.otp_code)
        self.otp_repo.delete(otp)
        new_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password)
        )
        self.repo.create(new_user)
        logger.info(f"User registered successfully {data.email}")
        return {"message": "User created successfully"}

    def send_forgot_password_otp(self, email: str) -> dict:
        logger.info(f"Sending forgot password OTP to {email}")
        user = self.repo.get_by_email(email)
        if not user:
            logger.warning(f"No user found for {email}")
            raise HTTPException(status_code=404, detail="No user found with this email")
        self._send_otp(email)
        return {"message": "Verification code sent"}

    def reset_forgotten_password(self, data: UserResetPassword) -> dict:
        logger.info(f"Resetting forgotten password for {data.email}")
        user = self.repo.get_by_email(data.email)
        if not user:
            logger.warning(f"No user found for {data.email}")
            raise HTTPException(status_code=404, detail="No user found with this email")
        otp = self._validate_otp(data.email, data.otp_code)
        self.otp_repo.delete(otp)
        self.repo.update_password(user.user_id, hash_password(data.new_password))
        logger.info(f"Password reset successfully for {data.email}")
        return {"message": "Password reset successfully"}
