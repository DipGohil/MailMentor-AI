from app.dependencies import SessionLocal
from app.models.email_model import Email
from app.rag.vector_store import search_email_vectors
from app.rag.llm import generate_answer
import re
from datetime import datetime

MAX_EMAILS = 4
MAX_CHARS_PER_EMAIL = 700

# SMART CLEAN TEXT

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

# CLEAN CONTEXT BUILDER

def clean_context(results):

    context = []

    for r in results[:MAX_EMAILS]:

        content = smart_clean_text(r["content"])
        created_at = r.get("created_at", "unknown")

        context.append(
            f"""
Date: {created_at}
Content: {content}
"""
        )

    return "\n\n".join(context)


# GET LATEST EMAILS FROM DB

def get_latest_from_db(limit=3):

    db = SessionLocal()

    emails = (
        db.query(Email)
        .order_by(Email.created_at.desc())
        .limit(limit)
        .all()
    )

    results = []

    for e in emails:
        results.append({
            "content": f"{e.subject}. {e.body}",
            "created_at": str(e.created_at)
        })

    db.close()
    return results



# MAIN SEARCH FUNCTION

def search_emails(query: str):

    query_lower = query.lower()

    # --------- LATEST LOGIC ----------
    if "latest" in query_lower or "recent" in query_lower:

        match = re.search(r"\d+", query_lower)
        limit = int(match.group()) if match else 3

        results = get_latest_from_db(limit)

    # SEMANTIC SEARCH
    else:
        results = search_email_vectors(query, n_results=5)

    # BUILD CONTEXT
    context = clean_context(results)

    today = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""
You are MailMentor AI — an executive email assistant.

Today date is {today}.

Give SHORT practical summaries.

- 3 to 6 bullet points
- Each bullet 1-2 lines
- No storytelling
- Use ONLY provided context
"""

    answer = generate_answer(system_prompt + query, context)

    return {
        "answer": answer,
        "results": results[:MAX_EMAILS]
    }