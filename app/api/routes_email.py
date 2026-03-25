import os
from fastapi import APIRouter, Depends
from app.services.email_service import fetch_and_store_emails
from app.dependencies import get_current_user
from app.ingestion.parser import extract_body
from app.ingestion.gmail_client import authenticate_gmail, has_gmail_token

router = APIRouter(
    prefix="/emails",
    tags=["Emails"]
)

@router.get("/fetch")
def fetch_emails(user = Depends(get_current_user)):
    
    if os.getenv("TESTING") == "1":
        return {"status": "skipped in test"}
    
    app_username = user.get("sub", "")
    result = fetch_and_store_emails(app_username=app_username, limit=500)
    
    return {
        "status": "success",
        "message": "emails fetched and stored",
        "data": result
    }

def get_gmail_service(app_username: str):
    return authenticate_gmail(app_username=app_username)


@router.get("/gmail/status")
def gmail_status(user = Depends(get_current_user)):
    app_username = user.get("sub", "")
    connected = has_gmail_token(app_username)
    if not connected:
        return {"connected": False, "email": None}

    try:
        service = authenticate_gmail(app_username=app_username)
        profile = service.users().getProfile(userId="me").execute()
        return {"connected": True, "email": profile.get("emailAddress")}
    except Exception:
        # token exists but may be invalid/expired
        return {"connected": False, "email": None}


@router.get("/gmail/connect")
def connect_gmail(user = Depends(get_current_user)):
    from fastapi import HTTPException
    from app.dependencies import SessionLocal
    from app.models.user_model import GmailConnection
    from app.ingestion.gmail_client import _token_path
    
    if os.getenv("TESTING") == "1":
        return {"status": "skipped in test"}

    app_username = user.get("sub", "")
    service = authenticate_gmail(app_username=app_username, force_reauth=True)
    
    try:
        profile = service.users().getProfile(userId="me").execute()
        email_address = profile.get("emailAddress")
        
        db = SessionLocal()
        existing = db.query(GmailConnection).filter(GmailConnection.email_address == email_address).first()
        
        if existing and existing.app_username != app_username:
            token_path = _token_path(app_username)
            if os.path.exists(token_path):
                os.remove(token_path)
            db.close()
            raise HTTPException(status_code=400, detail="This Gmail is already connected to another user.")
            
        if not existing:
            new_conn = GmailConnection(app_username=app_username, email_address=email_address)
            db.add(new_conn)
            db.commit()
            
        db.close()
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Failed to verify Gmail account.")
        
    return {"status": "connected"}

def extract_attachments(payload):
    attachments = []

    def walk_parts(parts):
        for part in parts:
            filename = part.get("filename", "")
            body = part.get("body", {})
            attachment_id = body.get("attachmentId")

            # Gmail attachment files usually have both filename + attachmentId
            if filename and attachment_id:
                attachments.append({
                    "filename": filename,
                    "mime_type": part.get("mimeType", ""),
                    "size": body.get("size", 0),
                    "attachment_id": attachment_id
                })

            nested_parts = part.get("parts", [])
            if nested_parts:
                walk_parts(nested_parts)

    walk_parts(payload.get("parts", []))
    return attachments


def find_attachment_meta(payload, target_attachment_id):
    def walk_parts(parts):
        for part in parts:
            body = part.get("body", {})
            if body.get("attachmentId") == target_attachment_id:
                return {
                    "filename": part.get("filename", ""),
                    "mime_type": part.get("mimeType", ""),
                    "size": body.get("size", 0)
                }
            nested = part.get("parts", [])
            if nested:
                found = walk_parts(nested)
                if found:
                    return found
        return None

    return walk_parts(payload.get("parts", [])) or {
        "filename": "",
        "mime_type": "application/octet-stream",
        "size": 0
    }


@router.get("/thread/{thread_id}")
def get_thread(thread_id: str, user = Depends(get_current_user)):

    # skip in test/CI
    if os.getenv("TESTING") == "1":
        return {'thread': []}
    
    app_username = user.get("sub", "")
    service = get_gmail_service(app_username)

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
        sent_at = next((h["value"] for h in headers if h["name"] == "Date"), "")

        body_text = extract_body(msg.get("payload", {})).strip() or msg.get("snippet", "")
        attachments = extract_attachments(msg.get("payload", {}))

        messages.append({
            "message_id": msg.get("id"),
            "subject": subject,
            "sender": sender,
            "sent_at": sent_at,
            "body": body_text,
            "attachments": attachments
        })

    return {"thread": messages}


@router.get("/attachment/{message_id}/{attachment_id}")
def get_attachment(message_id: str, attachment_id: str, user=Depends(get_current_user)):
    # skip in test/CI
    if os.getenv("TESTING") == "1":
        return {"status": "skipped in test"}

    app_username = user.get("sub", "")
    service = get_gmail_service(app_username)

    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    meta = find_attachment_meta(message.get("payload", {}), attachment_id)

    attachment = service.users().messages().attachments().get(
        userId="me",
        messageId=message_id,
        id=attachment_id
    ).execute()

    return {
        "filename": meta["filename"] or "attachment",
        "mime_type": meta["mime_type"] or "application/octet-stream",
        "size": meta["size"],
        "data": attachment.get("data", "")
    }

