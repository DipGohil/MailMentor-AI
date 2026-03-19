import os
from dotenv import load_dotenv
try:
    from groq import Groq
except ImportError:
    Groq = None

# Load .env variables
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer(query, context):
    
    if Groq is None:
        return "LLM not available in test environment"

    prompt = f"""
Answer user question using ONLY given emails.

Emails:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].message.content