# AI Crypto Advisor

An AI-powered cryptocurrency advisory application with separate frontend and backend components.

## Frontend

## Backend

## Setup

## Testing

Backend tests:

```powershell
cd backend
python -m pytest
```

Frontend tests:

```powershell
cd frontend
npm run test -- --run
```

Coverage reports are available with `python -m pytest --cov=app --cov-report=term-missing` in `backend` and `npm run test:coverage` in `frontend`.

The automated suite mocks CoinGecko, OpenRouter, and the Meme API. Daily behavior is tested with injected dates, so live services and Supabase are not required.
