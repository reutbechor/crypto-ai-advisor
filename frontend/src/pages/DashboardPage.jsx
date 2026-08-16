import { useCallback, useEffect, useRef, useState } from 'react'
import AIInsightSection from '../components/AIInsightSection.jsx'
import Brand from '../components/Brand.jsx'
import CryptoMoodSection from '../components/CryptoMoodSection.jsx'
import DashboardNav from '../components/DashboardNav.jsx'
import DashboardOverview from '../components/DashboardOverview.jsx'
import DashboardSkeleton from '../components/DashboardSkeleton.jsx'
import MarketCard from '../components/MarketCard.jsx'
import NewsCard from '../components/NewsCard.jsx'
import NewsModal from '../components/NewsModal.jsx'
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

const dashboardSectionIds = ['overview', 'market', 'news', 'ai-insight', 'meme']

function DashboardPage() {
  const { logout, token, user } = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [selectedNewsItem, setSelectedNewsItem] = useState(null)
  const [activeSection, setActiveSection] = useState('overview')
  const hasLoaded = useRef(false)
  const newsTriggerRef = useRef(null)
  const navigationLockRef = useRef(null)
  const navigationUnlockTimeoutRef = useRef(null)

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

  const openNewsModal = useCallback((item, event) => {
    newsTriggerRef.current = event.currentTarget
    setSelectedNewsItem(item)
  }, [])

  const closeNewsModal = useCallback(() => {
    setSelectedNewsItem(null)
    window.requestAnimationFrame(() => newsTriggerRef.current?.focus())
  }, [])

  const navigateToSection = useCallback((sectionId) => {
    const section = document.getElementById(sectionId)
    if (!section) {
      return
    }

    window.clearTimeout(navigationUnlockTimeoutRef.current)
    navigationLockRef.current = sectionId
    setActiveSection(sectionId)

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    section.scrollIntoView({
      behavior: prefersReducedMotion ? 'auto' : 'smooth',
      block: 'start',
    })
    section.focus({ preventScroll: true })
    navigationUnlockTimeoutRef.current = window.setTimeout(() => {
      navigationLockRef.current = null
    }, prefersReducedMotion ? 100 : 1400)
  }, [])

  useEffect(() => {
    if (hasLoaded.current) {
      return
    }
    hasLoaded.current = true
    loadDashboard()
  }, [loadDashboard])

  useEffect(() => () => window.clearTimeout(navigationUnlockTimeoutRef.current), [])

  useEffect(() => {
    if (!dashboard) {
      return undefined
    }

    const sections = dashboardSectionIds
      .map((sectionId) => document.getElementById(sectionId))
      .filter(Boolean)

    const observer = new IntersectionObserver(
      (entries) => {
        if (navigationLockRef.current) {
          return
        }

        const visibleSection = entries
          .filter((entry) => entry.isIntersecting)
          .sort((first, second) => second.intersectionRatio - first.intersectionRatio)[0]

        if (visibleSection) {
          setActiveSection(visibleSection.target.id)
        }
      },
      {
        rootMargin: '-72px 0px -58% 0px',
        threshold: [0, 0.1, 0.3],
      },
    )

    sections.forEach((section) => observer.observe(section))
    return () => observer.disconnect()
  }, [dashboard])

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

        {!isLoading && dashboard && !hasError && (
          <DashboardNav activeSection={activeSection} onNavigate={navigateToSection} />
        )}

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
            <section
              className="dashboard-welcome"
              id="overview"
              aria-labelledby="dashboard-title"
              tabIndex="-1"
            >
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

            <DashboardOverview dashboard={dashboard} onNavigate={navigateToSection} />

            <section
              className="dashboard-market dashboard-anchor-section"
              id="market"
              aria-labelledby="market-title"
              tabIndex="-1"
            >
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

            <section
              className="dashboard-news dashboard-anchor-section"
              id="news"
              aria-labelledby="news-title"
              tabIndex="-1"
            >
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
                    <NewsCard item={item} key={item.id} onRead={openNewsModal} />
                  ))}
                </div>
              )}
            </section>

            <AIInsightSection
              insight={dashboard.ai_insight}
              status={dashboard.ai_status}
            />

            <CryptoMoodSection meme={dashboard.meme} />
          </div>
        )}

        {selectedNewsItem && (
          <NewsModal item={selectedNewsItem} onClose={closeNewsModal} />
        )}
      </div>
    </main>
  )
}

export default DashboardPage
