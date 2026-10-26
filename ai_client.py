"""Talks to the AI. Standard stable implementation for Google Gemini."""
import os
import google.generativeai as genai

# Setup provider variable exactly as app.py expects
PROVIDER = "gemini"

# Configure using standard stable endpoint architecture
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the standard text generation instance
_client = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    client=genai.Client(http_options={'api_version': 'v1'}) if hasattr(genai, 'Client') else None
)
def generate(prompt, image_bytes=None, mime_type=None):
    """Return the AI's text answer. Handles text and images seamlessly."""
    global _client
    
    try:
        if image_bytes:
            # Format arguments for standard multimodal doubt submission
            response = _client.generate_content([
                {'mime_type': mime_type, 'data': image_bytes},
                prompt
            ])
        else:
            # Handle text-only doubts and flashcard processing
            response = _client.generate_content(prompt)
            
        return response.text or ""
    except Exception as e:
        print(f"Internal API Connection Error: {str(e)}")
        return "The AI is busy right now. Please try again."

