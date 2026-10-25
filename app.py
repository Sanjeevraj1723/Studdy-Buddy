import json
import os
import re
import time

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request

load_dotenv()  # must run before ai_client reads the environment
import ai_client  # noqa: E402

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024  # 6 MB uploads

DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "30"))  # AI requests per visitor per day
ALLOWED_IMAGES = {"image/jpeg", "image/png", "image/webp"}
LANGS = {"English", "Tamil", "Hindi"}
LEVELS = {"School", "College", "JEE", "NEET"}
STYLES = {"Simple (beginner)", "Normal", "Detailed (advanced)"}
_hits = {}


def over_limit():
    ip = (request.headers.get("X-Forwarded-For") or request.remote_addr or "?").split(",")[0].strip()
    day = time.strftime("%Y-%m-%d")
    for key in [k for k in _hits if k[1] != day]:
        del _hits[key]
    _hits[(ip, day)] = _hits.get((ip, day), 0) + 1
    return _hits[(ip, day)] > DAILY_LIMIT


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    question = (request.form.get("question") or "").strip()[:2000]
    level = request.form.get("level", "School")
    language = request.form.get("language", "English")
    style = request.form.get("style", "Normal")
    if level not in LEVELS or language not in LANGS or style not in STYLES:
        return jsonify(error="Invalid options."), 400

    image = request.files.get("image")
    img_bytes = mime = None
    if image:
        mime = image.mimetype
        if mime not in ALLOWED_IMAGES:
            return jsonify(error="Please upload a JPG, PNG or WEBP image."), 400
        img_bytes = image.read()
    if not question and not img_bytes:
        return jsonify(error="Please type or upload your doubt."), 400
    if over_limit():
        return jsonify(error="Daily limit reached. Please come back tomorrow."), 429

    prompt = (
        f"You are Study-Buddy, a friendly tutor for {level} students. "
        f"Answer in {language}. Style: {style}. "
        "Solve step by step, then give a one-line summary and one practice question. "
        "If an image is attached, read the doubt from it. "
        "Only help with studies; politely refuse anything else.\n\n"
        f"Student's doubt: {question or '(see image)'}"
    )
    try:
        answer = ai_client.generate(prompt, img_bytes, mime)
    except Exception as exc:  # keep keys and details out of the browser
        app.logger.error("AI error: %s", exc)
        return jsonify(error="The AI is busy right now. Please try again."), 502
    return jsonify(answer=answer)


@app.route("/api/cards", methods=["POST"])
def cards():
    data = request.get_json(silent=True) or {}
    topic = str(data.get("topic", "")).strip()[:200]
    level = data.get("level", "School")
    if not topic or level not in LEVELS:
        return jsonify(error="Please enter a topic."), 400
    if over_limit():
        return jsonify(error="Daily limit reached. Please come back tomorrow."), 429
    prompt = (
        f"Make 6 flashcards for a {level} student on the topic: {topic}. "
        'Reply ONLY with a JSON array like [{"f":"question","b":"short answer"}], no other text.'
    )
    try:
        text = ai_client.generate(prompt)
        items = json.loads(re.sub(r"```json|```", "", text).strip())
        items = [{"f": str(i["f"]), "b": str(i["b"])} for i in items if i.get("f") and i.get("b")]
    except Exception as exc:
        app.logger.error("Cards error: %s", exc)
        return jsonify(error="Could not make cards. Please try again."), 502
    return jsonify(cards=items)


@app.route("/robots.txt")
def robots():
    return Response(f"User-agent: *\nAllow: /\nSitemap: {request.url_root}sitemap.xml\n", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>{request.url_root}</loc></url></urlset>"
    )
    return Response(xml, mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True)
