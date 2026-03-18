import streamlit as st
from api_client import search_emails
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MailMentor AI",
    layout="wide"
)


# SESSION STATE

if "token" not in st.session_state:
    st.session_state.token = None



# AUTH FUNCTIONS

def login(username, password):
    try:
        res = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )

        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    except Exception as e:
        st.error(f"Login error: {e}")


def logout():
    st.session_state.token = None
    st.rerun()


def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}



# LOGIN SCREEN

if not st.session_state.token:

    st.title("MailMentor Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        login(username, password)

    st.stop()



# FETCH EMAILS (AUTH)

@st.cache_data(ttl=60)
def get_latest_emails():
    try:
        res = requests.get(
            f"{API_URL}/analytics/",
            headers=get_headers()
        )
        res.raise_for_status()
        return res.json().get("latest", [])
    except:
        return []



# UI

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

st.title("MailMentor AI Assistant")
st.caption("AI-powered Email Intelligence Dashboard")



# SIDEBAR

with st.sidebar:

    st.success("Logged in")

    if st.button("Logout"):
        logout()

    st.header("Filters")

    filter_type = st.radio(
        "Email Type",
        ["All", "Job", "Meeting", "Invoice"],
        horizontal=True
    )

    if st.button("Refresh Emails"):
        with st.spinner("Refreshing..."):
            requests.get(
                f"{API_URL}/emails/fetch",
                headers=get_headers()
            )
            st.success("Updated!")
            st.rerun()



# IMPORTANT EMAILS

latest_emails = get_latest_emails()

priority_emails = [
    e for e in latest_emails
    if e.get("priority") == "Important"
]

if priority_emails:

    st.markdown("## 🚨 Important Emails")

    with st.expander(f"View {len(priority_emails)} important emails"):

        for email in priority_emails:
            st.markdown(
                f"""
                **{email['subject']}**  
                <small>From: {email['sender']}</small>
                """,
                unsafe_allow_html=True
            )
            st.divider()



# AI WORKSPACE

st.markdown("## 🤖 MailMentor AI Workspace")

query = st.text_input(
    "Ask anything about your inbox",
    placeholder="Example: Update me about latest job opportunities"
)

if query:

    with st.spinner("Generating smart summary..."):

        res = requests.get(
            f"{API_URL}/search",
            params={"q": query + f" type:{filter_type}"},
            headers=get_headers()
        )

        data = res.json()

        st.subheader("Smart Inbox Summary")
        st.info(data.get("answer", ""))

        st.subheader("Results")

        for r in data.get("results", []):
            st.write(r["content"])
            st.caption(r["created_at"])
            st.divider()