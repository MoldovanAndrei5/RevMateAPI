from datetime import datetime, timezone
from fastapi import HTTPException
from repositories.interfaces.i_car_repository import ICarRepository
from repositories.interfaces.i_otp_repository import IOtpRepository
from repositories.interfaces.i_task_repository import ITaskRepository
from repositories.interfaces.i_user_repository import IUserRepository
from schemas.stats_schema import StatsResponse, MonthlyStats
from schemas.user_schema import UserUpdate
from services.interfaces.i_account_service import IAccountService
from services.interfaces.i_email_proxy_service import IEmailProxyService
from utils.auth import hash_password
from utils.otp import generate_otp
from utils.s3 import delete_file
from utils.logger import get_logger


logger = get_logger(__name__)

class AccountService(IAccountService):
    def __init__(self, repo: IUserRepository, car_repo: ICarRepository, task_repo: ITaskRepository, otp_repo: IOtpRepository, email_proxy_service: IEmailProxyService):
        self.repo = repo
        self.car_repo = car_repo
        self.task_repo = task_repo
        self.otp_repo = otp_repo
        self.email_proxy_service = email_proxy_service

    def get_account_stats(self, user_id: int) -> StatsResponse:
        logger.info(f"Getting account stats for user {user_id}")
        tasks = self.task_repo.get_all_by_user(user_id)
        now = datetime.now(timezone.utc)

        total_spent = 0.0
        completed = 0
        pending = 0
        overdue = 0
        spent_by_category: dict[str, float] = {}
        monthly: dict[str, dict[str, int]] = {}

        for task in tasks:
            # Cost aggregation
            if task.cost is not None:
                cost = float(task.cost)
                total_spent += cost
                category = task.category or "Other"
                spent_by_category[category] = spent_by_category.get(category, 0.0) + cost

            # Status counts + monthly grouping
            if task.completed_date is not None:
                completed += 1
                dt = datetime.fromtimestamp(task.completed_date / 1000, tz=timezone.utc)
                key = dt.strftime("%b %Y")
                monthly.setdefault(key, {"completed": 0, "scheduled": 0})
                monthly[key]["completed"] += 1
            elif task.scheduled_date is not None:
                scheduled_dt = datetime.fromtimestamp(task.scheduled_date / 1000, tz=timezone.utc)
                key = scheduled_dt.strftime("%b %Y")
                monthly.setdefault(key, {"completed": 0, "scheduled": 0})
                monthly[key]["scheduled"] += 1
                if scheduled_dt < now:
                    overdue += 1
                else:
                    pending += 1
            else:
                pending += 1

        sorted_months = sorted(monthly.items(), key=lambda x: datetime.strptime(x[0], "%b %Y"))
        tasks_by_month = [MonthlyStats(month=k, completed=v["completed"], scheduled=v["scheduled"]) for k, v in sorted_months]
        logger.info(f"Successfully generated stats for user {user_id}")
        return StatsResponse(
            total_spent=round(total_spent, 2),
            total_tasks=len(tasks),
            completed_tasks=completed,
            pending_tasks=pending,
            overdue_tasks=overdue,
            spent_by_category=spent_by_category,
            tasks_by_month=tasks_by_month,
        )
        
    def reset_password(self, user_id: int, data: UserUpdate) -> dict:
        logger.info(f"Resetting password for user {user_id}")
        user = self.repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        self.repo.update_password(user_id, hash_password(data.password))
        logger.info(f"Password updated for user {user_id}")
        return {"message": "Password updated successfully"}
    
    def send_delete_otp(self, user_id: int) -> dict:
        logger.info(f"Sending delete OTP for user {user_id}")
        user = self.repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        otp = generate_otp(user.email)
        self.otp_repo.create_or_replace(otp)
        self.email_proxy_service.send_otp(user.email, otp.otp_code)
        logger.info(f"OTP sent for user {user_id}")
        return {"message": "Verification code sent"}
    
    def delete_account(self, user_id: int, otp_code: str) -> dict:
        logger.info(f"Deleting account for user {user_id}")
        user = self.repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        otp = self.otp_repo.get_by_email(user.email)
        if not otp:
            logger.warning(f"No verification code found for {user.email}")
            raise HTTPException(status_code=404, detail="No verification code found for this email")
        if datetime.now(timezone.utc) > otp.expires_at:
            logger.warning(f"OTP expired for {user.email}")
            self.otp_repo.delete(otp)
            raise HTTPException(status_code=400, detail="Verification code expired")
        if otp.otp_code != otp_code:
            logger.warning(f"OTP code mismatch for {user.email}")
            raise HTTPException(status_code=401, detail="Incorrect OTP code")
        cars = self.car_repo.get_all_by_user(user_id)
        for car in cars:
            if car.image_key is not None:
                try:
                    delete_file(car.image_key)
                except Exception as e:
                    logger.error(f"Failed to delete file {car.image_key}: {e}")
            tasks = self.task_repo.get_by_car_with_invoices(car.car_uuid)
            for task in tasks:
                for invoice in task.invoices:
                    try:
                        delete_file(invoice.file_key)
                    except Exception as e:
                        logger.error(f"Failed to delete file {invoice.file_key}: {e}")
        self.repo.delete(user)
        logger.info(f"Deleted account for user {user_id}")
        return {"message": "Account deleted successfully"}