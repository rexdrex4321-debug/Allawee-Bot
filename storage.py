from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Any
from models import CorperUser, Expense


class DataManager:
    def __init__(self, file_path: str | Path = "data/budget.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def default_payload(self) -> dict[str, Any]:
        return {
            "profile": None,
            "expenses": [],
            "category_percentages": None,
            "exchange_baseline": None,
        }

    def load(self):
        if not self.file_path.exists():
            return self.default_payload()
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Stored data must be a JSON object.")
            return {**self.default_payload(), **data}
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            backup = self.file_path.with_suffix(".corrupt.json")
            try:
                backup.write_text(
                    self.file_path.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            except OSError:
                pass
            raise ValueError(f"Could not read budget data safely: {exc}") from exc

    def save(self, data):
        serialized = json.dumps(data, indent=2, ensure_ascii=False)
        tmp = self.file_path.with_suffix(".tmp")
        tmp.write_text(serialized, encoding="utf-8")

        # Windows can briefly lock the destination file (for example while
        # Streamlit/antivirus is accessing it). Retry the atomic replacement.
        last_error = None
        for attempt in range(5):
            try:
                os.replace(tmp, self.file_path)
                return
            except PermissionError as exc:
                last_error = exc
                if attempt == 4:
                    break
                time.sleep(0.1 * (attempt + 1))

        raise PermissionError(
            f"Could not replace {self.file_path}; it may be locked by another "
            "process. Close programs using the file and try again."
        ) from last_error

    def save_profile(self, profile, category_percentages, exchange_baseline=None):
        payload = self.load()
        payload["profile"] = profile.__dict__
        payload["category_percentages"] = category_percentages
        if exchange_baseline is not None:
            payload["exchange_baseline"] = exchange_baseline
        self.save(payload)

    def save_expenses(self, expenses):
        payload = self.load()
        payload["expenses"] = [e.to_dict() for e in expenses]
        self.save(payload)

    def load_profile(self):
        p = self.load()
        raw = p.get("profile")
        if not raw:
            return None, p.get("category_percentages"), p.get("exchange_baseline")
        return CorperUser(**raw), p.get("category_percentages"), p.get("exchange_baseline")

    def load_expenses(self):
        return [Expense(**e) for e in self.load().get("expenses", [])]
