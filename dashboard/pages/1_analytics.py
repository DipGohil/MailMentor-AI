import streamlit as st
import requests
import pandas as pd
import base64
import re

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


def fetch_attachment(message_id, attachment_id):
    try:
        res = requests.get(
            f"{API_URL}/emails/attachment/{message_id}/{attachment_id}",
            headers=get_headers()
        )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Attachment fetch failed: {e}")
        return None


def to_standard_base64(data):
    # Gmail returns URL-safe base64, browsers expect standard base64 for data URLs.
    if not data:
        return ""
    converted = data.replace("-", "+").replace("_", "/")
    while len(converted) % 4 != 0:
        converted += "="
    return converted


def is_image_attachment(mime_type, filename):
    mt = (mime_type or "").lower()
    fn = (filename or "").lower()
    return (
        mt.startswith("image/")
        or fn.endswith(".png")
        or fn.endswith(".jpg")
        or fn.endswith(".jpeg")
        or fn.endswith(".gif")
        or fn.endswith(".webp")
        or fn.endswith(".bmp")
    )


def extract_drive_pdf_links(body_text):
    if not body_text:
        return []

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    links = []
    seen = set()

    for idx, line in enumerate(lines):
        urls = re.findall(r"https?://\S+", line)
        for url in urls:
            if "drive.google.com" not in url:
                continue
            if url in seen:
                continue

            seen.add(url)

            # Try to use nearest human-friendly PDF name above the link.
            filename = "Attachment.pdf"
            for back in range(idx, -1, -1):
                match = re.search(r"([^\s]+\.pdf)\b", lines[back], re.IGNORECASE)
                if match:
                    filename = match.group(1)
                    break

            links.append({
                "filename": filename,
                "url": url
            })

    return links


def clean_email_body_for_display(body_text):
    if not body_text:
        return ""

    # Remove raw URLs so thread looks cleaner like Gmail preview cards.
    cleaned = re.sub(r"https?://\S+", "", body_text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def render_thread(thread, key_prefix):
    st.markdown("### Email Thread")

    for idx, msg in enumerate(thread):
        with st.container(border=True):
            st.markdown(f"**{msg.get('subject', '(No Subject)')}**")
            st.caption(f"{msg.get('sender', 'Unknown sender')} | {msg.get('sent_at', '')}")
            body_text = msg.get("body", "")
            st.write(clean_email_body_for_display(body_text))

            attachments = msg.get("attachments", [])
            drive_pdf_links = extract_drive_pdf_links(body_text)

            if attachments:
                st.markdown("**Attachments**")

                for a_idx, attachment in enumerate(attachments):
                    filename = attachment.get("filename", "Unknown file")
                    mime_type = attachment.get("mime_type", "application/octet-stream")
                    attachment_id = attachment.get("attachment_id")
                    message_id = msg.get("message_id")

                    st.write(f"- {filename}")

                    if not attachment_id or not message_id:
                        continue

                    payload = fetch_attachment(message_id, attachment_id)
                    if not payload or not payload.get("data"):
                        st.caption("Attachment unavailable")
                        continue

                    raw_bytes = base64.urlsafe_b64decode(payload["data"] + "===")
                    resolved_mime = payload.get("mime_type", mime_type)

                    if is_image_attachment(resolved_mime, filename):
                        # Show image directly, no download button for image.
                        st.image(raw_bytes, caption=filename)
                    else:
                        st.download_button(
                            label=f"Download {filename}",
                            data=raw_bytes,
                            file_name=payload.get("filename", filename),
                            mime=resolved_mime,
                            key=f"{key_prefix}_save_{idx}_{a_idx}"
                        )

            if drive_pdf_links:
                st.markdown("**Shared Files**")
                for link in drive_pdf_links:
                    st.markdown(f"- [{link['filename']}]({link['url']})")



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
                    render_thread(thread, key_prefix=f"important_{email['id']}")

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
                    render_thread(thread, key_prefix=f"normal_{email['id']}")
                else:
                    st.warning("Thread not available")

        st.divider()
