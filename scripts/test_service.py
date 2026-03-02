from app.services.email_service import fetch_and_store_emails

result = fetch_and_store_emails(limit = 5)

print(result)