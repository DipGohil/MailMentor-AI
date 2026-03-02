from fastapi import APIRouter
from app.services.action_service import extract_actions

router = APIRouter(prefix="/actions", tags=["Actions"])

@router.get("/")
def get_actions():
    return {"actions": extract_actions()}