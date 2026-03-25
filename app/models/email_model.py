## Created db table to store gmail data

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from app.dependencies import Base
from datetime import datetime, timezone

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index = True)
    # gmail_id is not globally unique across all app users
    gmail_id = Column(String, index=True)
    owner_username = Column(String, index=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    thread_id = Column(String)
    history_id = Column(String, index = True)
    category = Column(String, default="General")
    priority = Column(String, default="Normal")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_completed = Column(Boolean, default=False)

    __table_args__ = (
        Index("ix_emails_owner_gmail", "owner_username", "gmail_id"),
    )
