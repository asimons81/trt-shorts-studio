# Tony Shorts Studio

Tony Shorts Studio is a Streamlit-based helper app for producing YouTube Shorts for the channel **Tony Reviews Things**. It pulls article content, asks Gemini to craft a short script and metadata, generates Google Cloud Text-to-Speech voiceovers, surfaces visual prompts, and bundles assets for download.

## Features
- Fetch Tony Reviews Things articles or paste your own text as source material.
- Generate a full "short package" with summary, script, on-screen text, visual prompts, and metadata using **Gemini 2.5 Flash**.
- Synthesize MP3 voiceovers with **Google Cloud Text-to-Speech**.
- View visual prompt ideas and generate simple preview placeholders.
- Export everything as a downloadable zip (script, metadata, prompts, and voiceover if created).

## Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure secrets**
   Streamlit reads secrets from `.streamlit/secrets.toml`. Copy the template and fill in your values:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   GOOGLE_TTS_PROJECT_ID = "your-gcp-project-id"
   GOOGLE_TTS_CREDENTIALS_JSON = "{...service account json...}"
   WORDPRESS_BASE_URL = "https://tonyreviewsthings.com"
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Notes
- Gemini and Google TTS calls require valid credentials. The UI will show whether keys are detected.
- Placeholder preview images are generated locally if no image API is configured.
- The code favors small, composable modules under `services/` and `utils/` for clarity.
