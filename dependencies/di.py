from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from repositories.user_repository import UserRepository
from repositories.car_repository import CarRepository
from repositories.interfaces.i_user_repository import IUserRepository
from repositories.interfaces.i_car_repository import ICarRepository
from repositories.interfaces.i_invoice_repository import IInvoiceRepository
from repositories.interfaces.i_otp_repository import IOtpRepository
from repositories.interfaces.i_task_repository import ITaskRepository
from repositories.interfaces.i_transfer_repository import ITransferRepository
from repositories.invoice_repository import InvoiceRepository
from repositories.otp_repository import OtpRepository
from repositories.task_repository import TaskRepository
from repositories.transfer_repository import TransferRepository
from services.account_service import AccountService
from services.ai_proxy_service import AIProxyService
from services.auth_service import AuthService
from services.car_service import CarService
from services.email_proxy_service import EmailProxyService
from services.interfaces.i_account_service import IAccountService
from services.interfaces.i_ai_proxy_service import IAIProxyService
from services.interfaces.i_auth_service import IAuthService
from services.interfaces.i_car_service import ICarService
from services.interfaces.i_email_proxy_service import IEmailProxyService
from services.interfaces.i_invoice_service import IInvoiceService
from services.interfaces.i_task_service import ITaskService
from services.interfaces.i_transfer_service import ITransferService
from services.interfaces.i_upload_service import IUploadService
from services.invoice_service import InvoiceService
from services.task_service import TaskService
from services.transfer_service import TransferService
from services.upload_service import UploadService


def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)

def get_car_repository(db: Session = Depends(get_db)) -> ICarRepository:
    return CarRepository(db)

def get_invoice_repository(db: Session = Depends(get_db)) -> IInvoiceRepository:
    return InvoiceRepository(db)

def get_otp_repository(db: Session = Depends(get_db)) -> IOtpRepository:
    return OtpRepository(db)

def get_task_repository(db: Session = Depends(get_db)) -> ITaskRepository:
    return TaskRepository(db)

def get_transfer_repository(db: Session = Depends(get_db)) -> ITransferRepository:
    return TransferRepository(db)

def get_ai_proxy_service() -> IAIProxyService:
    return AIProxyService()

def get_email_proxy_service() -> IEmailProxyService:
    return EmailProxyService()

def get_auth_service(
        repo: IUserRepository = Depends(get_user_repository),
        otp_repo: IOtpRepository = Depends(get_otp_repository),
        email_proxy_service: IEmailProxyService = Depends(get_email_proxy_service),
) -> IAuthService:
    return AuthService(repo, otp_repo, email_proxy_service)

def get_car_service(
        repo: ICarRepository = Depends(get_car_repository),
        task_repo: ITaskRepository = Depends(get_task_repository)
) -> ICarService:
    return CarService(repo, task_repo)

def get_invoice_service(
        repo: IInvoiceRepository = Depends(get_invoice_repository),
        task_repo: ITaskRepository = Depends(get_task_repository)
) -> IInvoiceService:
    return InvoiceService(repo, task_repo)

def get_task_service(
        repo: ITaskRepository = Depends(get_task_repository),
        car_repo: ICarRepository = Depends(get_car_repository)
) -> ITaskService:
    return TaskService(repo, car_repo)

def get_transfer_service(
        repo:ITransferRepository = Depends(get_transfer_repository),
        car_repo: ICarRepository = Depends(get_car_repository),
        user_repo: IUserRepository = Depends(get_user_repository)
) -> ITransferService:
    return TransferService(repo, car_repo, user_repo)

def get_upload_service() -> IUploadService:
    return UploadService()

def get_account_service(
        repo: IUserRepository = Depends(get_user_repository),
        car_repo: ICarRepository = Depends(get_car_repository),
        task_repo: ITaskRepository = Depends(get_task_repository),
        otp_repo: IOtpRepository = Depends(get_otp_repository),
        email_proxy_service: IEmailProxyService = Depends(get_email_proxy_service)
) -> IAccountService:
    return AccountService(repo, car_repo, task_repo, otp_repo, email_proxy_service)
