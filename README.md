# Personalized AI Study Pack Generator

## Architecture

- `app.py` — Streamlit interface and controller
- `ai_workflow.py` — staged AI workflow: planning → content → review → conditional repair → verification
- `utils.py` — validation and formatting helpers
- `prompts/01_planning_prompt.txt` — planning-agent prompt
- `prompts/02_content_generation_prompt.txt` — content-generation prompt
- `prompts/03_review_repair_prompt.txt` — review/repair prompt
- `requirements.txt` — deployment dependencies

## Local setup

1. Create a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example`.
4. Put your real OpenAI API key in the secret file.
5. Run:
   `streamlit run app.py`

## Streamlit Community Cloud

Push this project to GitHub with `secrets.toml` excluded from Git.

Create a Streamlit Community Cloud app using `app.py` as the entrypoint. In the app's Secrets settings, add:

OPENAI_API_KEY = "your-real-key"

Never commit the real API key to GitHub.
