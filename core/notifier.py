"""Optional ntfy notification helper.

Notifications must never make an agent or the daily workflow fail. Configure
NTFY_TOPIC to enable delivery; otherwise messages are logged to stdout.
"""

from __future__ import annotations

import os
from typing import Optional

import requests


def send(title: str, message: str) -> bool:
    """Send *message* to ntfy, returning False when notifications are disabled.

    The notifier is deliberately best-effort: a notification outage should not
    prevent the daily report from being generated.
    """
    topic = os.getenv("NTFY_TOPIC")
    if not topic:
        print(f"[notifier] NTFY_TOPIC not configured; skipped: {title}")
        return False

    server = os.getenv("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
    try:
        response = requests.post(
            f"{server}/{topic.lstrip('/')}",
            data=message.encode("utf-8"),
            headers={"Title": title, "Content-Type": "text/plain; charset=utf-8"},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        print(f"[notifier] notification failed: {exc}")
        return False
