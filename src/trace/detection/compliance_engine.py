"""Module D — YAML-driven compliance rule engine with hot-reload.

Evaluates RBI / PMLA / FIU-IND rules. Rules edited in compliance_rules.yaml
take effect within 5 seconds (watchdog file watcher).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ComplianceEngine:
    def __init__(self, rules_path: Path):
        self.rules_path = rules_path
        self._rules: list[dict] = []
        self._load()
        self._start_watcher()

    def _load(self) -> None:
        with self.rules_path.open() as f:
            self._rules = yaml.safe_load(f).get("rules", [])

    def _start_watcher(self) -> None:
        observer = Observer()
        handler = _ReloadHandler(self._load)
        observer.schedule(handler, str(self.rules_path.parent), recursive=False)
        observer.daemon = True
        observer.start()

    def evaluate(self, txn: dict) -> list[dict]:
        """Return list of matched rules for this transaction."""
        raise NotImplementedError("First-match-wins evaluator with operator support.")


class _ReloadHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.src_path.endswith(".yaml"):
            self.callback()
