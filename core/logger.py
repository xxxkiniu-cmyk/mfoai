"""Small dependency-free logger used by agents."""

from __future__ import annotations

from datetime import datetime, timezone


class Logger:
    """Minimal logger compatible with the existing agent calls."""

    @staticmethod
    def log(agent: str, message: str, latency: float = 0.0, status: str = "INFO") -> None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"[{timestamp}] [{agent}] [{status}] ({latency:.2f}s) {message}")
