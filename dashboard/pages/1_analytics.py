import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide", page_title="MailMentor Elite Analytics")

API_URL = "http://localhost:8000"



# API CALL

def get_analytics():
    try:
        res = requests.get(f"{API_URL}/analytics/")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return {
            "total": 0,
            "jobs": 0,
            "important": 0,
            "latest": []
        }

data = get_analytics()

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

        # sort by real date
        trend_df = trend_df.sort_values("day")

        # create readable label
        trend_df["label"] = trend_df["day"].dt.strftime("%a")

        # use real date as index to keep correct order
        trend_df = trend_df.set_index("day")

        st.line_chart(
            trend_df["count"],
            # use_container_width=True
            width='stretch'
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


# LATEST EMAILS TABLE

# st.subheader("Latest Emails")

# if latest:

#     df_latest = pd.DataFrame(latest)

#     for _, row in df_latest.iterrows():

#         # SMALL TITLE STYLE
#         if row.get("priority") == "Important":

#             st.markdown(
#                 f"""
#                 <div style="border-left:6px solid red;padding:10px;background:#2a1a1a">
#                 🚨 <b>{row['subject']}</b><br>
#                 From: {row['sender']}
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )

#         else:

#             st.markdown(f"##### {row['subject']}")

#         st.caption(
#             f"From: {row['sender']} | Category: {row.get('category','General')}"
#         )

#     # FULL WIDTH BUTTON
#         if st.button("Summarize Email", key=f"sum_{row['id']}"):

#             with st.spinner("Generating AI summary..."):
#                 summary = get_email_summary(row["id"])

#             # SUMMARY BELOW (clean UI)
#             st.info(summary)

#         st.divider()

# else:
#     st.info("No recent emails available.")


# SPLIT IMPORTANT AND NORMAL EMAILS

important_emails = [e for e in latest if e.get("priority") == "Important"]
normal_emails = [e for e in latest if e.get("priority") != "Important"]


# IMPORTANT EMAILS (EXPANDABLE)

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