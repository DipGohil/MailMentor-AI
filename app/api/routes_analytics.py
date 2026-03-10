from fastapi import APIRouter
from app.dependencies import SessionLocal
from app.models.email_model import Email
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

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

    total = len(emails)

    jobs = len([e for e in emails if e.category == "Job"])
    meetings = len([e for e in emails if e.category == "Meeting"])
    important = len([e for e in emails
        if detect_priority(e.subject) == "Important"
        or "action" in e.subject.lower()
    ])
    
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        maxResults=100
    ).execute()

    messages = results.get("messages", [])
    latest = []

    for msg in messages:

        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full",
            metadataHeaders=["Subject", "From"]
        ).execute()

        headers = msg_data["payload"]["headers"]

        subject = ""
        sender = ""

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            if h["name"] == "From":
                sender = h["value"]

        priority = detect_priority(subject)
        
        latest.append({
            "id": msg["id"],
            "sender": sender,
            "subject": subject,
            "category": "Live Gmail",
            "priority": priority
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
        "important": important,
        "latest_days": days,
        "latest": latest
    }
from app.rag.llm import generate_answer

@router.get("/gmail-summary/{message_id}")
def summarize_gmail_email(message_id: str):

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
Summarize this email briefly.

Subject: {subject}
From: {sender}

Content:
{snippet}

- make it more humanoid.

Rules:
- bullet point style.(if needed)
- Each bullet point is on next line.
- short summary.
"""

    summary = generate_answer(prompt, "")

    return {
        "summary": summary
    }