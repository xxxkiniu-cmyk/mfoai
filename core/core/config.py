import os
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "local-dummy-key")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "local-model")
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL", "local-model")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://127.0.0.1:8080/v1")
NTFY_TOPIC = "centrum-dowodzenia-v3"
CITY = "Warszawa"
MAX_REPORTS = 30
LOG_DIR = "logs/"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
