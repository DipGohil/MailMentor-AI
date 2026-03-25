from app.services.email_service import fetch_and_store_emails

result = fetch_and_store_emails(app_username="manual_test", limit=5)

print(result)