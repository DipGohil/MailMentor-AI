# MailMentor AI — Intelligent Email Assistant

![CI](https://github.com/DipGohil/MailMentor-AI/actions/workflows/ci.yml/badge.svg)

MailMentor AI is a **production-ready AI-powered Email Intelligence Platform** that transforms your inbox into actionable insights using **Machine Learning, NLP, and RAG (Retrieval-Augmented Generation)**.

It enables users to **analyze, prioritize, summarize, and interact with emails intelligently**.

---

# 🌟 Key Highlights

* 🔐 Secure JWT-based Authentication
* 📬 Gmail Integration with Incremental Sync
* 🧠 ML-based Email Categorization (Scikit-learn)
* ⚡ Action Item Extraction (spaCy + NLP)
* 🧾 AI-powered Email Summarization
* 🔎 Semantic Search using RAG + Vector DB
* 📊 Executive Analytics Dashboard (Streamlit)
* ✅ CI/CD Pipeline with GitHub Actions
* 🧪 Full API Testing with Pytest

---

# 🧠 Core Features

## 📥 Gmail Integration

* OAuth-based secure access
* Strict 1-to-1 account mapping (One Login = One Gmail)
* Incremental email syncing using `historyId`
* Duplicate-safe ingestion

## 🤖 AI Intelligence Layer

* ML-based email categorization (replaces rule-based system)
* Smart priority detection using embeddings
* AI-generated summaries
* Semantic understanding via vector embeddings

## 🎯 Action Extraction (NLP)

* Detects actionable tasks from emails
* Deadline extraction using spaCy
* Mark tasks as completed (dashboard support)

## 🔍 RAG-based Smart Search

* Ask questions like:

  > “Show me latest job opportunities”
* Combines:

  * Keyword search
  * Semantic vector search
  * LLM-generated responses

## 📊 Analytics Dashboard

* Email trends over time
* Category distribution
* Important email tracking
* Thread-level visibility
* Action tracking UI

---

# 🏗️ System Architecture

```
Gmail API → Ingestion → PostgreSQL → Vector DB (Chroma)
                         ↓
                ML + NLP Processing
                         ↓
        FastAPI Backend (Secure APIs)
                         ↓
          Streamlit Dashboard UI
```

---

# 🛠️ Tech Stack

## 🔹 Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* JWT Authentication

## 🔹 AI / ML

* Scikit-learn (Classification)
* spaCy (NLP)
* Sentence Transformers (Embeddings)
* Groq / LLaMA (LLM)
* RAG Pipeline

## 🔹 Vector DB

* ChromaDB

## 🔹 Frontend

* Streamlit

## 🔹 DevOps

* Pytest
* GitHub Actions (CI/CD)

---

# 📁 Project Structure

```
app/
 ├── api/              # Routes (Auth, Email, Analytics, Search, Actions)
 ├── services/         # Business logic
 ├── ingestion/        # Gmail ingestion
 ├── rag/              # RAG + LLM logic
 ├── ml/               # ML models
 ├── models/           # DB models
 ├── schemas/          # Pydantic schemas
 └── main.py

dashboard/
 ├── app.py
 └── pages/

tests/
 ├── test_auth.py
 ├── test_actions.py
 ├── test_analytics.py
 ├── test_email.py
 ├── test_search.py
 └── test_summary.py
```

---

# ⚙️ Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone https://github.com/DipGohil/MailMentor-AI
cd MailMentor
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create `.env` file:

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GROQ_API_KEY=your_api_key
```

---

## 5️⃣ Run Backend

```bash
uvicorn app.main:app --reload
```

📍 API: http://localhost:8000

---

## 6️⃣ Run Dashboard

```bash
streamlit run dashboard/app.py
```

📍 UI: http://localhost:8501

---

# 🔐 Authentication & Account Management Flow

```
User Login → JWT Token → Stored in Session → Sent in Headers → Secure API Access
```

✔ Strict Account Management:
* Users can only connect to one unique Gmail account.
* Database tracks connected Gmails to prevent multiple users from linking the same account.

✔ Protected Endpoints:

* `/emails/fetch`
* `/emails/thread/{thread_id}`
* `/search`
* `/analytics`
* `/analytics/gmail-summary/{message_id}`
* `/analytics/email/{message_id}`
* `/summary`
* `/actions`
* `/actions/complete/{email_id}`
* `/email-summary/{email_id}`

---

# 🧪 Testing & CI/CD

## Run Tests Locally

```bash
python -m pytest -v
```

## CI/CD

* Automated testing via GitHub Actions
* Runs on every push
* Uses SQLite fallback for CI

---

# 📌 Key Engineering Decisions

* ✅ Strict 1-to-1 Gmail mapping (prevents account reuse across multiple logins)
* ✅ Replaced rule-based categorization with ML classifier
* ✅ Implemented RAG for intelligent search
* ✅ Used spaCy for structured NLP extraction
* ✅ Designed CI-safe architecture (mocked external APIs)
* ✅ Secure APIs with JWT authentication

---

# 🚀 Future Enhancements

* Role-based access control (Admin/User)
* Real-time email sync (webhooks)
* Notification system
* LLM fine-tuning
* Docker + Cloud Deployment

---

# 👨‍💻 Author

**Dip Gohil**
AI/ML Developer

---

# ⭐ If you like this project

Give it a ⭐ on GitHub and share 🚀
