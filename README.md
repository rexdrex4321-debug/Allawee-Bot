# Smart NYSC Allawee & Expense Copilot (AllaweeBot)

Python/Streamlit budgeting assistant for NYSC corps members. It records expenses, monitors a monthly allowance, validates quick expense text, persists data locally, generates reports, and optionally connects to Gemini and an exchange-rate API.

## Group 27

| Member | NYSC ID | Branch |
|---|---|---|
| Daniel Aisoa Idemudia | NC-NY-000493 | feature/core-oop |
| Ahmad Ibrahim | NC-NY-000519 | feature/budget-engine |
| Abdulrahman Idris | NC-SI-000815 | feature/regex-validation |
| Paul Oloche | NC-NY-000532 | feature/file-handling |
| Ajiroba Samuel | NC-SI-001019 | feature/exception-handling |
| Noel Kwufodu | NC-NY-000465 | feature/streamlit-ui |
| Pending | Pending | feature/gemini-ai |
| Pending | Pending | feature/public-api |

The final two identities remain pending until their names and NYSC IDs are supplied.

## Features
- OOP user and expense models
- Category-based budget tracking and allowance protection
- Regex validation and natural-language expense parsing
- JSON persistence and CSV/text reports
- Application-specific exception handling
- Streamlit dashboard
- Optional Gemini financial advice
- USD/NGN purchasing-power benchmark

## Setup
Create a virtual environment and install all project dependencies before running the app:
\n\n\`\`\`powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
\`\`\`
\nStart the Streamlit app with:
\n\`\`\`powershell
python -m streamlit run app.py
\`\`\`
\nRun automated tests with:
\n\`\`\`powershell
$env:PYTHONPATH = "."
python -m pytest -q
\`\`\`
\nIf PowerShell blocks virtual-environment activation, you can install the requirements without activating it by using the Python executable inside \`.venv\\Scripts\\python.exe\`.
\nCopy \`.env.example\` to a local \`.env\` file when using Gemini or SMTP email. Never commit \`.env\` or API keys.
\n## Git workflow
Development is organized into feature branches and merged to main through pull requests.
