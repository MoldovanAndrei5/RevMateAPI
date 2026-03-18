from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.user_schema import UserLogin, UserCreate, UserUpdate
from backend.utils.auth import verify_password, create_access_token, hash_password, get_current_user

router = APIRouter(tags=["Auth"])

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="There is no user with this email")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=404, detail="Incorrect password")
    token = create_access_token({"user_id": db_user.user_id})
    return {
        "access_token": token,
        "user_id": db_user.user_id
    }

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    new_user = User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        hashed_password = hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User created successfully"
    }

@router.put("/reset-password")
def reset_password(user_data: UserUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user),):
    db_query = db.query(User).filter(User.user_id == user_id)
    db_user = db_query.first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_query.update({"hashed_password": hash_password(user_data.password)})
    db.commit()
    db.refresh(db_user)
    return db_user
