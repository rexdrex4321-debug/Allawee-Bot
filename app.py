import streamlit as st
import pandas as pd
from datetime import date
from budget import BudgetTracker,DEFAULT_CATEGORY_PERCENTAGES
from models import CorperUser,Expense
from parsers import validate_email,sanitize_phone,validate_state_code,parse_expense_text
from storage import DataManager
from services import GeminiService,ExchangeRateService
from exceptions import AllaweeBotError,ExpenseParseError,InsufficientAllaweeError
from reports import build_text_report
st.set_page_config(page_title="AllaweeBot",page_icon="💰",layout="wide")
manager=DataManager()
if "profile" not in st.session_state:
    p,pct,base=manager.load_profile(); st.session_state.profile=p; st.session_state.percentages=pct or DEFAULT_CATEGORY_PERCENTAGES.copy(); st.session_state.baseline=base; st.session_state.expenses=manager.load_expenses()
def persist():
    if st.session_state.profile: manager.save_profile(st.session_state.profile,st.session_state.percentages,st.session_state.baseline)
    manager.save_expenses(st.session_state.expenses)
def money(v): return f"₦{v:,.2f}"
st.title("💰 AllaweeBot"); st.caption("Smart NYSC Allawee & Expense Copilot")
with st.sidebar:
    st.header("Profile & Budget")
    allowance=st.number_input("Monthly allowance (₦)",min_value=0.0,value=float(st.session_state.profile.monthly_allowance if st.session_state.profile else 77000),step=1000.0)
    with st.expander("Edit profile",expanded=st.session_state.profile is None):
        name=st.text_input("Full name",value=st.session_state.profile.name if st.session_state.profile else "")
        email=st.text_input("Email",value=st.session_state.profile.email if st.session_state.profile else "")
        phone=st.text_input("Phone",value=st.session_state.profile.phone if st.session_state.profile else "")
        state=st.text_input("Deployment state",value=st.session_state.profile.state if st.session_state.profile else "Anambra")
        code=st.text_input("NYSC State Code",value=st.session_state.profile.state_code if st.session_state.profile else "FC/26A/1234")
        ppa=st.text_input("PPA",value=st.session_state.profile.ppa if st.session_state.profile else "")
        if st.button("Save profile & budget"):
            try:
                st.session_state.profile=CorperUser(name=name.strip(),email=validate_email(email),phone=sanitize_phone(phone),state=state,state_code=validate_state_code(code),ppa=ppa.strip(),monthly_allowance=float(allowance))
                persist(); st.success("Profile saved.")
            except ValueError as e: st.error(str(e))
if not st.session_state.profile:
    st.info("Create your profile in the sidebar to begin."); st.stop()
t=BudgetTracker(st.session_state.profile,st.session_state.percentages)
page=st.radio("Navigate",["Dashboard","Quick Log","Expenses","AI Copilot","Reports"],horizontal=True)
if page=="Dashboard":
    total=t.total_spent(st.session_state.expenses); balance=t.remaining_balance(st.session_state.expenses)
    a,b,c,d=st.columns(4); a.metric("Allowance",money(st.session_state.profile.monthly_allowance)); b.metric("Spent",money(total)); c.metric("Balance",money(balance)); d.metric("Transactions",len(st.session_state.expenses))
    st.dataframe(pd.DataFrame(t.category_status(st.session_state.expenses)),use_container_width=True,hide_index=True)
elif page=="Quick Log":
    text=st.text_input("Example: Spent 3000 on transport")
    if st.button("Parse and add expense",type="primary"):
        try:
            e=Expense(**parse_expense_text(text),spent_at=str(date.today())); t.add_expense(st.session_state.expenses,e); persist(); st.success(f"Added {money(e.amount)} under {e.category}.")
        except (ExpenseParseError,InsufficientAllaweeError) as e: st.error(str(e))
elif page=="Expenses":
    if st.session_state.expenses: st.dataframe(pd.DataFrame([e.to_dict() for e in st.session_state.expenses]),use_container_width=True,hide_index=True)
    else: st.info("No expenses recorded yet.")
elif page=="AI Copilot":
    total=t.total_spent(st.session_state.expenses); balance=t.remaining_balance(st.session_state.expenses)
    if st.button("Generate advice",type="primary"): st.markdown(GeminiService().get_advice(state=st.session_state.profile.state,balance=balance,spent=total,category_rows=t.category_status(st.session_state.expenses),ppa=st.session_state.profile.ppa))
    try:
        info=ExchangeRateService().get_usd_ngn_rate(); st.metric("Allowance value in USD",f"USD {st.session_state.profile.monthly_allowance/info['rate']:,.2f}")
    except AllaweeBotError as e: st.warning(str(e))
elif page=="Reports":
    report=build_text_report(st.session_state.profile,st.session_state.expenses,t.remaining_balance(st.session_state.expenses))
    st.download_button("Download report",report,file_name="allaweebot_report.txt"); st.code(report)
