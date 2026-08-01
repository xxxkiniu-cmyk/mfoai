key = open(os.path.expanduser('~/.env')).read().strip().split('=')[1]
key = os.environ.get('OPENROUTER_KEY') or open(os.path.expanduser('~/.env')).read().strip().split('=')[1]key = os.environ.get('OPENROUTER_KEY') or open(os.path.expanduser('~/.env')).read().strip().split('=')[1]import requests
import os

# Wczytaj klucz API
key = open(os.path.expanduser('~/.env')).read().strip().split('=')[1]

# Pytanie do AI
pytanie = "Podaj krotka motywacyjna wiadomosc na dzisiaj po polsku. Max 2 zdania."

# Zapytaj AI
r = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={'Authorization': f'Bearer {key}'},
    json={
        'model': 'openai/gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': pytanie}]
    }
)

data = r.json()

if 'choices' in data:
    odpowiedz = data['choices'][0]['message']['content']
else:
    odpowiedz = "Blad AI: " + str(data)

# Wyslij na ntfy
requests.post(
    'https://ntfy.sh/centrum-dowodzenia-v3',
    data=odpowiedz.encode('utf-8'),
    headers={'Title': 'MFO.ai Bot'}
)

print("Wyslano:", odpowiedz)

