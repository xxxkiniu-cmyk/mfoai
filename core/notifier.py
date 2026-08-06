import os
import requests

def notify(message: str, title: str = "MFO.ai"):
    topic = os.getenv("NTFY_TOPIC", "")
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    if topic:
        try:
            requests.post(
                f"https://ntfy.sh/{topic}",
                data=message.encode("utf-8"),
                headers={"Title": title},
                timeout=10
            )
            print(f"[NTFY] {title}: {message}")
        except Exception as e:
            print(f"[NTFY] Błąd: {e}")
    
    if token and chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": f"{title}: {message}"},
                timeout=10
            )
            print(f"[TG] {title}: {message}")
        except Exception as e:
            print(
cat > ~/.mfo/core/notifier.py << 'EOF'
import os
import requests

def notify(message: str, title: str = "MFO.ai"):
    topic = os.getenv("NTFY_TOPIC", "")
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    if topic:
        try:
            requests.post(
                f"https://ntfy.sh/{topic}",
                data=message.encode("utf-8"),
                headers={"Title": title},
                timeout=10
            )
            print(f"[NTFY] {title}: {message}")
        except Exception as e:
            print(f"[NTFY] Błąd: {e}")
    
    if token and chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": f"{title}: {message}"},
                timeout=10
            )
            print(f"[TG] {title}: {message}")
        except Exception as e:
            print(f"[TG] Błąd: {e}")
