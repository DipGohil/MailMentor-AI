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


def register(username, password, confirm_password):
    if not username or not password:
        st.error("Username and password are required")
        return

    if password != confirm_password:
        st.error("Passwords do not match")
        return

    try:
        res = requests.post(
            f"{API_URL}/auth/register",
            json={"username": username, "password": password}
        )

        if res.status_code == 200:
            st.success("Registration successful. Please sign in.")
        elif res.status_code == 400:
            st.error("Username already exists")
        else:
            st.error("Registration failed")

    except Exception as e:
        st.error(f"Registration error: {e}")


def logout():
    st.session_state.token = None
    st.rerun()


def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def get_gmail_status():
    try:
        res = requests.get(
            f"{API_URL}/emails/gmail/status",
            headers=get_headers()
        )
        if res.status_code == 200:
            data = res.json()
            return {
                "connected": data.get("connected", False),
                "email": data.get("email")
            }
    except Exception:
        pass
    return {"connected": False, "email": None}


def connect_gmail():
    try:
        res = requests.get(
            f"{API_URL}/emails/gmail/connect",
            headers=get_headers()
        )
        if res.status_code == 200:
            st.success("Gmail connected successfully")
            st.rerun()
        else:
            st.error("Unable to connect Gmail")
    except Exception as e:
        st.error(f"Gmail connect failed: {e}")



# LOGIN SCREEN

if not st.session_state.token:

    st.title("MailMentor")
    st.caption("Secure access to your AI email workspace")

    signin_tab, register_tab = st.tabs(["Sign In", "Register"])

    with signin_tab:
        st.subheader("Welcome back")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Sign In", key="signin_btn"):
            login(username, password)

    with register_tab:
        st.subheader("Create account")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm password", type="password", key="register_confirm_password")

        if st.button("Create Account", key="register_btn"):
            register(new_username, new_password, confirm_password)

    st.stop()



# FETCH EMAILS (AUTH)

@st.cache_data(ttl=60)
def get_latest_emails(token: str):
    try:
        res = requests.get(
            f"{API_URL}/analytics/",
            headers={"Authorization": f"Bearer {token}"}
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

    st.header("Gmail Account")
    gmail_status = get_gmail_status()
    gmail_connected = gmail_status.get("connected", False)
    gmail_email = gmail_status.get("email")

    if gmail_connected:
        st.success("Gmail connected")
        if gmail_email:
            st.caption(f"Connected as: {gmail_email}")
        if st.button("Switch Gmail Account"):
            connect_gmail()
    else:
        st.warning("Gmail not connected")
        if st.button("Connect Gmail Account"):
            connect_gmail()

    st.header("Filters")

    filter_type = st.radio(
        "Email Type",
        ["All", "Job", "Meeting", "Invoice"],
        horizontal=True
    )

    if st.button("Refresh Emails"):
        with st.spinner("Refreshing..."):
            if not gmail_connected:
                st.warning("Connect Gmail first")
            else:
                requests.get(
                    f"{API_URL}/emails/fetch",
                    headers=get_headers()
                )
                st.success("Updated!")
                st.rerun()



# IMPORTANT EMAILS

latest_emails = get_latest_emails(st.session_state.token)

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