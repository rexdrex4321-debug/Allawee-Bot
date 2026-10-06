from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any
from models import CorperUser, Expense

def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
    last=None
    for attempt in range(5):
        try: os.replace(tmp,path); return
        except PermissionError as exc:
            last=exc
            if attempt==4: break
            time.sleep(0.1*(attempt+1))
    raise PermissionError(f"Could not replace {path}; it may be locked by another process.") from last

class DataManager:
    def __init__(self,file_path: str|Path="data/budget.json"):
        self.file_path=Path(file_path); self.file_path.parent.mkdir(parents=True,exist_ok=True)
    def default_payload(self): return {"profile":None,"expenses":[],"category_percentages":None,"exchange_baseline":None}
    def load(self):
        if not self.file_path.exists(): return self.default_payload()
        try:
            data=json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(data,dict): raise ValueError("Stored data must be a JSON object.")
            return {**self.default_payload(),**data}
        except (FileNotFoundError,json.JSONDecodeError,UnicodeDecodeError) as exc:
            raise ValueError(f"Could not read budget data safely: {exc}") from exc
    def save(self,data): _atomic_write(self.file_path,data)
    def save_profile(self,profile,category_percentages,exchange_baseline=None):
        payload=self.load(); payload["profile"]=profile.__dict__; payload["category_percentages"]=category_percentages
        if exchange_baseline is not None: payload["exchange_baseline"]=exchange_baseline
        self.save(payload)
    def save_expenses(self,expenses):
        payload=self.load(); payload["expenses"]=[e.to_dict() for e in expenses]; self.save(payload)
    def load_profile(self):
        p=self.load(); raw=p.get("profile")
        if not raw: return None,p.get("category_percentages"),p.get("exchange_baseline")
        return CorperUser(**raw),p.get("category_percentages"),p.get("exchange_baseline")
    def load_expenses(self): return [Expense(**e) for e in self.load().get("expenses",[])]

class AccountStore:
    def __init__(self,file_path: str|Path="data/accounts.json"):
        self.file_path=Path(file_path)
        self.file_path.parent.mkdir(parents=True,exist_ok=True)
    def _load(self):
        if not self.file_path.exists(): return {"users":{}}
        data=json.loads(self.file_path.read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {"users":{}}
    def _save(self,data): _atomic_write(self.file_path,data)
    def get(self,user_id): return self._load()["users"].get(user_id)
    def all_users(self): return list(self._load()["users"].values())
    def create(self,user_id,record):
        data=self._load()
        if user_id in data["users"]: raise ValueError("An account with this email already exists.")
        data["users"][user_id]=record; self._save(data)
    def update(self,user_id,record):
        data=self._load()
        if user_id not in data["users"]: raise KeyError("Account not found.")
        data["users"][user_id]=record; self._save(data)

class ProfileStore:
    def __init__(self,root: str|Path="data/profiles"):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def load(self,user_id):
        p=self.root/f"{user_id}.json"
        if not p.exists(): return {"profile":None,"expenses":[],"category_percentages":None,"exchange_baseline":None}
        return json.loads(p.read_text(encoding="utf-8"))
    def save(self,user_id,data): _atomic_write(self.root/f"{user_id}.json",data)
    def profile(self,user_id):
        raw=self.load(user_id).get("profile"); return CorperUser(**raw) if raw else None
    def expenses(self,user_id): return [Expense(**e) for e in self.load(user_id).get("expenses",[])]
    def settings(self,user_id):
        p=self.load(user_id); return p.get("category_percentages"),p.get("exchange_baseline")
    def save_user_data(self,user_id,profile,expenses,percentages,baseline=None):
        self.save(user_id,{"profile":profile.__dict__,"expenses":[e.to_dict() for e in expenses],"category_percentages":percentages,"exchange_baseline":baseline})
