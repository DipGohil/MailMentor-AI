from app.rag.embeddings import generate_embedding
import numpy as np

def categorize_email(subject: str):

    if not subject:
        return "General"
    
    s = subject.lower()

    # JOB / CAREER
    if any(word in s for word in [
        "job", "opening", "career", "recruiter",
        "intern", "apply", "hiring", "profile"
    ]):
        return "Job"

    # FINANCE
    if any(word in s for word in [
        "balance", "fund", "security", "payment",
        "invoice", "bank", "transaction"
    ]):
        return "Finance"

    # OTP / SECURITY
    if any(word in s for word in [
        "otp", "verification", "code",
        "security alert", "password"
    ]):
        return "Security"

    # PROMOTION / MARKETING
    if any(word in s for word in [
        "offer", "discount", "sale", "deal",
        "premium", "subscription"
    ]):
        return "Promotion"

    # MEETING / CALENDAR
    if any(word in s for word in [
        "meeting", "schedule", "calendar",
        "invite", "event"
    ]):
        return "Meeting"

    return "General"

IMPORTANT_KEYWORDS = [
    "urgent",
    "asap",
    "important",
    "deadline",
    "meeting",
    "action required",
    "immediate",
    "submit"
]

URGENT_CONTEXT = """
urgent meeting deadline action required
respond immediately project discussion
important update submit report
call tomorrow schedule meeting
"""

# Pre-compute semantic vector once
urgent_vector = generate_embedding(URGENT_CONTEXT)

# def detect_priority(text):

#     text_lower = text.lower()

#     # Keyword rule
#     for word in IMPORTANT_KEYWORDS:
#         if word in text_lower:
#             return "Important"

#     return "Normal"

def detect_priority(text):

    text_lower = text.lower()

    keyword_score = 0

    # KEYWORD SCORE
    for word in IMPORTANT_KEYWORDS:
        if word in text_lower:
            keyword_score += 1

    keyword_score = min(keyword_score / 2, 1)  # normalize


    # SEMANTIC SCORE
    try:
        email_vector = generate_embedding(text[:500])
        similarity = np.dot(email_vector, urgent_vector)

        semantic_score = float(similarity)

    except:
        semantic_score = 0


    # HYBRID SCORE
    final_score = (0.6 * keyword_score) + (0.4 * semantic_score)


    if final_score > 0.75:
        return "Important"

    return "Normal"