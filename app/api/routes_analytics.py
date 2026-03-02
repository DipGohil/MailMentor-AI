from fastapi import APIRouter
from app.dependencies import SessionLocal
from app.models.email_model import Email
from sqlalchemy import func
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/")
def get_analytics(days: int = 7):

    db = SessionLocal()

    cutoff_date = datetime.now(timezone.utc) - timedelta(days = days)
    
    total = (
        db.query(Email)
        .filter(Email.created_at >= cutoff_date)
        .count()
        )
    
    category_counts = (
        db.query(Email.category, func.count(Email.id))
        .filter(Email.created_at >= cutoff_date)
        .group_by(Email.category)
        .all()
    )

    latest = (
        db.query(Email)
        .filter(Email.created_at >= cutoff_date)
        .order_by(Email.id.desc())
        .limit(5)
        .all()
        )
    

    db.close()

    return {
        "total": total,
        "categories": {c: n for c, n in category_counts},
        "jobs": dict(category_counts).get("Job", 0),
        "meetings": dict(category_counts).get("Meeting", 0),
        "important": dict(category_counts).get("Important", 0),
        "finance": dict(category_counts).get("Finance", 0),
        "latest_days": days,
        "latest": [
            {   
                "id": e.id,
                "sender": e.sender,
                "subject": e.subject,
                "category": e.category
            } for e in latest
        ]
    }