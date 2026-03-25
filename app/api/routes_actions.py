from fastapi import APIRouter
from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.services.action_service import extract_action_and_deadline
from app.dependencies import get_current_user
from fastapi import Depends

router = APIRouter(
    prefix="/actions",
    tags=["Action Extraction"]
)


# GET ACTIONS
@router.get("/")
def get_actions(limit: int = 20, user = Depends(get_current_user)):

    db = SessionLocal()
    owner_username = user.get("sub", "")

    emails = (
        db.query(Email)
        .filter(Email.owner_username == owner_username)
        .order_by(Email.created_at.desc())
        .limit(limit)
        .all()
    )

    results = []

    for e in emails:

        text = f"{e.subject}. {e.body[:500]}"

        extracted = extract_action_and_deadline(text)

        if extracted:
            results.append({
                "email_id": e.id,
                "subject": e.subject,
                "sender": e.sender,                
                "action": extracted["action"],
                "deadline": extracted["deadline"],
                "is_completed": getattr(e, "is_completed", False)  # NEW SAFE
            })

    db.close()

    return {
        "count": len(results),
        "actions": results
    }


# MARK TASK COMPLETE
@router.post("/complete/{email_id}")
def mark_complete(email_id: int, user = Depends(get_current_user)):

    db = SessionLocal()
    owner_username = user.get("sub", "")

    email = db.query(Email).filter(
        Email.owner_username == owner_username,
        Email.id == email_id
    ).first()

    if not email:
        return {"status": "error", "message": "Email not found"}

    email.is_completed = True
    db.commit()
    db.close()

    return {"status": "completed"}