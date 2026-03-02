from groq import Groq   # or your LLM client
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_ai_insights(stats):

    prompt = f"""
You are an analytics assistant.

Generate short business-style insights from this email data:

Total Emails: {stats['total']}
Categories: {stats['categories']}
Jobs: {stats['jobs']}
Finance: {stats.get('finance',0)}
Important: {stats['important']}

Return 4 concise bullet insights.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content