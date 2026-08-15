# CoinSight AI Backend

FastAPI backend for the AI Crypto Advisor application.

## Stack

Python, FastAPI, and Uvicorn.

## Local setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Local URLs

- API: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/api/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
