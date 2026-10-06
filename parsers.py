from __future__ import annotations
import re
from typing import Optional
from exceptions import ExpenseParseError, InvalidStateCodeError

STATE_CODE_PATTERN=re.compile(r"^FC\/\d{2}[A-C]\/\d{4}$",re.I)
EMAIL_PATTERN=re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_PATTERN=re.compile(r"^(?:\+234|0)\d{10}$")
AMOUNT_PATTERN=re.compile(r"(?:₦|NGN|N)?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",re.I)
CATEGORY_ALIASES={"transport":"Transport","transportation":"Transport","bus":"Transport","uber":"Transport","bolt":"Transport","fuel":"Transport","food":"Food","meal":"Food","meals":"Food","lunch":"Food","dinner":"Food","breakfast":"Food","data":"Data","internet":"Data","airtime":"Data","accommodation":"Accommodation","rent":"Accommodation","lodging":"Accommodation","saving":"Savings","savings":"Savings","investment":"Savings","other":"Other"}

def validate_state_code(value:str)->str:
    value=value.strip().upper()
    if not STATE_CODE_PATTERN.fullmatch(value): raise InvalidStateCodeError("State code must follow FC/YYX/NNNN, for example FC/26A/1234.")
    return value

def validate_email(value:str)->str:
    value=value.strip()
    if not EMAIL_PATTERN.fullmatch(value): raise ValueError("Enter a valid email address.")
    return value

def sanitize_phone(value:str)->str:
    value=re.sub(r"[\s()\-]","",value.strip())
    if value.startswith("+234"): value="0"+value[4:]
    if not PHONE_PATTERN.fullmatch(value): raise ValueError("Phone number must look like 08012345678 or +2348012345678.")
    return value

def _parse_amount(text:str)->Optional[float]:
    m=AMOUNT_PATTERN.search(text)
    return float(m.group(1).replace(",","")) if m else None

def _parse_category(text:str)->Optional[str]:
    lowered=text.lower()
    phrase=re.search(r"\b(?:on|for|in)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",lowered)
    candidates=[phrase.group(1).strip()] if phrase else []
    candidates += re.findall(r"[a-zA-Z]+",lowered)
    for c in candidates:
        if c in CATEGORY_ALIASES: return CATEGORY_ALIASES[c]
    return None

def parse_expense_text(text:str)->dict:
    if not text or not text.strip(): raise ExpenseParseError("Please enter a spending sentence.")
    amount=_parse_amount(text); category=_parse_category(text)
    if amount is None or amount<=0: raise ExpenseParseError("I could not find a positive monetary amount in that sentence.")
    if category is None: raise ExpenseParseError("I could not identify the category. Use Transport, Food, Data, Accommodation, Savings, or Other.")
    return {"amount":amount,"category":category,"description":text.strip(),"source":"quick-text"}
