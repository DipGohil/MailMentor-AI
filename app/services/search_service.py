from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.rag.vector_store import search_email_vectors
from app.rag.llm import generate_answer

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

import re
from datetime import datetime


MAX_EMAILS = 10
MAX_CHARS_PER_EMAIL = 700


# -----------------------------
# CLEAN EMAIL TEXT
# -----------------------------
def smart_clean_text(text: str):

    if not text:
        return ""

    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text)

    garbage_words = [
        "unsubscribe",
        "privacy policy",
        "view in browser",
        "copyright",
        "all rights reserved"
    ]

    lines = text.split(".")
    important_lines = []

    for line in lines:

        small = line.lower()

        if any(g in small for g in garbage_words):
            continue

        if len(line.strip()) > 20:
            important_lines.append(line.strip())

    cleaned = ". ".join(important_lines)

    return cleaned[:MAX_CHARS_PER_EMAIL]


# -----------------------------
# CONTEXT BUILDER
# -----------------------------
def clean_context(results):

    context = []

    limit = min(len(results), MAX_EMAILS)

    for r in results[:limit]:

        content = smart_clean_text(r["content"])
        created_at = r.get("created_at", "unknown")

        context.append(
            f"""
Date: {created_at}
Content: {content}
"""
        )

    return "\n\n".join(context)


# -----------------------------
# FETCH LATEST EMAILS FROM GMAIL
# -----------------------------
def get_latest_from_gmail(limit=10):

    creds = Credentials.from_authorized_user_file(
        "token.json",
        ["https://www.googleapis.com/auth/gmail.readonly"]
    )

    service = build("gmail", "v1", credentials=creds)

    response = service.users().messages().list(
        userId="me",
        maxResults=limit
    ).execute()

    messages = response.get("messages", [])

    results = []

    for m in messages:

        msg = service.users().messages().get(
            userId="me",
            id=m["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()

        headers = msg["payload"]["headers"]

        subject = ""
        sender = ""
        date = ""

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            if h["name"] == "From":
                sender = h["value"]
            if h["name"] == "Date":
                date = h["value"]

        results.append({
            "email_id": m["id"],
            "content": f"{subject}",
            "created_at": date
        })

    return results


# -----------------------------
# KEYWORD SEARCH (POSTGRES)
# -----------------------------
def keyword_search(query):

    db = SessionLocal()

    emails = (
        db.query(Email)
        .filter(
            Email.subject.ilike(f"%{query}%") |
            Email.body.ilike(f"%{query}%")
        )
        .order_by(Email.created_at.desc())
        .limit(5)
        .all()
    )

    db.close()

    results = []

    for e in emails:
        results.append({
            "email_id": e.id,
            "content": f"{e.subject}. {e.body}",
            "created_at": str(e.created_at)
        })

    return results


# -----------------------------
# PRIORITY SCORING
# -----------------------------
priority_keywords = [
    "urgent",
    "deadline",
    "asap",
    "important",
    "meeting",
    "action required"
]


def score_email(email):

    text = email["content"].lower()

    score = 0

    for word in priority_keywords:
        if word in text:
            score += 2

    return score


# -----------------------------
# MAIN SEARCH FUNCTION
# -----------------------------
def search_emails(query: str):

    query_lower = query.lower()

    # Detect "latest emails" query
    if "latest" in query_lower or "recent" in query_lower:

        match = re.search(r"\d+", query_lower)
        limit = int(match.group()) if match else 5

        results = get_latest_from_gmail(limit)

    else:

        # keyword search
        keyword_results = keyword_search(query)

        # semantic search
        semantic_results = search_email_vectors(query, n_results=5)

        results = keyword_results + semantic_results

        # remove duplicates
        seen = set()
        unique_results = []

        for r in results:
            if r["email_id"] not in seen:
                unique_results.append(r)
                seen.add(r["email_id"])

        # prioritize urgent emails
        results = sorted(
            unique_results,
            key=score_email,
            reverse=True
        )

    # build LLM context
    context = clean_context(results)

    today = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""
You are MailMentor AI — an executive email assistant.

Today is {today}.

Your job is to summarize inbox activity clearly and professionally.

STYLE RULES:
• Write like a professional executive assistant.
• Do NOT repeat timestamps unless important.
• Focus on the main intent of each email.

FORMAT:
• Use 3 to 5 concise bullet points.
• Each bullet should represent one key insight.
• Each bullet must be on new line.
• Keep the tone readable and chatGPT style.

IMPORTANT:
Use ONLY the provided email context.
Do NOT invent information.
"""

    answer = generate_answer(system_prompt + query, context)

    return {
        "answer": answer,
        "results": results[:MAX_EMAILS]
    }