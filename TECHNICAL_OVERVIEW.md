# Technical Overview – CoinSight AI

This document describes the technical structure of CoinSight AI and how the different parts of the system communicate with each other.

The application is built as a full-stack system with a React frontend, a FastAPI backend, a PostgreSQL database hosted on Supabase, and several external services for market data, AI-generated content, and memes.

The frontend is responsible for the user interface, navigation, data presentation, and authentication state.

The backend is responsible for:

- Authentication
- Database access
- Storing user preferences
- Dashboard personalization
- Integration with external APIs
- Daily content management
- Feedback persistence
- Returning unified dashboard data to the frontend

---

## Architecture

The general system architecture is:

```text
User
  ↓
React Frontend
  ↓
FastAPI Backend
  ↓
PostgreSQL / Supabase
```

The backend also communicates with external services:

```text
FastAPI Backend
   ├── CoinGecko
   ├── OpenRouter
   └── Meme API
```

The frontend does not communicate directly with these external providers. All communication with CoinGecko, OpenRouter, and the Meme API is handled by the backend.

This approach allows the application to:

- Keep API keys on the server side only
- Centralize error handling
- Validate external data before returning it to the client
- Provide a consistent response structure to the frontend
- Avoid coupling the UI directly to external API response formats

---

## Frontend Structure

The frontend is built with React and Vite.

General structure:

```text
frontend/
└── src/
    ├── components/
    ├── context/
    ├── hooks/
    ├── pages/
    ├── services/
    ├── utils/
    ├── App.jsx
    └── main.jsx
```

### Pages

The `pages` directory contains the main application screens.

Examples:

- `WelcomePage`
- `SignupPage`
- `LoginPage`
- `OnboardingPage`
- `DashboardPage`

Each page represents a main screen in the application and connects the relevant UI components with the data required for that screen.

### Components

The `components` directory contains reusable UI components.

Examples:

- `MarketCard`
- `NewsCard`
- `NewsModal`
- `AIInsightSection`
- `CryptoMoodSection`
- `DashboardNav`
- `DashboardOverview`
- `DailyDateLabel`
- `FeedbackButtons`

Splitting the UI into reusable components helps keep `DashboardPage` readable and separates responsibilities between different parts of the interface.

For example:

- `MarketCard` is responsible for displaying the data of a single cryptocurrency.
- `NewsModal` is responsible for displaying the full content of a Market Brief.
- `AIInsightSection` is responsible for displaying the full AI Insight.
- `CryptoMoodSection` is responsible for displaying the daily meme.

### Services

The `services` directory centralizes communication with the backend.

Examples:

- `authApi.js`
- `onboardingApi.js`
- `dashboardApi.js`
- `feedbackApi.js`

Instead of making `fetch` requests directly inside React components, API calls are handled through the service layer.

For example:

```text
DashboardPage
      ↓
dashboardApi.js
      ↓
FastAPI Backend
```

This separates:

- UI
- State management
- API communication

It also makes it easier to change backend communication without modifying presentation components.

### Context

`AuthContext` is used to manage the authenticated user state.

It stores values such as:

- `user`
- `token`
- `isAuthenticated`
- `loading`

It provides actions such as:

- `login()`
- `logout()`
- `updateUser()`
- `refreshUser()`

After a successful login, the JWT is stored in `sessionStorage`.

When the application loads again, the frontend uses the existing token to call:

```http
GET /api/auth/me
```

This restores the authenticated user.

### Protected Routes

The application uses route guard components to control access to different screens.

Examples:

- `ProtectedRoute`
- `PublicOnlyRoute`
- `IncompleteOnboardingRoute`

`ProtectedRoute` prevents unauthenticated users from accessing protected screens such as the Dashboard and Onboarding.

`PublicOnlyRoute` prevents authenticated users from returning to the Login or Signup pages.

`IncompleteOnboardingRoute` prevents users who have already completed onboarding from going through the onboarding flow again.

---

## Dashboard Frontend Flow

When the user opens the Dashboard:

```text
DashboardPage
      ↓
GET /api/dashboard
      ↓
dashboardApi.js
      ↓
Backend
```

The frontend receives one unified response containing the data required for the entire Dashboard, such as:

- `user`
- `preferences`
- `market`
- `news`
- `ai_insight`
- `meme`
- `daily_date`
- `feedback`

The same response is used for both **Today at a Glance** and the full Dashboard sections below it.

The frontend does not make additional requests just to display preview cards.

### Dashboard Section Ordering

The order of the full Dashboard sections is determined by:

```text
preferences.content_preferences
```

A mapping connects onboarding preferences to Dashboard sections:

| Onboarding preference | Dashboard section |
| --- | --- |
| `coin_prices` | `market` |
| `market_news` | `news` |
| `ai_insights` | `ai-insight` |
| `fun` | `meme` |

The sections selected by the user are displayed first. The remaining sections are then appended in the default order.

For example:

```text
Preferences:
fun
coin_prices

Result:
Meme
Market
News
AI Insight
```

No section is hidden.

The **Today at a Glance** area always continues to display previews of all four content types.
