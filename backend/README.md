# CoinSight AI Backend

FastAPI backend for CoinSight AI, backed by PostgreSQL through SQLAlchemy.

## Requirements

- Python 3.10+
- PostgreSQL

## Local setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
createdb -U postgres coinsight
Copy-Item .env.example .env
```

Update `.env` with your PostgreSQL username and password, then start the API:

```powershell
python -m uvicorn app.main:app --reload
```

## OpenRouter AI insight

Create an OpenRouter API key and add it only to `backend/.env`:

```env
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL=openrouter/free
```

Never commit `backend/.env`. When the key is absent or OpenRouter is unavailable,
the dashboard uses a deterministic personalized market insight instead.

## Verification

- Database health: `http://127.0.0.1:8000/api/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

The application creates the `users` table on startup when PostgreSQL is available.
