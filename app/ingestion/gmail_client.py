import os
import re

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def _safe_user_key(app_username: str):
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", (app_username or "").strip())
    return cleaned or "default"


def _token_path(app_username: str):
    os.makedirs("tokens", exist_ok=True)
    return os.path.join("tokens", f"gmail_{_safe_user_key(app_username)}.json")


def has_gmail_token(app_username: str):
    return os.path.exists(_token_path(app_username))


def authenticate_gmail(app_username: str, force_reauth: bool = False):
    creds = None

    token_path = _token_path(app_username)

    if (not force_reauth) and os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(
            token_path,
            SCOPES
        )

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )

        creds = flow.run_local_server(port = 0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials = creds)

    return service

def get_full_message(service, message_id):
    msg = service.users().messages().get(
        userId = "me",
        id = message_id,
        format = "full"
    ).execute()
    return msg
