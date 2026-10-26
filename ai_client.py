import os
import requests

PROVIDER = "gemini"

def generate(prompt, image_bytes=None, mime_type=None):
    """Sends requests directly to Google's stable API endpoint without old library files."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "API Key missing in configuration."

    # Using Google's stable direct execution route
    url = f"https://googleapis.com{api_key}"
    headers = {"Content-Type": "application/json"}

    if image_bytes:
        import base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": image_b64
                        }
                    }
                ]
            }]
        }
    else:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_msg = data.get("error", {}).get("message", "Unknown API error")
            print(f"Google Direct API Error: {error_msg}")
            return "The AI is busy right now. Please try again."
            
    except Exception as e:
        print(f"Connection Exception: {str(e)}")
        return "The AI is busy right now. Please try again."
