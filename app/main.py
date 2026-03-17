from fastapi import FastAPI
from app.api.routes_email import router as email_router
from app.api.routes_search import router as search_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_summary import router as summary_router
from app.dependencies import Base, engine
from app.services.summary_service import summarize_single_email
from app.api.routes_actions import router as actions_router


app = FastAPI(title = "MailMentor API")
Base.metadata.create_all(bind=engine)
app.include_router(email_router)
app.include_router(search_router)
app.include_router(analytics_router)
app.include_router(summary_router)
app.include_router(actions_router)

@app.get("/")
def health():
    return {"status": "MailMentor running"}

@app.get("/email-summary/{email_id}")
def email_summary(email_id: int):
    return {
        "summary": summarize_single_email(email_id)
    }