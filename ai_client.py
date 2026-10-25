"""Talks to the AI. Switch provider with AI_PROVIDER in your .env file."""
import os
from google import genai
from google.genai import types

# Use the rock-solid model version
PROVIDER="gemini"
GEMINI_MODEL = "gemini-1.5-flash"

# Force the stable v1 API version directly inside the client
_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1'}
)


def generate(prompt, image_bytes=None, mime_type=None):
    """Return the AI's text answer. image_bytes is optional."""
    global _client
    if PROVIDER == "claude":
        import anthropic

        if _client is None:
            _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        content = []
        if image_bytes:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64.b64encode(image_bytes).decode(),
                },
            })
        content.append({"type": "text", "text": prompt})
        resp = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": content}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    # default: Gemini through the google-genai SDK
    from google import genai
    from google.genai import types

    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    parts = []
    if image_bytes:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
    parts.append(prompt)
    resp = _client.models.generate_content(model=GEMINI_MODEL, contents=parts)
    return resp.text or ""


