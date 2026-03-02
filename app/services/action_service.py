from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.rag.llm import generate_answer


def extract_actions():

    db = SessionLocal()

    emails = db.query(Email).order_by(Email.id.desc()).limit(8).all()

    context = ""

    for e in emails:
        context += f"{e.subject}\n{e.body[:400]}\n\n"

    db.close()

    prompt = """
Extract action items from emails.
Return list format:
- task
- deadline
"""

    return generate_answer(prompt, context)