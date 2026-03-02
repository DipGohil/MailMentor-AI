from fastapi import APIRouter
from app.services.summary_service import generate_inbox_summary

router = APIRouter(prefix="/summary", tags=["Summary"])

@router.get("/")
def get_summary():
    return {"summary": generate_inbox_summary()}