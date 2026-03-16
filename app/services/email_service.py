from app.ingestion.gmail_client import authenticate_gmail, get_full_message
from app.services.categorization_service import categorize_email
from app.ingestion.parser import parse_email
from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.models.summary_model import Summary
from app.services.summary_generator import generate_email_summary
from datetime import datetime, timedelta, timezone
from app.rag.vector_store import add_email_vectors_batch
from app.services.categorization_service import detect_priority
from googleapiclient.errors import HttpError

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def save_email(db, data, generate_summary = True):
    
    # Prevent duplicates
    existing = db.query(Email).filter(
        Email.gmail_id == data["gmail_id"]
    ).first()
    
    if existing:
        return None
    
    category = categorize_email(data["subject"])
    
    # priority = detect_priority(data["subject"] + " " + data["body"])
    text = f"{data['subject']} {data['body'][:800]}"
    priority = detect_priority(text)
    
    email = Email(
        gmail_id = data["gmail_id"],
        thread_id = data["thread_id"],
        sender = data["sender"],
        subject = data["subject"],
        body = data["body"],
        history_id = data.get("history_id"), # New
        category = category,
        priority = priority,
        created_at = data["created_at"].replace(tzinfo=None)
    )
    
    db.add(email)
    db.commit()
    db.refresh(email)
    
    # Generate summary only for short emails
    if generate_summary and email.body:

        summary_text = generate_email_summary(
            email.subject,
            email.body[:1500]
        )

        summary = Summary(
            email_id=email.id,
            summary_text=summary_text
        )

        db.add(summary)
        db.commit()
        
    return email
    

def fetch_and_store_emails(limit=100): #500

    service = authenticate_gmail()
    db = SessionLocal()
    
    # get last history id
    last_email = (
        db.query(Email)
        .order_by(Email.history_id.desc())
        .first()
    )
    
    last_history_id = last_email.history_id if last_email else None
    

    emails_for_embedding = []

    fetched = 0
    next_page = None

    # query = None

    while fetched < limit:

        # incremental sync
        messages = []

        if last_history_id:

            try:

                history = service.users().history().list(
                    userId="me",
                    startHistoryId=last_history_id
                ).execute()

                for record in history.get("history", []):
                    for msg in record.get("messagesAdded", []):
                        messages.append({"id": msg["message"]["id"]})

            except HttpError:

                # history expired → fallback to full fetch
                print("History expired. Running full sync.")

                last_history_id = None

        else:
            # first time full fetch
            response = service.users().messages().list(
                userId="me",
                q = "newer_than:7d",
                # q = "newer_than:7d -category:promotions",
                maxResults=25, #100
                pageToken=next_page
            ).execute()

            messages = response.get("messages", [])

        if not messages:
            break

        for m in messages:

            full_msg = get_full_message(service, m["id"])

            parsed = parse_email(full_msg)
            
            # Attach gmail history id
            parsed["history_id"] = full_msg.get("historyId")

            email = save_email(db, parsed, generate_summary=False)

            if email:

                text_for_embedding = f"""
                Subject: {email.subject}
                Sender: {email.sender}
                Category: {email.category}

                {(email.body or '')[:500]}
                """

                emails_for_embedding.append({
                    "id": email.id,
                    "text": text_for_embedding,
                    "created_at": email.created_at
                })

            fetched += 1

            if fetched >= limit:
                break

        next_page = response.get("nextPageToken")

        if not next_page:
            break
    
    if emails_for_embedding:
        add_email_vectors_batch(emails_for_embedding)

    db.close()

    return {"status": f"{fetched} emails saved"}

