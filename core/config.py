import os
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
FALLBACK_MODEL = "mistralai/mistral-7b-instruct:free"
NTFY_TOPIC = "centrum-dowodzenia-v3"
CITY = "Warszawa"
MAX_REPORTS = 30
LOG_DIR = "logs/"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
