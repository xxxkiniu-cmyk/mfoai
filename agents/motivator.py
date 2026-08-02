from core.llm_client import query_llm

def run_motivator():
    prompt = "Podaj krotka motywacyjna wiadomosc na dzisiaj po polsku. Max 2 zdania."
    return query_llm(prompt)
