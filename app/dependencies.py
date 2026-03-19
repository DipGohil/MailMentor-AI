import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import verify_token

# GET DATABASE URL (from env OR fallback)
DATABASE_URL = os.getenv("DATABASE_URL")

# FIX: fallback for CI/testing
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"

# FIX: SQLite needs special config
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# AUTH SETUP
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload