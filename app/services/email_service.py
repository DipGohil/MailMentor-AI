from app.ingestion.gmail_client import authenticate_gmail, get_full_message
from app.services.categorization_service import categorize_email
from app.ingestion.parser import parse_email
from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.rag.vector_store import add_email_vector
from app.models.summary_model import Summary
from app.services.summary_generator import generate_email_summary
from datetime import datetime, timedelta, timezone

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def save_email(db, data):
    
    # Prevent duplicates
    existing = db.query(Email).filter(
        Email.gmail_id == data["gmail_id"]
    ).first()
    
    # if existing:
    #     return
    
    category = categorize_email(data["subject"])
    
    email = Email(
        gmail_id = data["gmail_id"],
        thread_id = data["thread_id"],
        sender = data["sender"],
        subject = data["subject"],
        body = data["body"],
        category = category,
        created_at = data["created_at"].replace(tzinfo=None)
    )
    
    db.add(email)
    db.commit()
    db.refresh(email)
    
    # --- generate AI summary ---
    summary_text = generate_email_summary(
        email.subject,
        email.body or ""
    )

    summary = Summary(
        email_id=email.id,
        summary_text=summary_text
    )

    db.add(summary)
    db.commit()
    
    # add vector
    text_for_embedding = f"{email.subject}\n{email.body or ''}"
    add_email_vector(email.id, text_for_embedding, email.created_at)

def fetch_and_store_emails(limit = 10):
    service = authenticate_gmail()
    db = SessionLocal()
    
    # last X days
    days = 7
    after_time = int(
        (datetime.now(timezone.utc) - timedelta(days = days)).timestamp()
    )
    
    query = f"after:{after_time}"
    
    messages = service.users().messages().list(
        userId = "me",
        q = query,
        maxResults = limit
    ).execute().get("messages", [])
    
    for m in messages:
        
        full_msg = get_full_message(service, m["id"])
        
        parsed = parse_email(full_msg)
        
        save_email(db, parsed)
    
    db.close()
    
    return {"status": "emails saved"}
