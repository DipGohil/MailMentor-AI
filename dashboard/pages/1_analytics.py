import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="MailMentor Elite Analytics")

API_URL = "http://localhost:8000"


# AUTH CHECK

if "token" not in st.session_state or not st.session_state.token:
    st.warning("Please login first")
    st.stop()

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# UI

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

# DATE FILTER

days_filter = st.selectbox(
    "Filter Emails (by day)",
    list(range(1, 16)), # 1-15 days
    index=6  # default = day-7
)


def get_analytics(days):
    try:
        res = requests.get(
            f"{API_URL}/analytics/?days={days}",
            headers=get_headers()
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return {}


data = get_analytics(days_filter)



# KPI DATA

categories = data.get("categories", {})
latest = data.get("latest", [])
total = data.get("total", 0)
jobs = data.get("jobs", 0)
important = data.get("important", 0)
meetings = data.get("meetings", 0)
finance = data.get("finance", 0)



# HEADER

st.title("MailMentor Elite Analytics")
st.caption("AI-powered Executive Email Intelligence")



# KPI SECTION

st.markdown("### Executive KPIs")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Emails", total)
k2.metric("Job Opportunities", jobs)
k3.metric("Important Emails", important)
k4.metric("Meetings", meetings)
k5.metric("Finance", finance)

st.divider()



# ACTION DASHBOARD

st.markdown("## Action Required")

try:
    actions_res = requests.get(
        f"{API_URL}/actions",
        headers=get_headers()
    )
    actions_data = actions_res.json().get("actions", [])
except:
    actions_data = []

if actions_data:

    for task in actions_data:

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"**{task['subject']}**")
            st.caption(
                f"{task['sender']} | Action: {task['action']} | Deadline: {task['deadline'] or 'N/A'}"
            )

        with col2:
            if not task["is_completed"]:
                if st.button("Done", key=f"done_{task['email_id']}"):

                    requests.post(
                        f"{API_URL}/actions/complete/{task['email_id']}",
                        headers=get_headers()
                    )

                    st.success("Marked Done")
                    st.rerun()
            else:
                st.success("Completed")

        st.divider()

else:
    st.info("No action items found.")



# TREND GRAPH

st.subheader("Weekly Email Trend")

trend = data.get("trend", [])

if trend:
    trend_df = pd.DataFrame(trend)
    trend_df["day"] = pd.to_datetime(trend_df["day"])
    trend_df = trend_df.sort_values("day").set_index("day")

    st.line_chart(trend_df["count"], width="stretch")
else:
    st.info("No trend data available.")

st.divider()



# CATEGORY CHART

st.subheader("Email Category Distribution")

if categories:
    cat_df = pd.DataFrame(
        list(categories.items()),
        columns=["Category", "Count"]
    )
    st.bar_chart(cat_df.set_index("Category"), width="stretch")
else:
    st.info("No category data available.")



# SUMMARY FUNCTION

def get_email_summary(email_id):
    try:
        res = requests.get(
            f"{API_URL}/analytics/gmail-summary/{email_id}",
            headers=get_headers()
        )
        return res.json().get("summary", "No summary")
    except:
        return "Error fetching summary"



# EMAIL LISTS

important_emails = [e for e in latest if e.get("priority") == "Important"]
normal_emails = [e for e in latest if e.get("priority") != "Important"]



# IMPORTANT EMAILS

if important_emails:

    st.markdown("## 🚨 Important Emails")
    
    with st.expander(f"View {len(important_emails)} important emails", expanded=True):

        for email in important_emails:

            st.markdown(f"**{email['subject']}**")
            st.caption(f"{email['sender']}")

            if st.button("Summarize", key=f"imp_{email['id']}"):
                st.info(get_email_summary(email["id"]))

            if st.button("Thread", key=f"thread_{email['id']}"):

                if email.get("thread_id"):

                    res = requests.get(
                        f"{API_URL}/emails/thread/{email['thread_id']}",
                        headers=get_headers()
                    )

                    thread = res.json().get("thread", [])

                    for msg in thread:
                        st.markdown(f"**{msg['subject']}**")
                        st.caption(msg["sender"])
                        st.write(msg["body"])
                        st.divider()

            st.divider()



# NORMAL EMAILS

st.subheader("Latest Emails")

if normal_emails:

    for email in normal_emails:

        st.markdown(f"##### {email['subject']}")

        st.caption(
            f"From: {email['sender']} | Category: {email.get('category','General')}"
        )

        col1, col2 = st.columns(2)

        # SUMMARY BUTTON
        with col1:
            if st.button("Summarize Email", key=f"norm_{email['id']}"):
                with st.spinner("Generating AI summary..."):
                    summary = get_email_summary(email["id"])
                st.info(summary)

        # THREAD BUTTON (NEW)
        with col2:
            if st.button("View Thread", key=f"norm_thread_{email['id']}"):

                if email.get("thread_id"):

                    thread_res = requests.get(
                        f"{API_URL}/emails/thread/{email['thread_id']}",
                        headers=get_headers()
                    )

                    thread = thread_res.json().get("thread", [])

                    st.markdown("### Email Thread")

                    for msg in thread:
                        st.markdown(f"**{msg['subject']}**")
                        st.caption(msg["sender"])
                        st.write(msg["body"])
                        st.divider()
                else:
                    st.warning("Thread not available")

        st.divider()
