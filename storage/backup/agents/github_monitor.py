import urllib.request
import json
from core.notifier import send
from core.logger import Logger
from core.config import GITHUB_TOKEN

def run_github_monitor():
    repo = "xxxkiniu-cmyk/mfoai"
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=3"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MFO.ai-Monitor"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                runs = data.get("workflow_runs", [])
                if not runs:
                    report = "GitHub Actions: Brak uruchomien."
                else:
                    lines = []
                    for run in runs:
                        name = run.get("name", "Unknown")
                        conclusion = run.get("conclusion", "in_progress")
                        lines.append(f"- {name}: {conclusion}")
                    report = "Ostatnie workflow:
" + "
".join(lines)
                Logger.log("github_monitor", "API", 0.3, "SUCCESS")
                send("MFO.ai: GitHub Monitor", report, priority="default")
                return report
    except Exception as e:
        error_msg = f"Blad GitHub API: {e}"
        Logger.log("github_monitor", "API", 0.3, "WARNING", error=str(e))
        send("MFO.ai: GitHub Monitor", error_msg, priority="high")
        return error_msg

if __name__ == "__main__":
    print(run_github_monitor())
