"""Talks to the AI. Switch provider with AI_PROVIDER in your .env file."""
import base64
import os

PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

_client = None


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
