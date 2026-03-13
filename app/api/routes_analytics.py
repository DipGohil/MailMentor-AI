from fastapi import APIRouter
from app.dependencies import SessionLocal
from app.models.email_model import Email
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.rag.llm import generate_answer
from app.models.summary_model import Summary

PRIORITY_KEYWORDS = [
    "urgent",
    "asap",
    "important",
    "deadline",
    "meeting",
    "action required",
    "immediately",
    "submit",
]

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_gmail_service():

    creds = Credentials.from_authorized_user_file(
        "token.json",
        ["https://www.googleapis.com/auth/gmail.readonly"]
    )

    service = build("gmail", "v1", credentials=creds)

    return service

def detect_priority(subject):

    text = subject.lower()

    for word in PRIORITY_KEYWORDS:
        if word in text:
            return "Important"

    return "Normal"

@router.get("/")
def get_analytics(days: int = 7):

    db = SessionLocal()

    cutoff_date = datetime.now(timezone.utc) - timedelta(days = days)
    
    emails = (
        db.query(Email)
        .filter(Email.created_at >= cutoff_date)
        .all()
    )
    
    
    # CATEGORY DISTRIBUTION
    
    category_counts = (
        db.query(Email.category, func.count(Email.id))
        .filter(Email.created_at >= cutoff_date)
        .group_by(Email.category)
        .all()
    )

    categories = {c: n for c, n in category_counts}
    
    trend = (
        db.query(
            func.date(Email.created_at).label("day"),
            func.count(Email.id)
        )
        .filter(Email.created_at >= cutoff_date)
        .group_by(func.date(Email.created_at))
        .order_by(func.date(Email.created_at))
        .all()
    )
    trend_data = [
        {"day": str(t.day), "count": t[1]}
        for t in trend
    ]
 

    total = len(emails)
    jobs = len([e for e in emails if e.category == "Job"])
    meetings = len([e for e in emails if e.category == "Meeting"])
    important = len([e for e in emails if e.priority == "Important"])
    finance = len([e for e in emails if e.category == "Finance"])
    
    latest_emails = (
        db.query(Email)
        .filter(Email.created_at >= cutoff_date)
        .order_by(Email.created_at.desc())
        .limit(50)
        .all()
    )
    
    latest = []

    for e in latest_emails:

        
        latest.append({
            "id": e.gmail_id,
            "sender": e.sender,
            "subject": e.subject,
            "category": e.category,
            "priority": e.priority
        })   

    db.close()
    
    latest = sorted(
        latest,
        key=lambda x: x["priority"] != "Important"
    )

    return {
        "total": total,
        "jobs": jobs,
        "meetings": meetings,
        "finance": finance,
        "important": important,
        "categories": categories,
        "latest_days": days,
        "latest": latest,
        "trend": trend_data
    }

@router.get("/gmail-summary/{message_id}")
def summarize_gmail_email(message_id: str):

    db = SessionLocal()
    
    email = db.query(Email).filter(
        Email.gmail_id == message_id
    ).first()
    
    if not email:
        db.close()
        return {"summary": "Email not found in database"}
    
    # check if summary already exists
    
    existing = db.query(Summary).filter(
        Summary.email_id == email.id
    ).first()
    
    if existing:
        db.close()
        return {"summary": existing.summary_text}
    
    # if not, fetch email from gmail
    
    service = get_gmail_service()

    msg_data = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    headers = msg_data["payload"]["headers"]

    subject = ""
    sender = ""

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
        if h["name"] == "From":
            sender = h["value"]

    # extract snippet
    snippet = msg_data.get("snippet", "")

    prompt = f"""
You are MailMentor AI, an executive email assistant.

Summarize the following email clearly and professionally.

Email details:
Subject: {subject}
Sender: {sender}
Content: {snippet}

Rules:
• Do NOT repeat "Subject" or "Sender".
• Do NOT copy the email text.
• Write a concise professional summary.
• Use 1–2 bullet points only.
• Each bullet should be short and clear.

Good example:
• A LinkedIn job alert announcing Data Scientist opportunities at Adani Natural Resources.

Return only the summary.
"""

    summary = generate_answer(prompt, "")
    
    new_summary = Summary(
        email_id = email.id,
        summary_text = summary
    )
    
    db.add(new_summary)
    db.commit()
    db.close()

    return {
        "summary": summary
    }
    
@router.get("/email/{message_id}")
def get_full_email(message_id: str):

    service = get_gmail_service()

    msg_data = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    headers = msg_data["payload"]["headers"]

    subject = ""
    sender = ""

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
        if h["name"] == "From":
            sender = h["value"]

    snippet = msg_data.get("snippet", "")

    return {
        "subject": subject,
        "sender": sender,
        "body": snippet
    }