import os
import base64
import time
import requests

PROVIDER = "gemini"

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Primary model first, backup model second
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
]

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def generate(prompt, image_bytes=None, mime_type=None):
    """Generate Study Buddy answers using Gemini with retries and fallback."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Configuration error: GEMINI_API_KEY is missing.")
        return "AI setup error. Please check the server configuration."

    # Prepare the question and optional image
    parts = [{"text": str(prompt)}]

    if image_bytes:
        try:
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            parts.append({
                "inlineData": {
                    "mimeType": mime_type or "image/jpeg",
                    "data": image_b64,
                }
            })
        except Exception as exc:
            print("Image preparation error:", type(exc).__name__)
            return "Could not process that image. Please try another image."

    payload = {
        "contents": [{
            "role": "user",
            "parts": parts,
        }]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    # Try the primary model and then the backup
    for model in MODELS:
        url = f"{BASE_URL}/{model}:generateContent"

        print(f"Trying Gemini model: {model}")

        for attempt in range(2):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=40,
                )

                if response.ok:
                    try:
                        data = response.json()
                    except ValueError:
                        print(f"{model}: response was not valid JSON.")
                        break

                    candidates = data.get("candidates", [])

                    if candidates:
                        answer_parts = candidates[0].get(
                            "content", {}
                        ).get("parts", [])

                        answer = "".join(
                            item.get("text", "")
                            for item in answer_parts
                            if isinstance(item.get("text"), str)
                        ).strip()

                        if answer:
                            print(f"Gemini succeeded with {model}.")
                            return answer

                    print(f"{model}: no usable answer returned.")
                    break

                status = response.status_code
                print(f"{model}: HTTP {status}")

                if status in RETRYABLE_STATUS_CODES:
                    if attempt == 0:
                        time.sleep(2)
                        continue

                    # After retrying, move to the backup model
                    break

                if status == 404:
                    print(f"{model}: model unavailable; trying backup.")
                    break

                if status in (401, 403):
                    print("Gemini API key or permission problem.")
                    return (
                        "AI access error. Please check your Gemini API "
                        "key and model permissions in server settings."
                    )

                print("Gemini error response:", response.text[:800])
                return (
                    f"Gemini API error ({status}). "
                    "Please check the server logs."
                )

            except requests.exceptions.Timeout:
                print(f"{model}: request timed out.")

                if attempt == 0:
                    time.sleep(2)
                    continue

                break

            except requests.exceptions.RequestException as exc:
                print(f"{model}: connection error: {type(exc).__name__}")
                break

            except Exception as exc:
                print(f"{model}: unexpected error: {type(exc).__name__}")
                break

    print("All configured Gemini models failed.")

    return (
        "The AI service is temporarily unavailable or busy. "
        "Please wait a little and try again."
    )
                
                
