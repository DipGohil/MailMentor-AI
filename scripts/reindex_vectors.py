from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.rag.vector_store import add_email_vector


def reindex():

    db = SessionLocal()

    emails = db.query(Email).all()

    print(f"Found {len(emails)} emails")

    for email in emails:

        text = f"{email.subject}\n{email.body or ''}"

        add_email_vector(email.id, text)

    print("Reindex completed")

    db.close()


if __name__ == "__main__":
    reindex()