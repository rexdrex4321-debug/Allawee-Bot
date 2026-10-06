# Beginner Setup
1. Install Python 3.10 or newer.
2. Create a virtual environment: py -m venv .venv
3. Activate on Windows: .\\.venv\\Scripts\\Activate.ps1
4. Install dependencies: pip install -r requirements.txt
5. Copy .env.example to .env if Gemini is required.
6. Start the app: streamlit run app.py
7. Run tests: pytest -q
Never commit API keys or the local .env file.
