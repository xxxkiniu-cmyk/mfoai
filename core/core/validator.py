def validate_event(event: dict) -> bool:
    required = ["type", "payload", "timestamp", "source"]
    for field in required:
        if field not in event:
            print(f"[VALIDATOR] Brak pola: {field}")
            return False
    return True

def validate_command(command: dict) -> bool:
    required = ["type", "target_agent", "payload", "timestamp"]
    for field in required:
        if field not in command:
            print(f"[VALIDATOR] Brak pola: {field}")
            return False
    return True
