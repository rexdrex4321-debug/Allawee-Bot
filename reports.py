from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path
from models import CorperUser,Expense
def export_csv(expenses:list[Expense],output_dir:str|Path="exports")->Path:
    d=Path(output_dir); d.mkdir(parents=True,exist_ok=True); p=d/f"allaweebot_expenses_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with p.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=["spent_at","category","amount","description","source"]); w.writeheader()
        for e in expenses: w.writerow(e.to_dict())
    return p
def build_text_report(user:CorperUser,expenses:list[Expense],balance:float)->str:
    total=sum(e.amount for e in expenses); cats={}
    for e in expenses: cats[e.category]=cats.get(e.category,0)+e.amount
    lines=["ALLAWEEBOT MONTHLY REPORT","="*32,f"Name: {user.name}",f"State: {user.state}",f"PPA: {user.ppa or 'Not provided'}",f"Allowance: ₦{user.monthly_allowance:,.2f}",f"Total spent: ₦{total:,.2f}",f"Remaining: ₦{balance:,.2f}","","Category totals:"]
    lines += [f"- {c}: ₦{a:,.2f}" for c,a in sorted(cats.items())]
    lines += ["","Transactions:"]+[f"{e.spent_at} | {e.category} | ₦{e.amount:,.2f} | {e.description}" for e in expenses]
    return "\n".join(lines)
def export_text(user,expenses,balance,output_dir="exports"):
    d=Path(output_dir); d.mkdir(parents=True,exist_ok=True); p=d/f"allaweebot_report_{datetime.now():%Y%m%d_%H%M%S}.txt"; p.write_text(build_text_report(user,expenses,balance),encoding="utf-8"); return p
