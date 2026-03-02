from fastapi import FastAPI
from app.api.routes_email import router as email_router
from app.api.routes_search import router as search_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_summary import router as summary_router
from app.api.routes_actions import router as action_router
from app.api.routes_insight import router as insight_router
from app.models.summary_model import Summary
from app.models.email_model import Email
from app.dependencies import Base, engine
from app.services.summary_service import summarize_single_email


app = FastAPI(title = "MailMentor API")
Base.metadata.create_all(bind=engine)
app.include_router(email_router)
app.include_router(search_router)
app.include_router(analytics_router)
app.include_router(summary_router)
app.include_router(action_router)
app.include_router(insight_router)

@app.get("/")
def health():
    return {"status": "MailMentor running"}

@app.get("/email-summary/{email_id}")
def email_summary(email_id: int):
    return {
        "summary": summarize_single_email(email_id)
    }