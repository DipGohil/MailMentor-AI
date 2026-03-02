import os
import json

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    
    creds = None
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )
    
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )
    
        creds = flow.run_local_server(port = 0)
        
        with open("token.json", "w") as token:
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
