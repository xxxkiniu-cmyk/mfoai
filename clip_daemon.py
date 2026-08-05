#!/data/data/com.termux/files/usr/bin/python3
# ~/.mfo/clip_daemon.py - AUTO-SCHOWEK 1.5s
import subprocess, time, hashlib, pathlib, sys
sys.path.insert(0, str(pathlib.Path.home() / ".mfo"))
# Reużyj logiki z save.py
import importlib.util
spec = importlib.util.spec_from_file_location("save", str(pathlib.Path.home() / ".mfo/save.py"))
# prostszy: uruchom save.py jako proces

def get_clip():
    try:
        out = subprocess.check_output(["termux-clipboard-get"], timeout=2)
        return out.decode("utf-8", errors="ignore")
    except:
        return ""

def save_via_parser(text):
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(text)
        fname = f.name
    os.system(f"python ~/.mfo/save.py {fname}")
    os.unlink(fname)

print("[MFO] Clip daemon start - kopiuj w Gemini, ja zapiszę")
last_hash = ""
while True:
    try:
        txt = get_clip()
        if not txt: 
            time.sleep(1.5)
            continue
        h = hashlib.md5(txt.encode()).hexdigest()
        if h != last_hash and "# FILE:" in txt:
            print(f"[MFO] Nowy schowek wykryty ({len(txt)} znaków) -> zapisuję")
            save_via_parser(txt)
            last_hash = h
    except Exception as e:
        print("Err:", e)
    time.sleep(1.5)

