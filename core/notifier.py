import urllib.request
import urllib.error
from core.config import NTFY_TOPIC

def send(title: str, message: str, priority: str = "default", correlation_id: str = "corr-notifier-default") -> bool:
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    headers = {
        "Title": title.encode("utf-8") if isinstance(title, str) else title,
        "Priority": priority
    }
    
    data = message.encode("utf-8") if isinstance(message, str) else message
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print(f"[INFO] NTFY_SUCCESS: Wysłano: {title}")
                return True
    except urllib.error.URLError as e:
        print(f"[ERROR] NTFY_ERROR: {e.reason}")
    except Exception as e:
        print(f"[ERROR] NTFY_ERROR: {str(e)}")
        
    return False
