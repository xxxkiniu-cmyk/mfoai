import random
from core.llm_client import ask
from core.notifier import send
from core.logger import Logger

FALLBACK_QUOTES = [
    "Dzialaj lokalnie, mysl globalnie! Kazdy krok ma znaczenie.",
    "Nawet najmniejszy kod napisany dzisiaj to krok do przodu.",
    "System dziala, Ty tez dajesz rade. Walcz o swoje!"
]

def run_motivator():
    prompt = "Napisz krotka, motywujaca sentencje po polsku dla programisty budujacego system offline-first."
    try:
        quote = ask(prompt)
        if not quote or "[ERROR]" in quote:
            raise Exception("LLM offline or returned error")
        Logger.log("motivator", "LLM", 0.5, "SUCCESS")
    except Exception as e:
        quote = random.choice(FALLBACK_QUOTES)
        Logger.log("motivator", "FALLBACK", 0.1, "WARNING", error=str(e))
    send("Motywacja MFO.ai", quote, priority="default")
    return quote

if __name__ == "__main__":
    print(run_motivator())


def run():
 return run_motivator()
