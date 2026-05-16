"""Module D -- YAML-driven compliance rule engine with hot-reload.

Evaluates RBI / PMLA / FIU-IND rules against transactions.
Rules edited in compliance_rules.yaml take effect within ~5 seconds
via watchdog file watcher.

Rule format in YAML:
  rules:
    - id: RULE_ID
      description: "Human-readable description"
      field: amount          # transaction field to check
      op: gt                 # gt | lt | eq | gte | lte | in
      value: 500000          # comparison value
      action: FLAG           # FLAG | ALERT | FREEZE
      severity: HIGH         # HIGH | MEDIUM | LOW
"""

from __future__ import annotations

import threading
from pathlib import Path

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

_SEVERITY_SCORE = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.2}
_OPS = {
    "gt": lambda a, b: float(a) > float(b),
    "lt": lambda a, b: float(a) < float(b),
    "gte": lambda a, b: float(a) >= float(b),
    "lte": lambda a, b: float(a) <= float(b),
    "eq": lambda a, b: str(a) == str(b),
    "in": lambda a, b: str(a) in (b if isinstance(b, list) else [b]),
}


class ComplianceEngine:
    def __init__(self, rules_path: Path, start_watcher: bool = True) -> None:
        self.rules_path = Path(rules_path)
        self._rules: list[dict] = []
        self._lock = threading.RLock()
        self._load()
        if start_watcher:
            self._start_watcher()

    def _load(self) -> None:
        with self._lock:
            try:
                with self.rules_path.open() as f:
                    data = yaml.safe_load(f) or {}
                self._rules = data.get("rules", [])
            except Exception:
                self._rules = []

    def _start_watcher(self) -> None:
        observer = Observer()
        handler = _ReloadHandler(self._load, self.rules_path.name)
        observer.schedule(handler, str(self.rules_path.parent), recursive=False)
        observer.daemon = True
        observer.start()

    def evaluate(self, txn: dict) -> list[dict]:
        """Return list of matched rule results for a transaction dict."""
        matched = []
        with self._lock:
            rules = list(self._rules)
        for rule in rules:
            field = rule.get("field", "")
            op_name = rule.get("op", "")
            value = rule.get("value")
            op_fn = _OPS.get(op_name)
            if op_fn is None or field not in txn:
                continue
            try:
                if op_fn(txn[field], value):
                    matched.append({
                        "rule_id": rule.get("id", "UNKNOWN"),
                        "description": rule.get("description", ""),
                        "action": rule.get("action", "FLAG"),
                        "severity": rule.get("severity", "LOW"),
                    })
            except Exception:
                continue
        return matched

    def compliance_score(self, txn: dict) -> float:
        """Return a 0-1 risk score based on matched rules."""
        results = self.evaluate(txn)
        if not results:
            return 0.0
        max_sev = max(_SEVERITY_SCORE.get(r["severity"], 0.1) for r in results)
        # Scale: any match => at least 0.3, max severity HIGH => 1.0
        return min(1.0, 0.3 + max_sev * 0.7)


class _ReloadHandler(FileSystemEventHandler):
    def __init__(self, callback, filename: str) -> None:
        self._callback = callback
        self._filename = filename

    def on_modified(self, event) -> None:
        if not event.is_directory and event.src_path.endswith(self._filename):
            self._callback()
