import urllib.request, re
from core.llm_client import ask
from core.notifier import send
from core.logger import Logger

def fetch_news():
    try:
        url = "https://feeds.bbci.co.uk/news/world/rss.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read().decode("utf-8")
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", content)
        if len(titles) < 2:
            titles = re.findall(r"<title>(.*?)</title>", content)
        titles = titles[1:6] if len(titles) > 1 else titles[:5]
        return titles if titles else None
    except Exception as e:
        Logger.log("news", f"RSS error {e}", 0.1, "ERROR")
        return None

def run_news():
    titles = fetch_news()
    if not titles:
        msg = "📰 Wiadomości świat: brak danych (BBC RSS niedostępny)"
        send("Wiadomości MFO.ai", msg)
        return msg
    titles_str = "\n".join([f"- {t}" for t in titles])
    prompt = f"Podsumuj po polsku w 4 zdaniach trendy z nagłówków BBC:\n{titles_str}\nWskaż 1 okazję dla MFO folie, wezwanie do działania."
    try:
        summary = ask(prompt)
    except Exception as e:
        summary = "\n".join([f"• {t}" for t in titles]) + f"\n(błąd AI: {e})"
    msg = f"📰 Wiadomości świat:\n" + "\n".join([f"• {t}" for t in titles]) + f"\n\n🤖 Podsumowanie AI:\n{summary}"
    Logger.log("news", "RSS", 0.1, "SUCCESS")
    send("Wiadomości MFO.ai", msg)
    return msg

def run():
    return run_news()

if __name__ == "__main__":
    print(run_news())
