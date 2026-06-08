import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
from calendar_tools import create_calendar_event
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------- UI CONFIG ----------
st.set_page_config(
    page_title=" Meeting Coordinator",
    page_icon="📅",
    layout="centered"
)

st.title("📅  Meeting Coordinator")
st.caption("Agentic AI system that schedules meetings intelligently")

st.divider()

# ---------- USER INPUT ----------
meeting_topic = st.text_input("📝 Meeting Topic", placeholder="Project discussion")

emails = st.text_area(
    "📧 Attendees Email IDs ",
    placeholder="abc@gmail.com, xyz@gmail.com"
)

meeting_date = st.date_input("📆 Meeting Date")
meeting_time = st.time_input("⏰ Meeting Time")

duration = st.slider("⏳ Duration (minutes)", 15, 180, 60)

st.divider()

# ---------- AGENT LOGIC ----------
if st.button("🤖 Schedule"):
    if not meeting_topic or not emails:
        st.error("Please fill all required fields")
    else:
        with st.spinner("Thinking like an AI agent..."):
            # Convert to datetime
            start_datetime = datetime.combine(meeting_date, meeting_time)

            # ✅ STRICT prompt to avoid long explanations
            prompt = f"""
Rewrite the following meeting title professionally.
Return ONLY one short improved title.
No explanation.
No bullet points.
No multiple options.
Maximum 8 words.

Title: "{meeting_topic}"
"""

            try:
                response = model.generate_content(prompt)
                
                # Extra safety: take only first line
                ai_title = response.text.strip().split("\n")[0]

                # Fallback if AI gives empty response
                if not ai_title:
                    ai_title = meeting_topic.strip()

            except Exception:
                # Fallback if Gemini fails
                ai_title = meeting_topic.strip()

            # Clean email list
            attendee_list = [
                email.strip()
                for email in emails.split(",")
                if email.strip()
            ]

            try:
                event = create_calendar_event(
                    title=ai_title,
                    attendees=attendee_list,
                    start_time=start_datetime,
                    duration_minutes=duration
                )

                st.success("✅ Meeting Scheduled Successfully!")
                st.write("### 📌 Final Meeting Title")
                st.info(ai_title)

                st.write("### 🔗 Calendar Event Link")
                st.markdown(event.get("htmlLink"))

            except Exception as e:
                st.error("Failed to create meeting")
                st.code(str(e))