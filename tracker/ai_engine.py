import requests
import os
import time
import json
import re


API_KEY = os.getenv("GEMINI_API_KEY")

def generate_ai_insight(data):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""
You are a financial analyst AI.

Analyze this data:
{data}

Return ONLY valid JSON.
Do NOT include ```json or ``` markers.
Do NOT include any explanation.

Format:
{{
  "summary": "1 line summary",
  "top_category": "category name",
  "top_category_percent": number,
  "anomaly": "biggest unusual spending",
  "advice": ["point1", "point2", "point3"]
}}
"""
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload)
        result = response.json()
    except Exception as e:
        print("REQUEST ERROR:", e)
        return fallback_response("Request failed")

    # 🔥 HANDLE API ERRORS
    if "error" in result:
        code = result["error"].get("code")

        if code == 429:
            return fallback_response("Rate limit hit")

        if code == 503:
            return fallback_response("Service busy")

        return fallback_response("Unknown API error")

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("RESPONSE FORMAT ERROR:", e)
        return fallback_response("Invalid response structure")

    print("RAW AI RESPONSE:\n", text)  # 🧪 debug once if needed

    # 🔥 CLEAN RESPONSE
    text = text.replace("```json", "").replace("```", "").strip()

    # 🔥 EXTRACT JSON ONLY
    match = re.search(r"\{.*\}", text, re.DOTALL)
    clean_text = match.group(0) if match else text

    # 🔥 PARSE SAFELY
    try:
        return json.loads(clean_text)
    except Exception as e:
        print("PARSE ERROR:", e)
        print("CLEAN TEXT:", clean_text)
        return fallback_response("Parsing failed")


# ✅ COMMON FALLBACK
def fallback_response(reason):
    return {
        "summary": f"AI unavailable ({reason})",
        "top_category": None,
        "top_category_percent": None,
        "anomaly": "Could not analyze spending right now",
        "advice": [
            "Please try again later",
            "Your expense tracking is still working correctly"
        ]
    }
