# CoinSight AI

A full-stack personalized crypto dashboard combining live market data, curated news, daily AI insights, and community feedback.

## Live Demo

[Open CoinSight AI](https://monumental-macaron-ceac17.netlify.app/)

## Tech Stack

- **Frontend:** React, Vite, React Router, JavaScript, CSS
- **Backend:** FastAPI, SQLAlchemy, JWT authentication
- **Database:** PostgreSQL on Supabase
- **Integrations:** CoinGecko, OpenRouter, Meme API

## Run Locally

Copy the example environment files before starting each application.

```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

```powershell
# Frontend - run in a second terminal
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

- Frontend: `http://localhost:5173`
- API documentation: `http://127.0.0.1:8000/docs`

## Tests

```powershell
# From backend/
python -m pytest

# From frontend/
npm run test -- --run
```

External providers are mocked in the automated test suite.

## Documentation

- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Technical Overview](docs/TECHNICAL_OVERVIEW.md)
- [User Guide](docs/USER_GUIDE.md)
- [AI Usage Summary](docs/AI_USAGE.md)
- [Backend Setup](backend/README.md)
