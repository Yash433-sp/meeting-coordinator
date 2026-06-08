import os
import json
import dotenv
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta
from calendar_tools import create_calendar_event, list_upcoming_events

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class MeetingAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def parse_meeting_request(self, user_input):
        """Use Gemini to extract meeting details"""
        
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        prompt = f"""Extract meeting details from: "{user_input}"

Today is {today.strftime("%A, %B %d, %Y")}.
Tomorrow is {tomorrow.strftime("%A, %B %d, %Y")}.

Return ONLY valid JSON (no markdown, no extra text):
{{
    "title": "meeting title",
    "attendees": ["email@example.com"],
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "duration_minutes": 60
}}

Rules:
- If "tomorrow", use {tomorrow.strftime("%Y-%m-%d")}
- If "today", use {today.strftime("%Y-%m-%d")}
- If no title, use "Meeting"
- If no duration, use 60
- Time in 24-hour format (14:00 for 2pm)
- Return ONLY JSON"""

        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up markdown
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        
        # Extract JSON
        if "{" in response_text:
            response_text = response_text[response_text.index("{"):]
        if "}" in response_text:
            response_text = response_text[:response_text.rindex("}")+1]
        
        return json.loads(response_text)
    
    def schedule_meeting(self, user_input):
        """Schedule a meeting"""
        try:
            print("\n🤔 Understanding your request...")
            meeting_details = self.parse_meeting_request(user_input)
            
            print(f"\n📋 Extracted details:")
            print(f"   Title: {meeting_details['title']}")
            print(f"   Attendees: {', '.join(meeting_details['attendees'])}")
            print(f"   Date: {meeting_details['date']}")
            print(f"   Time: {meeting_details['time']}")
            print(f"   Duration: {meeting_details['duration_minutes']} min")
            
            confirm = input("\n✅ Correct? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y', 'yeah', 'yep']:
                print("❌ Cancelled")
                return None
            
            date_str = f"{meeting_details['date']} {meeting_details['time']}"
            start_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            
            print("\n📅 Creating event...")
            event = create_calendar_event(
                title=meeting_details['title'],
                attendees=meeting_details['attendees'],
                start_time=start_time,
                duration_minutes=meeting_details['duration_minutes']
            )
            
            print(f"\n✅ SUCCESS!")
            print(f"🔗 {event.get('htmlLink')}")
            print(f"📧 Invites sent to: {', '.join(meeting_details['attendees'])}")
            
            return event
            
        except json.JSONDecodeError as e:
            print(f"❌ Parse error. Try being more specific.")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def show_upcoming_meetings(self):
        """Show upcoming meetings"""
        try:
            print("\n📅 Fetching meetings...")
            events = list_upcoming_events(max_results=5)
            
            if not events:
                print("   No upcoming meetings.")
                return
            
            print(f"\n📋 Next {len(events)} meetings:")
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                formatted = dt.strftime("%b %d, %I:%M %p")
                print(f"   {i}. {formatted} - {summary}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    print("="*60)
    print("🤖 AI MEETING COORDINATOR (Google Gemini)")
    print("="*60)
    
    agent = MeetingAgent()
    
    print("\n💡 Commands:")
    print("   • Type meeting request naturally")
    print("   • 'list' - Show upcoming meetings")
    print("   • 'quit' - Exit")
    
    print("\n📝 Examples:")
    print("   schedule meeting with alice@gmail.com tomorrow at 2pm")
    print("   call with bob@test.com Monday at 10am for 30 minutes")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'list':
                agent.show_upcoming_meetings()
            else:
                agent.schedule_meeting(user_input)
            
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()