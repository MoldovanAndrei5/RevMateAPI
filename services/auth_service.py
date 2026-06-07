from datetime import datetime, timezone
from fastapi import HTTPException
from models.user import User
from repositories.interfaces.i_user_repository import IUserRepository
from repositories.interfaces.i_otp_repository import IOtpRepository
from schemas.user_schema import UserCreate, UserLogin
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

    def login(self, data: UserLogin) -> dict:
        logger.info(f"Login attempt for {data.email}")
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            logger.warning("Incorrect email or password")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        token = create_access_token({"user_id": user.user_id})
        logger.info(f"Successful login for user {data.email}")
        return {"access_token": token, "user_id": user.user_id}
    
    def send_otp(self, email: str) -> dict:
        logger.info(f"Sending OTP to {email}")
        existing = self.repo.get_by_email(email)
        if existing:
            logger.warning(f"User {email} already exists")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        otp = generate_otp(email)
        self.otp_repo.create_or_replace(otp)
        self.email_proxy_service.send_otp(email, otp.otp_code)
        logger.info(f"OTP successfully sent to {email}")
        return {"message": "Verification code sent"}

    def register(self, data: UserCreate) -> dict:
        logger.info(f"Registration attempt for user {data.email}")
        otp = self.otp_repo.get_by_email(data.email)
        if not otp:
            logger.warning(f"No verification code for {data.email}")
            raise HTTPException(status_code=404, detail="No verification code found for this email")
        if datetime.now(timezone.utc) > otp.expires_at:
            logger.warning(f"OTP expired for {data.email}")
            self.otp_repo.delete(otp)
            raise HTTPException(status_code=400, detail="Verification code expired")
        if otp.otp_code != data.otp_code:
            logger.warning(f"OTP code mismatch for {data.email}")
            raise HTTPException(status_code=401, detail="Incorrect otp code")
        
        new_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password)
        )
        self.repo.create(new_user)
        self.otp_repo.delete(otp)
        logger.info(f"User registered successfully {data.email}")
        return {"message": "User created successfully"}
