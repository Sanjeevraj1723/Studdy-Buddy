"""Talks to the AI. Switch provider with AI_PROVIDER in your .env file."""
import os
import base64
import google.generativeai as genai

# Setup provider variable
PROVIDER = "gemini"

# Configure the API key using the standard library format
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the client object that the rest of your file uses
_client = genai.GenerativeModel('gemini-1.5-flash')

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
            model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=1500,
            messages=[{"role": "user", "content": content}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    # standard stable Gemini implementation using google-generativeai library
    try:
        if image_bytes:
            # If an image doubt is submitted
            response = _client.generate_content([
                {'mime_type': mime_type, 'data': image_bytes},
                prompt
            ])
        else:
            # If it's a normal text doubt
            response = _client.generate_content(prompt)
            
        return response.text or ""
    except Exception as e:
        print(f"AI Generation Error: {str(e)}")
        return "The AI is busy right now. Please try again."

