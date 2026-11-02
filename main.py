import os, json, datetime, tempfile
import agents.motivator, agents.weather, agents.finance, agents.news

def try_call(mod):
    for fn in ["run", "run_motivator", "run_weather", "fetch_weather", "run_finance"]:
        if hasattr(mod, fn):
            return getattr(mod, fn)()
    if hasattr(mod, "get_exchange_rates"):
        return mod.get_exchange_rates()
    raise Exception(f"Brak funkcji startowej w {mod.__name__}")

def main():
    fp = "reports.json"
    try:
        with open(fp, "r", encoding="utf-8") as f:
            hist = json.load(f)
    except FileNotFoundError:
        hist = []
    except (OSError, ValueError):
        raise RuntimeError("Nie można odczytać reports.json; zapis wstrzymany.") from None
    if not isinstance(hist, list):
        raise RuntimeError("reports.json musi zawierać listę; zapis wstrzymany.")

    report = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "agents": {}}
    for name, mod in [("motivator", agents.motivator), ("weather", agents.weather), ("finance", agents.finance), ("news", agents.news)]:
        try:
            res = try_call(mod)
            data = str(res) if name == "news" else str(res)[:500]
            if isinstance(res, dict) and res.get("ok") is False:
                error = str(res.get("error") or "Agent zwrócił ok=False.")
                report["agents"][name] = {"status": "ERROR", "data": data, "error": error}
                print(f"[{name}] ERROR: {error}")
                continue
            report["agents"][name] = {"status": "SUCCESS", "data": data}
            if name == "motivator":
                report["agents"][name]["fallback_used"] = res["fallback_used"]
            print(f"[{name}] SUCCESS")
        except Exception as e:
            report["agents"][name] = {"status": "ERROR", "error": str(e)}
            print(f"[{name}] ERROR: {e}")

    hist.append(report)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=os.path.dirname(os.path.abspath(fp)),
            prefix=".reports-", suffix=".tmp", delete=False,
        ) as f:
            temp_path = f.name
            json.dump(hist, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, fp)
    except (OSError, ValueError, TypeError):
        raise RuntimeError("Nie można zapisać reports.json; oryginał zachowany.") from None
    finally:
        if temp_path is not None:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass
    print(f"\n[INFO] Zapisano raport do {fp}")

if __name__ == "__main__":
    main()
