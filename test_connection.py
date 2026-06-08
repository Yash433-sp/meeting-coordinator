print("Testing connections...\n")

# Test Gemini
print("1️⃣ Testing Gemini API...")
try:
    import os
    import google.genai as genai
    from dotenv import load_dotenv
    
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Try multiple model names
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except:
        try:
            model = genai.GenerativeModel('gemini-2.5-pro')
        except:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    response = model.generate_content("Say 'API works!'")
    
    print(f"    Gemini: {response.text.strip()}")
except Exception as e:
    print(f"    Error: {str(e)}")

# Test Calendar
print("\n2️⃣ Testing Google Calendar...")
try:
    from calendar_tools import get_calendar_service
    
    service = get_calendar_service()
    print("    Calendar: Connected!")
    
except Exception as e:
    print(f"    Error: {str(e)}")

print("\n✅ Done!")