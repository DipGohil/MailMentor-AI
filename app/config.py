import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

