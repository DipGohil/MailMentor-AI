# MailMentor AI

MailMentor AI is an **AI-powered Email Intelligence Platform** built with FastAPI, Streamlit, PostgreSQL, and RAG architecture.

It helps users:

* Fetch Gmail emails automatically
* Categorize emails using AI
* Generate smart summaries
* View analytics & insights
* Ask questions over recent emails (RAG-based)

---

## Features

### Gmail Integration

* OAuth authentication
* Fetch latest emails securely
* Avoid duplicate inserts

### AI Intelligence

* Email categorization
* AI summaries
* Insights generation
* Semantic search using vector embeddings

### Analytics Dashboard

* Total emails
* Category distribution
* Latest emails
* Executive metrics

### RAG Search

* Ask natural language queries
* Retrieval-augmented generation over emails

---

## Tech Stack

**Backend**

* FastAPI
* SQLAlchemy
* PostgreSQL
* ChromaDB (Vector DB)

**AI / ML**

* LLM (Groq / Llama)
* Embeddings
* RAG Pipeline

**Frontend**

* Streamlit Dashboard

---

## Project Structure

```
app/
 ├── api/
 ├── services/
 ├── ingestion/
 ├── rag/
 ├── models/
 ├── schemas/
 └── main.py

dashboard/
 ├── app.py
 └── pages/
```

---

## Setup Instructions

### 1. Clone Project

```bash
git clone https://github.com/DipGohil/MailMentor-AI
cd MailMentor
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

### 5. Start Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard runs at:

```
http://localhost:8501
```

---

## Gmail OAuth Setup

1. Enable Gmail API in Google Cloud Console
2. Download `credentials.json`
3. Place inside project root
4. Run `/emails/fetch` endpoint once for authorization

---

## Main API Endpoints

| Endpoint        | Description         |
| --------------- | ------------------- |
| `/emails/fetch` | Fetch latest emails |
| `/analytics/`   | Email analytics     |
| `/search/`      | Ask questions (RAG) |
| `/insights/`    | AI insights         |
| `/summary/`     | Email summary       |

---

## Future Improvements

* Auto background email sync
* Executive UI redesign
* Smart notifications
* Email action automation

---

## Author

Dip Gohil
AI/ML Developer
