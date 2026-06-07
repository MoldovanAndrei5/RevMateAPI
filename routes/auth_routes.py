from fastapi import APIRouter, Depends
from dependencies.di import get_auth_service
from schemas.auth_schema import AuthResponse, SendOtpRequest
from schemas.response_schema import MessageResponse
from schemas.user_schema import UserLogin, UserCreate, UserResetPassword
from services.interfaces.i_auth_service import IAuthService

router = APIRouter(tags=["Auth"])

@router.post("/login", response_model=AuthResponse)
def login(user: UserLogin, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.login(user)

@router.post("/send-otp", response_model=MessageResponse)
def send_register_otp(body: SendOtpRequest, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.send_register_otp(body.email)

@router.post("/register", response_model=MessageResponse)
def register(user: UserCreate, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.register(user)

@router.post("/forgot-password/send-otp", response_model=MessageResponse)
def send_forgot_password_otp(body: SendOtpRequest, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.send_forgot_password_otp(body.email)

@router.post("/forgot-password/reset", response_model=MessageResponse)
def reset_forgotten_password(body: UserResetPassword, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.reset_forgotten_password(body)
