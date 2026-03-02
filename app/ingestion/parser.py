import base64
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
def decode_body(data):
    if not data:
        return ""
    
    decoded = base64.urlsafe_b64decode(data)
    return decoded.decode("utf-8", errors = "ignore")

def clean_html(html_content):
    
    #Convert HTML email into readable plain text
    
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # remove scripts/styles
    for tag in soup(["script", "style"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)

def extract_headers(headers):
    result = {}

    for h in headers:
        name = h["name"]
        
        if name == "From":
            result["sender"] = h["value"]
        
        elif name == "Subject":
            result["subject"] = h["value"]
        
        elif name == "Date":
            result["date"] = h["value"]
    
    return result
        
def extract_body(payload):

    # direct body
    body_data = payload.get("body", {}).get("data")
    if body_data:
        return decode_body(body_data)

    # multipart emails
    parts = payload.get("parts", [])

    for part in parts:

        mime_type = part.get("mimeType", "")

        # Plain text
        if mime_type == "text/plain":
            data = part.get("body", {}).get("data")
            if data:
                return decode_body(data)

        # HTML fallback
        if mime_type == "text/html":
            data = part.get("body", {}).get("data")
            if data:
                html = decode_body(data)
                return clean_html(html)

        # Nested parts
        if part.get("parts"):
            nested = extract_body(part)
            if nested:
                return nested

    return ""

def parse_email(message):
    
    payload = message.get("payload", {})
    headers = extract_headers(payload.get("headers", []))
    body = extract_body(payload)
    
    # Convert Gmail date → datetime
    date_str = headers.get("date", "")
    try:
        email_datetime = parsedate_to_datetime(date_str)
    except:
        email_datetime = datetime.now(timezone.utc)
    
    return {
        "gmail_id": message["id"],
        "thread_id": message["threadId"],
        "sender": headers.get("sender", ""),
        "subject": headers.get("subject", ""),
        # "date": headers.get("date", ""),
        "body": body,
        "created_at": email_datetime
    }