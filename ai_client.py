import os
import base64
import time
import requests

PROVIDER = "gemini"

BASE_URL = "https://generativelanguage.googleapis.com"
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
]


def generate(prompt, image_bytes=None, mime_type=None):
    """Generate an answer with retries and a backup Gemini model."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("GEMINI_API_KEY is missing from server settings.")
        return "AI setup error. Please check server configuration."

    parts = [{"text": str(prompt)}]

    if image_bytes:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        parts.append({
            "inlineData": {
                "mimeType": mime_type or "image/jpeg",
                "data": image_b64,
            }
        })

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

    for model in MODELS:
        url = f"{BASE_URL}/v1beta/models/{model}:generateContent"

        for attempt in range(2):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=45,
                )

                if response.ok:
                    data = response.json()
                    candidates = data.get("candidates", [])

                    if candidates:
                        answer_parts = candidates[0].get(
                            "content", {}
                        ).get("parts", [])

                        answer = "".join(
                            part.get("text", "")
                            for part in answer_parts
                            if isinstance(part.get("text"), str)
                        ).strip()

                        if answer:
                            return answer

                    print("Gemini returned no usable answer.")
                    break

                print(
                    f"Gemini model {model}: "
                    f"HTTP {response.status_code}"
                )

                if response.status_code not in (429, 500, 502, 503, 504):
                    print("Gemini error:", response.text[:1000])
                    return (
                        f"Gemini API error ({response.status_code}). "
                        "Please check server configuration and API access."
                    )

                if attempt == 0:
                    time.sleep(2)

            except requests.exceptions.Timeout:
                print(f"Gemini timeout on model {model}.")
                if attempt == 0:
                    time.sleep(2)

            except (requests.exceptions.RequestException, ValueError) as exc:
                print(f"Gemini request failed: {type(exc).__name__}")
                if attempt == 0:
                    time.sleep(2)

    return (
        "The AI services are temporarily busy. "
        "Please wait a little and try again."
    )
