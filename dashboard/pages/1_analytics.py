import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="MailMentor Elite Analytics")

API_URL = "http://localhost:8000"


# DATE FILTER

days_filter = st.selectbox(
    "Filter Emails (by day)",
    [1, 3, 7, 14, 30],
    index=2
)

def get_analytics(days):

    try:
        res = requests.get(f"{API_URL}/analytics/?days={days}")
        res.raise_for_status()
        return res.json()

    except Exception as e:
        st.error(f"API Error: {e}")
        return {}

data = get_analytics(days_filter)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

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
    actions_res = requests.get(f"{API_URL}/actions")
    actions_data = actions_res.json().get("actions", [])
except:
    actions_data = []

if actions_data:

    for task in actions_data:

        col1, col2 = st.columns([4,1])

        with col1:
            st.markdown(f"**{task['subject']}**")
            st.caption(
                f"{task['sender']} | Action: {task['action']} | Deadline: {task['deadline'] or 'N/A'}"
            )

        with col2:

            if not task["is_completed"]:
                if st.button("Done", key=f"done_{task['email_id']}"):

                    requests.post(
                        f"{API_URL}/actions/complete/{task['email_id']}"
                    )

                    st.success("Marked Done")
                    st.rerun()   # instant refresh

            else:
                st.success("Completed")

        st.divider()

else:
    st.info("No action items found.")


# TREND SECTION

left = st.container()

# TREND GRAPH
with left:
    st.subheader("Weekly Email Trend")

    trend = data.get("trend", [])

    if trend:

        trend_df = pd.DataFrame(trend)

        # convert to datetime
        trend_df["day"] = pd.to_datetime(trend_df["day"])

        # sort by actual date
        trend_df = trend_df.sort_values("day")

        # keep date as index (important)
        trend_df = trend_df.set_index("day")

        st.line_chart(
            trend_df["count"],
            width="stretch"
        )

    else:
        st.info("No trend data available.")

st.divider()

# EMAIL CATEGORY

st.subheader("Email Category Distribution")

categories = data.get("categories", {})

if categories:

    cat_df = pd.DataFrame(
        list(categories.items()),
        columns=["Category", "Count"]
    )

    st.bar_chart(
        cat_df.set_index("Category"),
        # use_container_width=True
        width='stretch'
    )

else:
    st.info("No category data available.")

def get_email_summary(email_id):
    
    try:
        res = requests.get(
            f"{API_URL}/analytics/gmail-summary/{email_id}"
        )
        res.raise_for_status()
        return res.json().get("summary", "No summary")
    
    except Exception as e:
        return f"Summary error: {e}"


# SPLIT IMPORTANT AND NORMAL EMAILS

important_emails = [e for e in latest if e.get("priority") == "Important"]
normal_emails = [e for e in latest if e.get("priority") != "Important"]


# IMPORTANT EMAILS

if important_emails:

    st.markdown("## 🚨 Important Emails")

    with st.expander(f"View {len(important_emails)} important emails", expanded=True):

        for email in important_emails:

            st.markdown(
                f"""
                <div style="border-left:6px solid red;padding:10px;background:#2a1a1a">
                🚨 <b>{email['subject']}</b><br>
                From: {email['sender']}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.caption(
                f"From: {email['sender']} | Category: {email.get('category','General')}"
            )

            if st.button("Summarize Email", key=f"imp_{email['id']}"):

                with st.spinner("Generating AI summary..."):
                    summary = get_email_summary(email["id"])

                st.info(summary)
                
            # THREAD VIEW
            if st.button("View Thread", key=f"thread_{email['id']}"):
                
                if email.get("thread_id"):
                    
                    thread_res = requests.get(
                        f"{API_URL}/emails/thread/{email['thread_id']}"
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



# NORMAL LATEST EMAILS

st.subheader("Latest Emails")

if normal_emails:

    for email in normal_emails:

        st.markdown(f"##### {email['subject']}")

        st.caption(
            f"From: {email['sender']} | Category: {email.get('category','General')}"
        )

        if st.button("Summarize Email", key=f"norm_{email['id']}"):

            with st.spinner("Generating AI summary..."):
                summary = get_email_summary(email["id"])

            st.info(summary)

        st.divider()

else:
    st.info("No recent emails available.")