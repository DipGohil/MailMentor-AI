from app.rag.vector_store import search_email_vectors
from app.rag.llm import generate_answer
import re
from datetime import datetime


# limit how much text goes to LLM
MAX_EMAILS = 4
MAX_CHARS_PER_EMAIL = 700

def smart_clean_text(text: str):
    """
    Smart compression of email content
    """

    if not text:
        return ""

    # 1️ remove urls (tracking links etc.)
    text = re.sub(r"http\S+", "", text)

    # 2️ remove extra spaces/new lines
    text = re.sub(r"\s+", " ", text)

    # 3️ remove long footer lines
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

        # skip garbage
        if any(g in small for g in garbage_words):
            continue

        # keep meaningful lines
        if len(line.strip()) > 20:
            important_lines.append(line.strip())

    cleaned = ". ".join(important_lines)

    # 4. final size control
    return cleaned[:MAX_CHARS_PER_EMAIL]


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

def search_emails(query: str):

    # vector search
    results = search_email_vectors(query, n_results = 5)
    # print("vector results:", results)

    # make SMALL context
    context = clean_context(results)
    
    today = datetime.now().strftime("%Y-%m-%d")

    # system_prompt = f"""
    # You are MailMentor AI — a smart, human-like email assistant.

    # Today date is {today}.
    
    # Write like ChatGPT assistant style — natural and concise.
    
    # STYLE RULES:
    # - Speak naturally like a helpful assistant.
    # - Summarize emails like a human would explain to a user.
    # - DO NOT list raw timestamps unless needed.
    # - Combine similar emails into one insight.
    # - Focus on meaning, not raw data.

    # BEHAVIOR:
    # - If user asks for latest emails → give a smooth narrative summary.
    # - Mention important themes, opportunities, or actions.
    # - Keep tone friendly and professional.

    # IMPORTANT:
    # - Use ONLY provided emails.
    # - Do NOT invent emails.
    # """
    
    system_prompt = f"""
You are MailMentor AI — an executive email assistant.

Today date is {today}.

GOAL:
Give SHORT, practical email summaries.

OUTPUT STYLE (VERY IMPORTANT):

OUTPUT STYLE:

- Write in SHORT readable sections.
- Use 3 to 6 bullet points.
- EACH bullet should be on a NEW LINE.
- Each bullet = 1 email or 1 major insight.
- Keep each bullet 1 to 2 lines max.
- Avoid long paragraphs.
- Avoid single-line compressed output.
- Total response should feel like a quick inbox briefing.
- No greetings or storytelling.

STRICT:
- Use ONLY provided email context.
- DO NOT invent emails.
"""

     # LLM answer
    answer = generate_answer(system_prompt + query, context)

    return {
        "answer": answer,
        "results": results[:MAX_EMAILS]
    }