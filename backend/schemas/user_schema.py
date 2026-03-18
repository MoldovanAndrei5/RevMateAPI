from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSchema(BaseModel):
    user_id: Optional[int] = None
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    
    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    
class UserUpdate(BaseModel):
    password: str
    