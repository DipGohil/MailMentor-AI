from app.ingestion.gmail_client import authenticate_gmail, get_full_message
from app.ingestion.parser import parse_email

service = authenticate_gmail()

messages = service.users().messages().list(
    userId = "me",
    maxResults = 1
).execute().get("messages", [])

msg = get_full_message(service, messages[0]["id"])

parsed = parse_email(msg)

print(parsed)