# CoinSight AI – Project Overview

## General Overview

CoinSight AI is a full-stack application that provides users with a personalized cryptocurrency dashboard. Its daily content is tailored to each user's interests, investor profile, and selected crypto assets.

## Registration, Login, and Personalization

The user experience begins with secure registration and login. After signing in for the first time, the user completes a short onboarding process in which they select:

- The cryptocurrencies they are interested in
- Their investor type
- Their preferred content types

These preferences are stored in a PostgreSQL database and are later used to personalize the dashboard.

## Dashboard Content

The dashboard contains four main content areas:

1. Live market data
2. Market news
3. AI Insight
4. A daily crypto meme

Cryptocurrency prices are retrieved from CoinGecko and filtered according to the assets selected by the user. News items are prioritized using the same preferences, while the AI Insight combines the user's investor type, selected assets, and current market data to generate a short, personalized insight through OpenRouter.

## Daily Content

AI Insight and Crypto Mood operate through a daily-content mechanism. Each user receives one AI Insight and one meme per day.

The content is stored in the database and returned consistently throughout the same day, while live market data continues to update independently. The first time the user opens the dashboard on a new day, new daily content is generated and stored.

## Personalized Content Ordering

The dashboard is also personalized according to the user's content preferences. All four content areas remain available, but the full sections are ordered so that the user's preferred content appears first.

The **Today at a Glance** area and persistent navigation bar provide quick access to every dashboard section.

## User Feedback

Users can provide feedback using 👍 or 👎 on:

- News
- AI Insight
- Crypto Mood

Feedback is stored per user and content item, and may be used in the future to improve the recommendation mechanism. An automatic recommendation model has not yet been implemented at the current stage.

## Core Technologies

### Frontend

- React
- Vite
- JavaScript
- React Router
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- JWT-based authentication

### Database

- PostgreSQL
- Supabase

### External Services

- CoinGecko
- OpenRouter
- Meme API

## Additional Capabilities

The system also includes:

- External service failure handling
- Fallback mechanisms
- Protected routes
- Responsive design
- Accessibility support
- Automated tests for the application's main flows
