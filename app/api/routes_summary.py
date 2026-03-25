from fastapi import APIRouter
from app.services.summary_service import generate_inbox_summary
from fastapi import Depends
from app.dependencies import get_current_user


router = APIRouter(prefix="/summary", tags=["Summary"])

@router.get("/")
def get_summary(user = Depends(get_current_user)):
    owner_username = user.get("sub", "")
    return {"summary": generate_inbox_summary(owner_username=owner_username)}