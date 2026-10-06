from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any

@dataclass
class User:
    name: str
    email: str
    phone: str

@dataclass
class CorperUser(User):
    state: str
    state_code: str
    ppa: str = ""
    monthly_allowance: float = 77000.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

@dataclass
class Expense:
    amount: float
    category: str
    description: str
    spent_at: str = field(default_factory=lambda: date.today().isoformat())
    source: str = "manual"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
