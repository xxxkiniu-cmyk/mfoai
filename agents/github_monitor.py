import subprocess
from core.notifier import send
from core.logger import Logger

def run_github_monitor():
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--workflow=bot.yml", "--limit=1", "--json", "status,conclusion,createdAt"],
            capture_output=True, text=True, timeout=30
        )
        data = result.stdout.strip()
        if "completed" in data and "success" in data:
            msg = "✅ GitHub Actions: ostatni run SUCCESS"
        elif "failure" in data:
            msg = "❌ GitHub Actions: ostatni run FAILURE"
        else:
            msg = f"📊 GitHub Actions status:\n{data[:200]}"
    except Exception as e:
        msg = f"GitHub Monitor błąd: {e}"
    Logger.log("github_monitor", "CHECK", 0.1, "SUCCESS")
    send("GitHub Monitor MFO.ai", msg)
    return msg

def run():
    return run_github_monitor()

if __name__ == "__main__":
    print(run_github_monitor())
