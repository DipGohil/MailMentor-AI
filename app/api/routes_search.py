from fastapi import APIRouter
from app.services.search_service import search_emails

router = APIRouter(
    prefix = "/search",
    tags = ["AI Search"]
)

@router.get("/")
def search(q: str):
    
    data = search_emails(q)
    
    return {
        "query": q,
        "answer": data["answer"],
        "results": data["results"]
    }