## User Guide & Functionality

### Getting Started & Registration

When entering the website, the user arrives at the Welcome page, where they can either create a new account or sign in to an existing one.

During registration, the user enters their name, email, and password. After a successful signup, they are redirected to the Login page.

### Login & First-Time Access

After logging in, the system checks whether the user has already completed the onboarding process.

On the first login, the user is redirected to the Onboarding flow. On future logins, once their preferences have already been defined, they are taken directly to their personalized Dashboard.

### Onboarding & Personal Preferences

During onboarding, the user defines three types of preferences:

**Crypto Assets**  
For example: Bitcoin, Ethereum, Solana, Cardano, and XRP.

**Investor Type**  
For example: HODLer, Day Trader, or NFT Collector.

**Content Preferences**  
Market News, Coin Prices, AI Insights, and Fun.

These selections are saved and later used to personalize the Dashboard experience.

### Personalized Dashboard

After completing onboarding, the user enters their personalized Dashboard.

At the top of the page, a **Today at a Glance** section provides a quick overview of the four main content areas:

- Market
- Market News
- AI Insight
- Crypto Mood

A sticky navigation bar also allows the user to move directly between the different Dashboard sections without manually scrolling through the entire page.

### Dashboard Personalization

The system uses the user's preferences in two different ways.

The selected crypto assets affect the **content itself**. For example, a user who follows Bitcoin and Ethereum will receive market prices, news, and AI insights that focus mainly on those assets.

The selected content preferences affect the **order of the full Dashboard sections**. Preferred content types appear first, while the remaining sections are still available further down the page.

This allows the Dashboard to prioritize what is most relevant to each user without hiding any features.

### Market – Live Crypto Prices

The Market section displays current market data for the crypto assets selected during onboarding.

For each asset, the user can see information such as:

- Current price
- 24-hour price change
- Market cap

Market data is refreshed whenever the Dashboard is loaded.

### Market News

The Market News section displays market briefs that are prioritized according to the crypto assets the user follows.

The Dashboard shows a short preview for each article, including the headline and basic information. By clicking **Read Full Brief**, the user can open a modal and read the full article.

This keeps the Dashboard easy to scan while still allowing users to read more detailed content when they choose to.

### Daily AI Insight

The system provides a personalized AI-generated insight based on:

- The user's selected crypto assets
- The user's investor type
- Current market data

The insight is designed to provide market context and general information. It does not provide direct financial advice or buy/sell instructions.

Each user receives **one AI Insight per day**. Refreshing the page during the same day returns the same insight, while a new insight is created on the next day.

The date of the daily content is displayed in the Dashboard.

### Daily Crypto Mood

Each day, the user receives a crypto-related meme as part of the **Crypto Mood** section.

Similar to the AI Insight, the meme is stored as daily content. The same meme remains available throughout the day, even after refreshing the page or logging in again.

On a new day, a new meme is selected.

If the external meme provider is unavailable, the system can display a local fallback meme instead.

### Feedback

Users can provide thumbs-up or thumbs-down feedback on:

- Market News
- AI Insight
- Crypto Mood

The selected feedback is stored for the user and remains selected after refreshing the page.

Users can change their vote or remove it.

In the current version, feedback is collected and stored for future recommendation improvements. It does not yet automatically modify the recommendation logic.

### Daily Content vs. Live Content

The system distinguishes between content that should remain live and content that should remain stable throughout the day:

- **Market Prices** → refreshed whenever the Dashboard is loaded
- **AI Insight** → one personalized insight per user per day
- **Crypto Mood** → one meme per user per day
- **Market News** → personalized according to the user's selected assets