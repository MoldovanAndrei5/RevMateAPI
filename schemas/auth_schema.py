from pydantic import BaseModel

class AuthResponse(BaseModel):
    access_token: str
    user_id: int

class SendOtpRequest(BaseModel):
    email: str