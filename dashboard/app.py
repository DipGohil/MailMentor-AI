import streamlit as st
from api_client import search_emails
import requests

API_URL = "http://localhost:8000"


def get_dashboard_stats():
    try:
        res = requests.get(f"{API_URL}/analytics/")
        res.raise_for_status()
        
        data = res.json()
        
        # st.write("DEBUG:", data)
        return data
    
    except Exception as e:
        st.error(f"API error: {e}")
        return {
            "total": 0,
            "important": 0,
            "jobs": 0,
            "meetings": 0,
            "finance": 0,
            "latest_days": "-"
        }

st.set_page_config(
    page_title="MailMentor AI",
    layout = "wide"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

st.title("MailMentor AI Assistant")
st.caption("AI-powered Email Intelligence Dashboard")

with st.sidebar:

    st.header("Filters")

    filter_type = st.radio(
        "Email Type",
        ["All", "Job", "Meeting", "Invoice"],
        horizontal=True
    )
    
    if st.button("Refresh Emails"):
        with st.spinner("refreshing.."):
            requests.get(f"{API_URL}/emails/fetch")
            st.success("Updated!")
            st.rerun()
    
st.markdown("## Mail Insights")

stats = get_dashboard_stats()

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    st.metric("Total Emails", stats["total"])

with col2:
    st.metric("Important", stats["important"])

with col3:
    st.metric("Job Related", stats["jobs"])

with col4:
    st.metric("Meetings", stats["meetings"])

with col5:
    st.metric("Finance", stats["finance"])

with col6:
    st.metric("Latest Mail (days ago)", stats.get("latest_days", "-")) 

# ===============================
# AI WORKSPACE (SINGLE OUTPUT)
# ===============================

st.markdown("## 🤖 MailMentor AI Workspace")

query = st.text_input(
    "Ask anything about your inbox",
    placeholder="Example: Update me about latest job opportunities"
)

if query:

    with st.spinner("Generating smart summary..."):

        # One unified backend request
        result = search_emails(
            query + f" type:{filter_type}"
        )

        final_summary = result.get("answer", "No summary generated")
        
        if result.get("emails"):
            st.subheader("Latest Emails")
            st.dataframe(result["emails"], use_container_width=True)

    st.subheader("Smart Inbox Summary")
    st.info(final_summary)

