import { useCallback, useEffect, useRef, useState } from 'react'
import Brand from '../components/Brand.jsx'
import DashboardSkeleton from '../components/DashboardSkeleton.jsx'
import MarketCard from '../components/MarketCard.jsx'
import NewsCard from '../components/NewsCard.jsx'
import useAuth from '../hooks/useAuth.js'
import { ApiError } from '../services/apiClient.js'
import { getDashboard } from '../services/dashboardApi.js'


const assetLabels = {
  bitcoin: 'Bitcoin',
  ethereum: 'Ethereum',
  solana: 'Solana',
  cardano: 'Cardano',
  ripple: 'XRP',
}

const investorLabels = {
  hodler: 'HODLer',
  day_trader: 'Day Trader',
  nft_collector: 'NFT Collector',
}

const contentLabels = {
  market_news: 'Market News',
  coin_prices: 'Coin Prices',
  ai_insights: 'AI Insights',
  fun: 'Fun',
}

function DashboardPage() {
  const { logout, token, user } = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const hasLoaded = useRef(false)

  const loadDashboard = useCallback(async () => {
    setIsLoading(true)
    setHasError(false)

    try {
      const result = await getDashboard(token)
      setDashboard(result)
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        logout()
        return
      }
      setHasError(true)
    } finally {
      setIsLoading(false)
    }
  }, [logout, token])

  useEffect(() => {
    if (hasLoaded.current) {
      return
    }
    hasLoaded.current = true
    loadDashboard()
  }, [loadDashboard])

  const displayName = dashboard?.user.name || user.name
  const firstName = displayName.trim().split(/\s+/)[0]

  return (
    <main className="dashboard-page">
      <div className="dashboard-shell">
        <header className="dashboard-header">
          <Brand />
          <div className="dashboard-account">
            <div>
              <span>Personalized for you</span>
              <strong>{displayName}</strong>
            </div>
            <button className="dashboard-logout" type="button" onClick={logout}>
              Logout
            </button>
          </div>
        </header>

        {isLoading && <DashboardSkeleton />}

        {!isLoading && hasError && (
          <section className="dashboard-error" aria-labelledby="dashboard-error-title">
            <p className="eyebrow">Dashboard unavailable</p>
            <h1 id="dashboard-error-title">Unable to load your dashboard.</h1>
            <p>Please try again.</p>
            <button className="button button--primary" type="button" onClick={loadDashboard}>
              Try Again
            </button>
          </section>
        )}

        {!isLoading && dashboard && !hasError && (
          <div className="dashboard-content">
            <section className="dashboard-welcome" aria-labelledby="dashboard-title">
              <div>
                <p className="eyebrow">Your workspace</p>
                <h1 id="dashboard-title">Good to see you, {firstName}.</h1>
              </div>
              <div className="preference-summary" aria-label="Your saved preferences">
                <p>
                  {dashboard.preferences.crypto_assets
                    .map((asset) => assetLabels[asset])
                    .join(' · ')}
                </p>
                <strong>{investorLabels[dashboard.preferences.investor_type]}</strong>
                <div className="content-preference-list">
                  {dashboard.preferences.content_preferences.map((preference) => (
                    <span key={preference}>{contentLabels[preference]}</span>
                  ))}
                </div>
              </div>
            </section>

            <section className="dashboard-market" aria-labelledby="market-title">
              <header className="dashboard-section-heading">
                <div>
                  <h2 id="market-title">Your Market</h2>
                  <p>Live prices for the assets you follow.</p>
                </div>
                <span className="live-label">
                  <span aria-hidden="true" /> Live USD
                </span>
              </header>

              {dashboard.market_status === 'unavailable' ? (
                <div className="market-unavailable" role="status">
                  <div>
                    <h3>Market data is temporarily unavailable.</h3>
                    <p>Your preferences are safe. Try loading prices again.</p>
                  </div>
                  <button className="button button--secondary" type="button" onClick={loadDashboard}>
                    Try Again
                  </button>
                </div>
              ) : (
                <div className="market-grid">
                  {dashboard.market.map((coin) => (
                    <MarketCard coin={coin} key={coin.id} />
                  ))}
                </div>
              )}
            </section>

            <section className="dashboard-news" aria-labelledby="news-title">
              <header className="dashboard-section-heading">
                <div>
                  <h2 id="news-title">Market News</h2>
                  <p>Updates matched to the assets you follow.</p>
                </div>
                <span className="brief-label">Curated Market Briefs</span>
              </header>

              {dashboard.news_status === 'unavailable' || dashboard.news.length === 0 ? (
                <div className="news-unavailable" role="status">
                  <h3>News is temporarily unavailable.</h3>
                  <p>Your market data and saved preferences are still available.</p>
                </div>
              ) : (
                <div className="news-grid">
                  {dashboard.news.map((item) => (
                    <NewsCard item={item} key={item.id} />
                  ))}
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </main>
  )
}

export default DashboardPage
