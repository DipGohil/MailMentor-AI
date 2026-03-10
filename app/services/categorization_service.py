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
]

def detect_priority(text):

    text = text.lower()

    for word in IMPORTANT_KEYWORDS:
        if word in text:
            return "Important"

    return "Normal"