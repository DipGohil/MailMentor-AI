from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.rag.llm import generate_answer
from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.rag.llm import generate_answer
from datetime import datetime, timedelta, timezone


def generate_inbox_summary(limit = 3):

    db = SessionLocal()
    
    today = datetime.now(timezone.utc)
    start = today-timedelta(days = 1)
    end = today

    # fetch latest emails
    emails = (
        db.query(Email)
        .order_by(Email.created_at.desc())
        .limit(limit)
        .all()
    )

    db.close()

    if not emails:
        return "No emails found."

    # STEP 1 — chunk summarization
    chunk_summaries = []

    for chunk in chunk_emails(emails, chunk_size=3):

        context = build_context(chunk)
        
        today = datetime.now().strftime("%Y-%m-%d")

        prompt = f"""
        Today date is {today}
        
        Summarize these emails in short bullet points.
        Respect email dates when summarizing.
        """

        summary = generate_answer(prompt, context)

        chunk_summaries.append(summary)

    # STEP 2 — final summary of summaries
    final_context = "\n".join(chunk_summaries)

    final_prompt = """
    Combine these partial summaries into ONE clean executive summary.
    Keep it short and professional.
    """

    final_summary = generate_answer(final_prompt, final_context)

    return final_summary

def chunk_emails(emails, chunk_size=3):
    """Split emails into small groups"""
    for i in range(0, len(emails), chunk_size):
        yield emails[i:i + chunk_size]

def build_context(email_chunk):
    context = ""
    for e in email_chunk:
        body = (e.body or "")[:150]
        context += f"""
Date: {e.created_at}
Subject: {e.subject}
Body: {body}
        
"""
    return context
def summarize_single_email(email_id: int):

    db = SessionLocal()

    email = db.query(Email).filter(Email.id == email_id).first()

    db.close()

    if not email:
        return "Email not found."

    context = f"""
    Date: {email.created_at}
    Sender: {email.sender}
    Subject: {email.subject}

    Email Body:
    {email.body[:2000]}
    """

    prompt = """
    You are an email assistant.

    Summarize this email naturally like a human assistant.

    Output format:
    - Short summary
    - Main purpose
    - Required action (if any)
    - Important deadlines (if any)

    Keep response clean and professional.
    """

    return generate_answer(prompt, context)