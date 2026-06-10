from fastapi import APIRouter, Depends
from dependencies.di import get_account_service
from schemas.response_schema import MessageResponse
from schemas.stats_schema import StatsResponse
from schemas.user_schema import UserUpdate, DeleteAccount
from services.interfaces.i_account_service import IAccountService
from utils.auth import get_current_user


router = APIRouter(tags=["Account"], dependencies=[Depends(get_current_user)])

@router.get("/stats", response_model=StatsResponse)
def get_account_stats(user_id: int = Depends(get_current_user), account_service: IAccountService = Depends(get_account_service)):
    return account_service.get_account_stats(user_id)

@router.put("/reset-password", response_model=MessageResponse)
def reset_password(user_data: UserUpdate, user_id: int = Depends(get_current_user), account_service: IAccountService = Depends(get_account_service)):
    return account_service.reset_password(user_id, user_data)

@router.post("/send-delete-otp", response_model=MessageResponse)
def send_delete_otp(user_id: int = Depends(get_current_user), account_service: IAccountService = Depends(get_account_service)):
    return account_service.send_delete_otp(user_id)

@router.delete("/delete-account", response_model=MessageResponse)
def delete_account(body: DeleteAccount, user_id: int = Depends(get_current_user), account_service: IAccountService = Depends(get_account_service)):
    return account_service.delete_account(user_id, body.otp_code)
