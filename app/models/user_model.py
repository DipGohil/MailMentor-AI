from sqlalchemy import Column, Integer, String
from app.dependencies import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

class GmailConnection(Base):
    __tablename__ = "gmail_connections"

    id = Column(Integer, primary_key=True, index=True)
    app_username = Column(String, unique=True)
    email_address = Column(String, unique=True)