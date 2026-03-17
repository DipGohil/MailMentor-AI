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
    "submit",
    "do not fail",
    "tomorrow",
]

URGENT_CONTEXT = """
urgent meeting deadline action required
respond immediately important update
project discussion approval request
schedule call join meeting tomorrow
please review immediately submit report
critical update response required
"""

# Precompute normalized vector
def normalize(v):
    return v / np.linalg.norm(v)

urgent_vector = normalize(np.array(generate_embedding(URGENT_CONTEXT)))


def cosine_similarity(a, b):
    a = normalize(np.array(a))
    return np.dot(a, b)


def detect_priority(text):

    text_lower = text.lower()

    # STEP 1: Strong keyword shortcut (FAST)
    for word in IMPORTANT_KEYWORDS:
        if word in text_lower:
            return "Important"

    # STEP 2: Semantic similarity
    try:
        email_vector = generate_embedding(text[:500])
        similarity = cosine_similarity(email_vector, urgent_vector)

    except:
        similarity = 0

    # Threshold tuned for embeddings
    if similarity > 0.75:
        return "Important"

    return "Normal"