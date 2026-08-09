"""Resilient autonomous cycle scheduler."""
from __future__ import annotations

import threading
import time
from typing import Optional


class AutonomousScheduler:
    def __init__(self, pipeline, interval_seconds: int = 1800, top_count: int = 5, enrich: bool = True):
        self.pipeline = pipeline
        self.interval_seconds = max(10, int(interval_seconds))
        self.top_count = top_count
        self.enrich = enrich
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.last_result = None
        self.last_error: Optional[str] = None
        self.running = False

    def start(self, run_immediately: bool = True):
        if self.running:
            return
        self._stop.clear()
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="autonomous-news-cycle")
        self._thread.start()
        if not run_immediately:
            return

    def stop(self, timeout: float = 5.0):
        self._stop.set()
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)

    def _loop(self):
        first = True
        try:
            while not self._stop.is_set():
                if first:
                    first = False
                else:
                    if self._stop.wait(self.interval_seconds):
                        break
                try:
                    self.last_result = self.pipeline.run(
                        top_count=self.top_count,
                        enrich=self.enrich,
                    )
                    self.last_error = None
                except Exception as exc:  # isolate one bad cycle
                    self.last_error = str(exc)
                    try:
                        persona = self.pipeline.persona_engine.get_persona()
                        if persona:
                            persona.state.last_error = str(exc)
                    except Exception:
                        pass
        finally:
            self.running = False
