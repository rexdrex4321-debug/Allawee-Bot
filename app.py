import streamlit as st
import pandas as pd
from datetime import date
from budget import BudgetTracker,DEFAULT_CATEGORY_PERCENTAGES
from models import CorperUser,Expense
from parsers import validate_email,sanitize_phone,validate_state_code,parse_expense_text
from storage import AccountStore,ProfileStore
from auth import hash_password,verify_password,make_user_id
from email_service import EmailService
from services import GeminiService,ExchangeRateService
from exceptions import AllaweeBotError,ExpenseParseError,InsufficientAllaweeError
from reports import build_text_report

st.set_page_config(page_title="AllaweeBot",page_icon="💰",layout="wide")
accounts=AccountStore(); profiles=ProfileStore(); mailer=EmailService()

def money(v): return f"₦{v:,.2f}"

def logout():
    for key in ["authenticated","user_id","profile","expenses","percentages","baseline"]:
        st.session_state.pop(key,None)
    st.rerun()

def load_user(user_id):
    st.session_state.user_id=user_id
    st.session_state.profile=profiles.profile(user_id)
    st.session_state.expenses=profiles.expenses(user_id)
    pct,base=profiles.settings(user_id)
    st.session_state.percentages=pct or DEFAULT_CATEGORY_PERCENTAGES.copy()
    st.session_state.baseline=base
    st.session_state.authenticated=True

if not st.session_state.get("authenticated"):
    st.title("💰 AllaweeBot")
    st.subheader("Your NYSC allowance and expense copilot")
    login_tab,signup_tab=st.tabs(["🔐 Login","🆕 Create account"])
    with login_tab:
        email=st.text_input("Email",key="login_email")
        password=st.text_input("Password",type="password",key="login_password")
        if st.button("Login",type="primary",use_container_width=True):
            try:
                uid=make_user_id(validate_email(email))
                record=accounts.get(uid)
                if not record or not verify_password(password,record["password_hash"]):
                    st.error("Invalid email or password.")
                else:
                    load_user(uid); st.rerun()
            except ValueError as e: st.error(str(e))
    with signup_tab:
        name=st.text_input("Full name",key="signup_name")
        email=st.text_input("Email address",key="signup_email")
        password=st.text_input("Password (8+ characters)",type="password",key="signup_password")
        confirm=st.text_input("Confirm password",type="password",key="signup_confirm")
        phone=st.text_input("Phone number",key="signup_phone")
        if st.button("Create account",type="primary",use_container_width=True):
            try:
                email=validate_email(email)
                if password!=confirm: raise ValueError("Passwords do not match.")
                uid=make_user_id(email)
                accounts.create(uid,{"id":uid,"email":email,"password_hash":hash_password(password),"name":name.strip()})
                st.session_state.pending_account=(uid,email,name.strip(),phone)
                st.success("Account created. Complete your NYSC profile after logging in.")
            except ValueError as e: st.error(str(e))
    st.info("Your password is stored as a secure PBKDF2 hash, not plain text.")
    st.stop()

profile=st.session_state.get("profile")
if not profile:
    st.title("👋 Welcome to AllaweeBot")
    st.write("Complete your profile to start tracking your allowance.")
    with st.form("profile_setup"):
        name=st.text_input("Full name",value=accounts.get(st.session_state.user_id).get("name",""))
        email=st.text_input("Email",value=accounts.get(st.session_state.user_id)["email"],disabled=True)
        phone=st.text_input("Phone")
        state=st.text_input("Deployment state",value="Anambra")
        code=st.text_input("NYSC State Code",value="FC/26A/1234")
        ppa=st.text_input("PPA")
        allowance=st.number_input("Monthly allowance (₦)",min_value=0.0,value=77000.0,step=1000.0)
        if st.form_submit_button("Save and open home",type="primary"):
            try:
                p=CorperUser(name=name.strip(),email=validate_email(email),phone=sanitize_phone(phone),state=state.strip(),state_code=validate_state_code(code),ppa=ppa.strip(),monthly_allowance=float(allowance))
                st.session_state.profile=p; st.session_state.expenses=[]; st.session_state.percentages=DEFAULT_CATEGORY_PERCENTAGES.copy(); st.session_state.baseline=None
                profiles.save_user_data(st.session_state.user_id,p,[],st.session_state.percentages)
                st.rerun()
            except ValueError as e: st.error(str(e))
    st.stop()

t=BudgetTracker(profile,st.session_state.percentages)
total=t.total_spent(st.session_state.expenses); balance=t.remaining_balance(st.session_state.expenses)

with st.sidebar:
    st.title("💰 AllaweeBot")
    st.caption(f"Signed in as {profile.name}")
    page=st.radio("Menu",["🏠 Home","➕ Add Expense","💳 Expenses","🤖 AI Copilot","📊 Reports","👤 Profile & Account"])
    if st.button("Log out",use_container_width=True): logout()

def persist():
    profiles.save_user_data(st.session_state.user_id,st.session_state.profile,st.session_state.expenses,st.session_state.percentages,st.session_state.baseline)

if page=="🏠 Home":
    st.title(f"Welcome back, {profile.name.split()[0]} 👋")
    st.caption("Your personal NYSC financial dashboard")
    a,b,c,d=st.columns(4)
    a.metric("Monthly allowance",money(profile.monthly_allowance))
    b.metric("Spent",money(total))
    c.metric("Balance",money(balance))
    d.metric("Transactions",len(st.session_state.expenses))
    st.subheader("Budget status")
    st.dataframe(pd.DataFrame(t.category_status(st.session_state.expenses)),use_container_width=True,hide_index=True)
    st.subheader("Recent expenses")
    recent=st.session_state.expenses[-5:][::-1]
    if recent: st.dataframe(pd.DataFrame([e.to_dict() for e in recent]),use_container_width=True,hide_index=True)
    else: st.info("No expenses yet. Use Add Expense to record your first one.")

elif page=="➕ Add Expense":
    st.title("Add an expense")
    text=st.text_input("Describe it",placeholder="Spent 3000 on transport")
    if st.button("Parse and add expense",type="primary"):
        try:
            e=Expense(**parse_expense_text(text),spent_at=str(date.today()))
            t.add_expense(st.session_state.expenses,e); persist()
            st.success(f"Added {money(e.amount)} under {e.category}.")
            st.rerun()
        except (ExpenseParseError,InsufficientAllaweeError) as e: st.error(str(e))

elif page=="💳 Expenses":
    st.title("Expense history")
    if st.session_state.expenses: st.dataframe(pd.DataFrame([e.to_dict() for e in st.session_state.expenses]),use_container_width=True,hide_index=True)
    else: st.info("No expenses recorded yet.")

elif page=="🤖 AI Copilot":
    st.title("AI Copilot")
    if st.button("Generate advice",type="primary"):
        st.markdown(GeminiService().get_advice(state=profile.state,balance=balance,spent=total,category_rows=t.category_status(st.session_state.expenses),ppa=profile.ppa))
    try:
        info=ExchangeRateService().get_usd_ngn_rate()
        st.metric("Allowance value in USD",f"USD {profile.monthly_allowance/info['rate']:,.2f}")
    except AllaweeBotError as e: st.warning(str(e))

elif page=="📊 Reports":
    st.title("Reports")
    report=build_text_report(profile,st.session_state.expenses,balance)
    st.download_button("Download report",report,file_name="allaweebot_report.txt")
    st.code(report)

elif page=="👤 Profile & Account":
    st.title("Profile & Account")
    with st.form("edit_profile"):
        name=st.text_input("Full name",value=profile.name)
        phone=st.text_input("Phone",value=profile.phone)
        state=st.text_input("Deployment state",value=profile.state)
        code=st.text_input("NYSC State Code",value=profile.state_code)
        ppa=st.text_input("PPA",value=profile.ppa)
        allowance=st.number_input("Monthly allowance (₦)",min_value=0.0,value=float(profile.monthly_allowance),step=1000.0)
        if st.form_submit_button("Save profile changes"):
            try:
                st.session_state.profile=CorperUser(name=name.strip(),email=profile.email,phone=sanitize_phone(phone),state=state.strip(),state_code=validate_state_code(code),ppa=ppa.strip(),monthly_allowance=float(allowance))
                persist(); st.success("Profile updated.")
            except ValueError as e: st.error(str(e))
    st.divider()
    st.subheader("Change password")
    with st.form("password_form"):
        current=st.text_input("Current password",type="password")
        new=st.text_input("New password",type="password")
        confirm=st.text_input("Confirm new password",type="password")
        if st.form_submit_button("Change password"):
            record=accounts.get(st.session_state.user_id)
            if not verify_password(current,record["password_hash"]): st.error("Current password is incorrect.")
            elif new!=confirm: st.error("New passwords do not match.")
            else:
                record["password_hash"]=hash_password(new); accounts.update(st.session_state.user_id,record); st.success("Password changed.")
    st.divider()
    st.subheader("Email notifications")
    st.write("Send a real email using the SMTP settings in your local .env file.")
    if mailer.configured:
        if st.button("Send test email"):
            try:
                mailer.send(profile.email,"AllaweeBot test email",f"Hello {profile.name}, your AllaweeBot email notifications are working.")
                st.success("Test email sent.")
            except Exception as e: st.error(f"Email could not be sent: {e}")
    else:
        st.info("SMTP is not configured yet. Copy .env.example to .env and add your SMTP credentials.")
