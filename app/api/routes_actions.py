from fastapi import APIRouter
from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.services.action_service import extract_action_and_deadline

router = APIRouter(
    prefix="/actions",
    tags=["Action Extraction"]
)


@router.get("/")
def get_actions(limit: int = 20):

    db = SessionLocal()

    emails = (
        db.query(Email)
        .order_by(Email.created_at.desc())
        .limit(limit)
        .all()
    )

    results = []

    for e in emails:

        text = f"{e.subject}. {e.body}"

        extracted = extract_action_and_deadline(text)

        if extracted:
            results.append({
                "email_id": e.id,
                "subject": e.subject,
                "action": extracted["action"],
                "deadline": extracted["deadline"]
            })

    db.close()

    return {
        "count": len(results),
        "actions": results
    }