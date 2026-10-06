# Smart NYSC Allawee & Expense Copilot (AllaweeBot)

AllaweeBot is an interactive Python/Streamlit application designed to help NYSC corps members record expenses, monitor monthly spending limits, benchmark purchasing power, and receive personalized financial guidance.

## Project

- **Course:** Python Advanced
- **Organization:** NCAIR Internship
- **Group:** 27
- **Project title:** Smart NYSC Allawee & Expense Copilot (AllaweeBot)

## Main features

- Object-Oriented Programming models for users, corps members, expenses, and budgets
- Regular-expression validation and natural-language expense parsing
- Category-based allowance limits and overspending warnings
- JSON persistence and CSV/text reports
- Exception handling for invalid input, files, and external services
- Streamlit dashboard with Plotly visualizations
- Optional Google Gemini financial copilot
- USD/NGN purchasing-power benchmark using ExchangeRate-API

## Technology stack

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- Google Gemini API
- ExchangeRate-API
- JSON / CSV
- Git and GitHub

## Project structure

```text
Allawee-Bot/
├── app.py
├── models.py
├── budget.py
├── parsers.py
├── storage.py
├── reports.py
├── services.py
├── exceptions.py
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
├── exports/
└── tests/
```

## Local setup

Create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file from `.env.example` and add your Gemini API key if AI features are required.

Run the application:

```powershell
streamlit run app.py
```

Run tests:

```powershell
pytest -q
```

## Git workflow

The project is intended to use a main branch plus feature branches:

- `feature/core-oop`
- `feature/budget-engine`
- `feature/regex-validation`
- `feature/file-handling`
- `feature/exception-handling`
- `feature/streamlit-ui`
- `feature/gemini-ai`
- `feature/public-api`

Changes should be developed on feature branches and merged into `main) through pull requests.

## Group member currently recorded

| Member | Responsibility / Branch |
|---|---|
| Daniel Aisosa Idemudia | Group Leader — `feature/core-oop` |
| Paul Oloche | Group member — assignment to be confirmed |

> Do not commit API keys or other secrets to this repository. The local `.env` file is ignored by Git.

## Project purpose

AllaweeBot addresses common budgeting difficulties faced by NYSC corps members, including transportation, food, data, accommodation, savings, and other day-to-day expenses.
