import requests

BASE_URL = "http://localhost:8000"

def search_emails(query):
    response = requests.get(
        f"{BASE_URL}/search/",
        params = {"q": query}
    )
    return response.json()

def get_email_summary(email_id):
    import requests

    res = requests.get(f"http://127.0.0.1:8000/email-summary/{email_id}")

    if res.status_code == 200:
        return res.json()["summary"]

    return "Unable to generate summary."
