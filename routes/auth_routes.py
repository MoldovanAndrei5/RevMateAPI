from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user_schema import UserLogin, UserCreate, UserUpdate
from utils.auth import verify_password, create_access_token, hash_password, get_current_user

router = APIRouter(tags=["Auth"])


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    print(f"[LOGIN] Attempt for email: {user.email}")

    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        print(f"[LOGIN FAILED] No user found with email: {user.email}")
        raise HTTPException(status_code=404, detail="There is no user with this email")

    print(f"[LOGIN] User found: ID {db_user.user_id}")

    if not verify_password(user.password, db_user.hashed_password):
        print(f"[LOGIN FAILED] Incorrect password for user ID: {db_user.user_id}")
        raise HTTPException(status_code=404, detail="Incorrect password")

    print(f"[LOGIN SUCCESS] User ID {db_user.user_id} authenticated")

    token = create_access_token({"user_id": db_user.user_id})
    print(f"[TOKEN CREATED] for user ID {db_user.user_id}")

    return {
        "access_token": token,
        "user_id": db_user.user_id
    }


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    print(f"[REGISTER] Attempt for email: {user.email}")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        print(f"[REGISTER FAILED] Email already exists: {user.email}")
        raise HTTPException(status_code=400, detail="User with this email already exists")

    print(f"[REGISTER] Creating new user: {user.email}")

    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"[REGISTER SUCCESS] User created with ID: {new_user.user_id}")

    return {
        "message": "User created successfully"
    }


@router.put("/reset-password")
def reset_password(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    print(f"[RESET PASSWORD] Attempt for user ID: {user_id}")

    db_query = db.query(User).filter(User.user_id == user_id)
    db_user = db_query.first()

    if not db_user:
        print(f"[RESET FAILED] User not found: ID {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    print(f"[RESET] Updating password for user ID: {user_id}")

    db_query.update({"hashed_password": hash_password(user_data.password)})
    db.commit()
    db.refresh(db_user)

    print(f"[RESET SUCCESS] Password updated for user ID: {user_id}")

    return db_user