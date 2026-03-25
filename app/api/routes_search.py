from fastapi import APIRouter
from app.services.search_service import search_emails
from fastapi import Depends
from app.dependencies import get_current_user

router = APIRouter(
    prefix = "/search",
    tags = ["AI Search"]
)

@router.get("/")
def search(q: str, user = Depends(get_current_user)):
    app_username = user.get("sub", "")
    data = search_emails(q, app_username=app_username)
    
    return {
        "query": q,
        "answer": data["answer"],
        "results": data["results"]
    }