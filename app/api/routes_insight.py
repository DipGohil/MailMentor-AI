from fastapi import APIRouter
from app.api.routes_analytics import get_analytics
from app.services.insight_service import generate_ai_insights

router = APIRouter(prefix="/insights", tags=["AI Insights"])


@router.get("/")
def get_ai_insights(days: int = 7):
    try:
        stats = get_analytics(days)
        insights = generate_ai_insights(stats)

        return {
            "insights": insights
        }
    except Exception as e:
        return {"error": str(e)}