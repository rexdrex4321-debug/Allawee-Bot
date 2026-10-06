from __future__ import annotations
from collections import defaultdict
from typing import Iterable
from exceptions import InsufficientAllaweeError
from models import CorperUser, Expense

DEFAULT_CATEGORY_PERCENTAGES={"Transport":.20,"Food":.30,"Data":.10,"Accommodation":.20,"Savings":.10,"Other":.10}

class BudgetTracker:
    def __init__(self,user:CorperUser,category_percentages:dict[str,float]|None=None):
        self.user=user
        self.category_percentages=category_percentages or DEFAULT_CATEGORY_PERCENTAGES.copy()
        if abs(sum(self.category_percentages.values())-1)>0.001:
            raise ValueError("Category percentages must add up to 100%.")

    @property
    def category_limits(self):
        return {c:self.user.monthly_allowance*p for c,p in self.category_percentages.items()}

    @staticmethod
    def total_spent(expenses:Iterable[Expense])->float:
        return sum(e.amount for e in expenses)

    def spent_by_category(self,expenses:Iterable[Expense]):
        totals=defaultdict(float)
        for e in expenses: totals[e.category]+=e.amount
        return dict(totals)

    def remaining_balance(self,expenses):
        return self.user.monthly_allowance-self.total_spent(expenses)

    def add_expense(self,expenses:list[Expense],expense:Expense):
        current=self.total_spent(expenses)
        if current+expense.amount>self.user.monthly_allowance:
            raise InsufficientAllaweeError(f"This expense would exceed the allowance by ₦{current+expense.amount-self.user.monthly_allowance:,.2f}.")
        expenses.append(expense)

    def category_status(self,expenses):
        spent=self.spent_by_category(expenses)
        rows=[]
        for category,limit in self.category_limits.items():
            amount=spent.get(category,0.0); used=amount/limit*100 if limit else 0
            status="Over limit" if used>=100 else "Near limit" if used>=80 else "Healthy"
            rows.append({"Category":category,"Limit":limit,"Spent":amount,"Remaining":limit-amount,"Used %":used,"Status":status})
        return rows
