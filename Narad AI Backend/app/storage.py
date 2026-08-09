"""Small durable JSON storage used by the hackathon backend.

The project does not need a heavyweight database for the demo. This store
provides atomic JSON persistence and keeps the application restart-safe.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def read(self, default: Any):
        with self._lock:
            if not self.path.exists():
                return default
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                return default

    def write(self, value: Any) -> None:
        with self._lock:
            fd, tmp = tempfile.mkstemp(
                prefix=self.path.name,
                suffix=".tmp",
                dir=str(self.path.parent),
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(value, f, ensure_ascii=False, indent=2, default=str)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, self.path)
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
