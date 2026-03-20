from fastapi import APIRouter
from app.services.email_service import fetch_and_store_emails
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.dependencies import get_current_user
from fastapi import Depends
import os

router = APIRouter(
    prefix="/emails",
    tags=["Emails"]
)

@router.get("/fetch")
def fetch_emails(user = Depends(get_current_user)):
    
    if os.getenv("TESTING") == "1":
        return {"status": "skipped in test"}
    
    result = fetch_and_store_emails(limit = 500)
    
    return {
        "status": "success",
        "message": "emails fetched and stored",
        "data": result
    }

def get_gmail_service():

    creds = Credentials.from_authorized_user_file(
        "token.json",
        ["https://www.googleapis.com/auth/gmail.readonly"]
    )

    return build("gmail", "v1", credentials=creds)


@router.get("/thread/{thread_id}")
def get_thread(thread_id: str, user = Depends(get_current_user)):

    # skip in test/CI
    if os.getenv("TESTING") == "1":
        return {'thread': []}
    
    service = get_gmail_service()
    
    service = get_gmail_service()

    thread = service.users().threads().get(
        userId="me",
        id=thread_id
    ).execute()

    messages = []

    for msg in thread.get("messages", []):

        headers = msg["payload"]["headers"]

        subject = ""
        sender = ""

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            if h["name"] == "From":
                sender = h["value"]

        snippet = msg.get("snippet", "")

        messages.append({
            "subject": subject,
            "sender": sender,
            "body": snippet
        })

    return {"thread": messages}

