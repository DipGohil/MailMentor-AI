import spacy
import re

# safe for CI pipeline
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# ACTION KEYWORDS
ACTION_VERBS = [
    "submit", "join", "review", "complete",
    "approve", "send", "update", "check",
    "schedule", "attend"
]

import re

def clean_email_text(text: str):

    if not text:
        return ""

    # remove HTML tags
    text = re.sub(r"<.*?>", " ", text)

    # remove URLs
    text = re.sub(r"http\S+", " ", text)

    # remove CSS-like patterns
    text = re.sub(r"\b\d+px\b", "", text)

    # remove large random numbers
    text = re.sub(r"\b\d{3,}\b", "", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

VALID_DEADLINE_WORDS = [
    "today", "tomorrow", "tonight",
    "next week", "next month",
    "monday", "tuesday", "wednesday",
    "thursday", "friday", "saturday", "sunday"
]

def is_valid_deadline(text):

    text = text.lower()

    # reject garbage
    if any(x in text for x in ["px", ";", "{", "}", "http"]):
        return False

    # reject pure numbers
    if text.strip().isdigit():
        return False

    # accept meaningful time words
    if any(word in text for word in VALID_DEADLINE_WORDS):
        return True

    # accept proper dates like "16 march"
    if re.search(r"\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", text):
        return True

    return False

def extract_action_and_deadline(text: str):

    text = clean_email_text(text)

    doc = nlp(text)

    action = None
    deadline = None

    # ACTION
    for token in doc:
        if token.lemma_.lower() in ACTION_VERBS:
            action = token.lemma_.lower()
            break

    # DEADLINE (spaCy)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            if is_valid_deadline(ent.text):   # FILTER
                deadline = ent.text.lower()
                break

    # REGEX fallback
    if not deadline:
        match = re.search(
            r"(today|tomorrow|next week|next month)",
            text.lower()
        )
        if match:
            deadline = match.group()

    if action:
        return {
            "action": action,
            "deadline": deadline
        }

    return None