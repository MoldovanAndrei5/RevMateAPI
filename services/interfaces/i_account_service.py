from abc import ABC, abstractmethod
from schemas.stats_schema import StatsResponse
from schemas.user_schema import UserUpdate


class IAccountService(ABC):
    @abstractmethod
    def get_account_stats(self, user_id: int) -> StatsResponse: ...
    
    @abstractmethod
    def reset_password(self, user_id: int, data: UserUpdate) -> dict: ...
    
    @abstractmethod
    def send_delete_otp(self, user_id: int) -> dict: ...
    
    @abstractmethod
    def delete_account(self, user_id: int, otp_code: str) -> dict: ...
