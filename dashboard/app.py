import streamlit as st
from api_client import search_emails
import requests

API_URL = "http://localhost:8000"

def get_latest_emails():

    try:
        res = requests.get(f"{API_URL}/analytics/")
        res.raise_for_status()

        data = res.json()

        return data.get("latest", [])

    except:
        return []

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
            
latest_emails = get_latest_emails()
            
priority_emails = [
    e for e in latest_emails
    if e.get("priority") == "Important"
][:5] # Limits to show only 5

# if priority_emails:

#     st.markdown("## 🚨 Important Emails")

#     for email in priority_emails:

#         st.markdown(
#             f"""
#             <div style="border-left:6px solid red;padding:12px;background:#2a1a1a;border-radius:6px;margin-bottom:10px">
#             <b>{email['subject']}</b><br>
#             <small>From: {email['sender']}</small>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

if priority_emails:

    st.markdown("## 🚨 Important Emails")

    with st.expander(f"View {len(priority_emails)} important emails", expanded=False):

        for email in priority_emails:

            col1, col2 = st.columns([4,1])

            with col1:
                st.markdown(
                    f"""
                    **{email['subject']}**  
                    <small>From: {email['sender']}</small>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("Open", key=email["id"]):
                    st.session_state["opened_email_id"] = email["id"]
                    
            if st.session_state.get("opened_email_id") == email["id"]:

                res = requests.get(
                    f"{API_URL}/analytics/email/{email['id']}"
                )

                if res.status_code == 200:

                    data = res.json()

                    st.markdown(
                        f"""
                        <div style="background:#111827;padding:15px;border-radius:8px;margin-top:10px">

                        <b>Subject:</b> {data['subject']}<br>
                        <b>From:</b> {data['sender']}<br><br>

                        <b>Body:</b><br>
                        {data['body']}

                        </div>
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

