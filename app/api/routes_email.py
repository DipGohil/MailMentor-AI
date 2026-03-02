from fastapi import APIRouter
from app.services.email_service import fetch_and_store_emails

router = APIRouter(
    prefix="/emails",
    tags=["Emails"]
)

@router.get("/fetch")
def fetch_emails():
    
    result = fetch_and_store_emails(limit = 5)
    
    return {
        "status": "success",
        "message": "emails fetched and stored",
        "data": result
    }
