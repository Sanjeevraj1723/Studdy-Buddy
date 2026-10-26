import os
import requests

PROVIDER = "gemini"

def generate(prompt, image_bytes=None, mime_type=None):
    """Sends clean HTTP requests directly to Google Gemini's official stable endpoint."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "API Key missing in environment settings."

    # Completely fixed, absolute URL structure separating the base path from the API key parameter
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
            # Standard path extraction to pull the text response out of the JSON response block cleanly
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_msg = data.get("error", {}).get("message", "API Configuration Mismatch")
            print(f"Google Direct Server Error: {error_msg}")
            return "The AI is busy right now. Please try again."
            
    except Exception as e:
        print(f"Network Connection Exception: {str(e)}")
        return "The AI is busy right now. Please try again."
