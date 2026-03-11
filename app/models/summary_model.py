from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.dependencies import Base

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("emails.id"), unique = True, index = True)
    summary_text = Column(Text)