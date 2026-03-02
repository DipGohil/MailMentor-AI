## Created db table to store gmail data

from sqlalchemy import Column, Integer, String, Text, DateTime
from app.dependencies import Base
from datetime import datetime, timezone

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index = True)
    gmail_id = Column(String, unique=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    thread_id = Column(String)
    category = Column(String, default="General")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
