from sqlalchemy import Column, Integer, Text, DateTime
from app.dependencies import Base
from datetime import datetime, timezone

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)
    days = Column(Integer)
    insight_text = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))