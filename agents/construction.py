from core.llm_client import ask
from core.notifier import send
from core.logger import Logger

def run_construction():
    prompt = """Jesteś asystentem firmy Master Home Finish Szczecin (folie okienne, montaż, kosztorysy).
Podaj po polsku w 4 punktach:
1. Tip dnia dla ekipy montażowej
2. Co sprawdzić przed wyjazdem do klienta
3. Jak wycenić zlecenie na folię matową 20m2
4. Motywacja dla właściciela firmy
Bądź konkretny i praktyczny."""
    try:
        advice = ask(prompt)
    except Exception as e:
        advice = f"Błąd AI: {e}"
    msg = f"🏗️ MFO Budowlany:\n{advice}"
    Logger.log("construction", "AI", 0.5, "SUCCESS")
    send("MFO Budowlany", msg)
    return msg

def run():
    return run_construction()

if __name__ == "__main__":
    print(run_construction())
