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



# HEADER

st.title("MailMentor Elite Analytics")
st.caption("AI-powered Executive Email Intelligence")



# KPI SECTION

st.markdown("### Executive KPIs")

k1, k2, k3 = st.columns(3)

k1.metric("Total Emails", total)
k2.metric("Job Opportunities", jobs)
k3.metric("Important Emails", important)

st.divider()


# ALERTS + TREND SECTION

left = st.container()

# TREND GRAPH
with left:
    st.subheader("Weekly Email Trend")

    trend_df = pd.DataFrame({
        "Day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        "Emails": [
            max(total-6, 0),
            max(total-5, 0),
            max(total-4, 0),
            max(total-3, 0),
            max(total-2, 0),
            max(total-1, 0),
            total
        ]
    })

    st.line_chart(trend_df.set_index("Day"))

st.divider()

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

st.subheader("Latest Emails")

if latest:

    df_latest = pd.DataFrame(latest)

    for _, row in df_latest.iterrows():

        # SMALL TITLE STYLE
        if row.get("priority") == "Important":

            st.markdown(
                f"""
                <div style="border-left:6px solid red;padding:10px;background:#2a1a1a">
                🚨 <b>{row['subject']}</b><br>
                From: {row['sender']}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(f"##### {row['subject']}")

        st.caption(
            f"From: {row['sender']} | Category: {row.get('category','General')}"
        )

    # FULL WIDTH BUTTON
        if st.button("Summarize Email", key=f"sum_{row['id']}"):

            with st.spinner("Generating AI summary..."):
                summary = get_email_summary(row["id"])

            # SUMMARY BELOW (clean UI)
            st.info(summary)

        st.divider()

else:
    st.info("No recent emails available.")