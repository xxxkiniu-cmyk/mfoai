import os

def get(key: str, default: str = "") -> str:
    return os.getenv(key, default)

KEYS = {
    "chatgpt": get("OPENAI_API_KEY"),
    "claude": get("ANTHROPIC_API_KEY"),
    "gemini": get("GEMINI_API_KEY"),
    "meta": get("META_API_KEY"),
    "grok": get("GROK_API_KEY"),
    "openrouter": get("OPENROUTER_API_KEY"),
}

def get_key(model: str) -> str:
    return KEYS.get(model.lower(), "")
