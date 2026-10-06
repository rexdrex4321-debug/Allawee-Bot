from models import CorperUser,Expense
from budget import BudgetTracker
from parsers import parse_expense_text,validate_state_code,sanitize_phone
from exceptions import InsufficientAllaweeError,ExpenseParseError
from reports import build_text_report
from storage import DataManager,AccountStore,ProfileStore
from auth import hash_password,verify_password,make_user_id

def user(): return CorperUser("Test User","test@example.com","08012345678","Anambra","FC/26A/1234",monthly_allowance=77000)
def test_models(): assert Expense(100,"Food","Lunch").to_dict()["amount"]==100
def test_budget():
 t=BudgetTracker(user()); es=[Expense(3000,"Food","Lunch"),Expense(5000,"Transport","Bus")]; assert t.total_spent(es)==8000 and t.remaining_balance(es)==69000
def test_overrun():
 t=BudgetTracker(user()); es=[Expense(76000,"Food","Meals")]
 try: t.add_expense(es,Expense(2000,"Transport","Taxi")); assert False
 except InsufficientAllaweeError: assert len(es)==1
def test_parser(): assert parse_expense_text("Spent 3,000 on transport")["category"]=="Transport"
def test_parser_naira(): assert parse_expense_text("I spent ₦1,200 for food")["amount"]==1200
def test_parser_rejects_missing_category():
 try: parse_expense_text("Spent 5000"); assert False
 except ExpenseParseError: assert True
def test_validation(): assert validate_state_code("fc/26a/1234")=="FC/26A/1234" and sanitize_phone("+234 801-234-5678")=="08012345678"
def test_report(): assert "ALLAWEEBOT MONTHLY REPORT" in build_text_report(user(),[Expense(3000,"Food","Lunch")],74000)
def test_storage(tmp_path):
 m=DataManager(tmp_path/"budget.json"); m.save_profile(user(),{"Food":1.0}); m.save_expenses([Expense(2500,"Food","Lunch")]); p,pc,_=m.load_profile(); assert p.name=="Test User" and pc=={"Food":1.0} and m.load_expenses()[0].amount==2500
def test_missing_storage(tmp_path): assert DataManager(tmp_path/"missing.json").load()==DataManager(tmp_path/"missing.json").default_payload()
def test_password_hash_is_not_plaintext():
 h=hash_password("correct-horse"); assert h!="correct-horse" and verify_password("correct-horse",h) and not verify_password("wrong-pass",h)
def test_account_store(tmp_path):
 store=AccountStore(tmp_path/"accounts.json"); uid=make_user_id("TEST@example.com")
 store.create(uid,{"id":uid,"email":"test@example.com","password_hash":"hash","name":"Test"})
 assert store.get(uid)["name"]=="Test"
def test_profile_store(tmp_path):
 store=ProfileStore(tmp_path/"profiles"); p=user(); store.save_user_data("abc",p,[Expense(100,"Food","Snack")],{"Food":1.0})
 assert store.profile("abc").email=="test@example.com" and store.expenses("abc")[0].amount==100
