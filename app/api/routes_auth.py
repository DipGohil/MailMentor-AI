from fastapi import APIRouter, HTTPException
from app.dependencies import SessionLocal
from app.models.user_model import User
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token
)
from app.schemas.auth_schema import UserCreate, UserLogin   

router = APIRouter(prefix="/auth", tags=["Authentication"])


# REGISTER USER
@router.post("/register")
def register(user: UserCreate):   

    db = SessionLocal()

    existing = db.query(User).filter(User.username == user.username).first()

    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.close()

    return {"status": "user created"}


# LOGIN
@router.post("/login")
def login(user: UserLogin):   

    db = SessionLocal()

    existing_user = db.query(User).filter(User.username == user.username).first()

    if not existing_user or not verify_password(user.password, existing_user.password):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": existing_user.username})

    db.close()

    return {
        "access_token": token,
        "token_type": "bearer"
    }