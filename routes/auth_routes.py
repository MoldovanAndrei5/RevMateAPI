from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.user_schema import UserLogin, UserCreate, UserUpdate
from services.auth_service import AuthService
from utils.auth import get_current_user

router = APIRouter(tags=["Auth"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/login")
def login(user: UserLogin, service: AuthService = Depends(get_auth_service)):
    return service.login(user)

@router.post("/register")
def register(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    return service.register(user)

@router.put("/reset-password")
def reset_password(user_data: UserUpdate, user_id: int = Depends(get_current_user), service: AuthService = Depends(get_auth_service)):
    return service.reset_password(user_id, user_data)