import sys
import os

# Dodajemy ścieżkę do modułów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import motivator, weather

def main():
    print("=== MFO.ai Command Center ===")
    
    print("\n[1/2] Uruchamianie Agenta Motywacyjnego...")
    try:
        motivator.run()
    except Exception as e:
        print(f"Błąd w motivator: {e}")
        
    print("\n[2/2] Uruchamianie Agenta Pogody...")
    try:
        report = weather.fetch_weather()
        print(f"Pogoda: {report}")
        weather.send_notification(report)
    except Exception as e:
        print(f"Błąd w weather: {e}")

if __name__ == "__main__":
    main()
