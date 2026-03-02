from app.rag.llm import generate_answer

def generate_email_summary(subject, body):

    prompt = (
        "Summarize this email in 2-3 bullet points "
        "for quick reading."
    )

    context = f"Subject: {subject}\nBody: {body}"

    return generate_answer(prompt, context)