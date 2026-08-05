#!/data/data/com.termux/files/usr/bin/python3
# ~/.mfo/save.py - TURBO PARSER
import sys, os, re, json, shutil, py_compile, time, pathlib
from datetime import datetime

BASE = pathlib.Path.home() / ".mfo"
INBOX = BASE / "storage/inbox"
LOGS = BASE / "storage/logs"
LOGS.mkdir(parents=True, exist_ok=True)
INBOX.mkdir(parents=True, exist_ok=True)

def notify(msg, is_error=False):
    title = "MFO TURBO"
    try:
        os.system(f'termux-notification --content "{msg[:120]}" --title "{title}" {"--priority high" if not is_error else ""} --button1 "Otwórz" --button1-action "termux-open {INBOX}" 2>/dev/null || true')
        if is_error:
            os.system("termux-vibrate -d 600 2>/dev/null || true")
        else:
            os.system("termux-vibrate -d 100 2>/dev/null || true")
    except: pass
    # Fallback dla braku termux-api
    try:
        # Próba użycia black jeśli jest
        pass
    except: pass

def log_action(path, status):
    entry = {
        "ts": datetime.now().isoformat(),
        "file": str(path),
        "status": status
    }
    with open(LOGS / "turbo.jsonl", "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def format_file(p: pathlib.Path):
    try:
        os.system(f"black {p} -q 2>/dev/null; isort {p} -q 2>/dev/null || true")
    except: pass

# Wczytaj input
src_path = sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin"
try:
    text = pathlib.Path(src_path).read_text(encoding="utf-8", errors="ignore")
except:
    text = sys.stdin.read()

if not text.strip():
    notify("Pusty share - nic do zapisu", True)
    sys.exit(0)

# Parser: split by # FILE: lub ### FILE:
pattern = re.compile(r'(?:^|\n)\s*(?:#|//)?\s*FILE:\s*(.+?)\s*\n', re.IGNORECASE)
# Lepszy split: szukaj markerów
parts = re.split(r'(?m)^(?:#{1,3}|//)\s*FILE:\s*(.+)$', text)

files_to_save = []
if len(parts) == 1:
    # Brak markerów -> inbox
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    inbox_file = INBOX / f"paste_{ts}.py"
    files_to_save.append((inbox_file, text))
else:
    # parts: [pre, path1, content1, path2, content2...]
    i = 1
    while i < len(parts)-1:
        raw_path = parts[i].strip().strip('"').strip("'").strip()
        content = parts[i+1]
        # Wyczyść content - usuń pierwszy newline
        if content.startswith("\n"): content = content[1:]
        # Zabezpieczenie ścieżki
        p = pathlib.Path.home() / raw_path.lstrip("~/").lstrip("/")
        if raw_path.startswith("~/") or raw_path.startswith("./"):
            p = pathlib.Path.home() / raw_path.lstrip("~/").lstrip("./")
        elif not raw_path.startswith("/"):
            p = pathlib.Path.home() / raw_path
        else:
            p = pathlib.Path(raw_path)
        files_to_save.append((p, content))
        i += 2

for target_path, content in files_to_save:
    target_path = pathlib.Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup
    if target_path.exists():
        shutil.copy2(target_path, str(target_path) + ".bak")

    # Sprawdź składnię dla .py
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")

    if target_path.suffix == ".py":
        try:
            py_compile.compile(str(tmp_path), doraise=True)
        except py_compile.PyCompileError as e:
            err_file = target_path.with_suffix(".error.py")
            tmp_path.rename(err_file)
            notify(f"BŁĄD: {target_path.name} - {e}", True)
            log_action(target_path, f"ERROR: {e}")
            print(f"[!] Błąd składni w {target_path}, zapisano jako {err_file}")
            continue

    # OK - nadpisz
    format_file(tmp_path)
    shutil.move(str(tmp_path), str(target_path))
    notify(f"✅ Zapisano: {target_path}")
    log_action(target_path, "OK")
    print(f"[OK] {target_path}")

