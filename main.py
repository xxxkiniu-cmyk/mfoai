import os, json, datetime
import agents.motivator, agents.weather, agents.finance, agents.news

def try_call(mod):
    for fn in ["run", "run_motivator", "run_weather", "fetch_weather", "run_finance"]:
        if hasattr(mod, fn):
            return getattr(mod, fn)()
    if hasattr(mod, "get_exchange_rates"):
        return mod.get_exchange_rates()
    raise Exception(f"Brak funkcji startowej w {mod.__name__}")

def main():
    report = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "agents": {}}
    for name, mod in [("motivator", agents.motivator), ("weather", agents.weather), ("finance", agents.finance), ("news", agents.news)]:
        try:
            res = try_call(mod)
            report["agents"][name] = {"status": "SUCCESS", "data": str(res)[:500]}
            print(f"[{name}] SUCCESS")
        except Exception as e:
            report["agents"][name] = {"status": "ERROR", "error": str(e)}
            print(f"[{name}] ERROR: {e}")

    fp="reports.json"
    hist=[]
    if os.path.exists(fp):
        try:
            with open(fp,'r',encoding='utf-8') as f: hist=json.load(f)
        except: hist=[]
    hist.append(report)
    with open(fp,'w',encoding='utf-8') as f: json.dump(hist,f,ensure_ascii=False,indent=2)
    print(f"\n[INFO] Zapisano raport do {fp}")

if __name__ == "__main__":
    main()
