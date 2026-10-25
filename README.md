# Study-Buddy

Doubt solver (text, image, voice), timetable maker (up to 8 subjects), warm-ups and study cards.
Flask backend + HTML/CSS/JS frontend.

## Run on your computer (Windows + VS Code)
1. Unzip the folder and open it in VS Code (File > Open Folder).
2. Open a terminal in VS Code (Terminal > New Terminal) and run:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Make your settings file: copy `.env.example` and rename the copy to `.env`.
   Open `.env` and paste your API key (get a Gemini key from Google AI Studio, or a Claude key from the Anthropic Console).
4. Start the site:
   ```
   python app.py
   ```
5. Open http://127.0.0.1:5000 in Chrome.

## Put it online (Render, example)
1. Create a free GitHub account and upload this folder (the `.gitignore` keeps `.env` private).
2. On render.com choose New > Web Service and connect your GitHub repo.
3. Build command: `pip install -r requirements.txt`   Start command: `gunicorn app:app`
4. Under Environment, add the same values as your `.env` (AI_PROVIDER, the API key, DAILY_LIMIT).
5. Deploy. You get a public https link.

## Get found on Google
1. (Optional) Buy a domain and connect it in Render settings.
2. Go to Google Search Console, add your site and verify it.
3. Submit `https://YOUR-SITE/sitemap.xml`.

## Notes
- Check current model names and prices in your provider's docs; change them in `.env` if needed.
- Study cards are saved in each visitor's own browser (localStorage).
- Add a short privacy note before launching, since many users are students.
