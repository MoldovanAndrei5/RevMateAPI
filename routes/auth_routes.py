from fastapi import APIRouter, Depends
from dependencies.di import get_auth_service
from schemas.auth_schema import AuthResponse, SendOtpRequest
from schemas.response_schema import MessageResponse
from schemas.user_schema import UserLogin, UserCreate, UserUpdate
from services.interfaces.i_auth_service import IAuthService
from utils.auth import get_current_user

router = APIRouter(tags=["Auth"])

@router.post("/login", response_model=AuthResponse)
def login(user: UserLogin, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.login(user)

@router.post("/send-otp", response_model=MessageResponse)
def send_otp(body: SendOtpRequest, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.send_otp(body.email)

@router.post("/register", response_model=MessageResponse)
def register(user: UserCreate, auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.register(user)

@router.put("/reset-password", response_model=MessageResponse)
def reset_password(user_data: UserUpdate, user_id: int = Depends(get_current_user), auth_service: IAuthService = Depends(get_auth_service)):
    return auth_service.reset_password(user_id, user_data)