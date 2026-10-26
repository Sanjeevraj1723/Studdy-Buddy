import os
import base64
import requests

PROVIDER = "gemini"

# Gemini API configuration
BASE_URL = "https://generativelanguage.googleapis.com"
MODEL = "gemini-2.5-flash"


def generate(prompt, image_bytes=None, mime_type=None):
    """Generate a Study Buddy response using Google's Gemini API."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Configuration error: GEMINI_API_KEY is missing.")
        return "AI setup error. Please check the server configuration."

    url = f"{BASE_URL}/v1beta/models/{MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    parts = [{"text": str(prompt)}]

    # Include an image when one is provided
    if image_bytes:
        if not mime_type:
            mime_type = "image/jpeg"

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": image_b64,
            }
        })

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=45,
        )

        # Check HTTP errors before trying to parse JSON
        if not response.ok:
            print("Gemini HTTP status:", response.status_code)
            print("Gemini error response:", response.text[:1500])
            return (
                f"Gemini API error ({response.status_code}). "
                "Please check the server logs."
            )

        # Safely parse the response
        try:
            data = response.json()
        except ValueError:
            print("Gemini returned a non-JSON response.")
            print("Response:", response.text[:1000])
            return "The AI returned an unexpected response. Please try again."

        # Check whether Gemini returned any usable text
        candidates = data.get("candidates", [])

        if not candidates:
            print("Gemini returned no candidates:", str(data)[:1500])
            return "The AI could not generate an answer. Please try again."

        content = candidates[0].get("content", {})
        response_parts = content.get("parts", [])

        answer = "".join(
            part.get("text", "")
            for part in response_parts
            if isinstance(part.get("text"), str)
        ).strip()

        if answer:
            return answer

        print("Gemini response contained no text:", str(data)[:1500])
        return "The AI returned no text. Please try another question."

    except requests.exceptions.Timeout:
        print("Gemini request timed out.")
        return "The AI took too long to respond. Please try again."

    except requests.exceptions.RequestException as exc:
        print("Gemini connection error:", repr(exc))
        return "Could not connect to the AI service. Please try again."

    except Exception as exc:
        print("Unexpected AI client error:", repr(exc))
        return "Something went wrong while generating the answer."
