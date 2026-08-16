import MemeImage from './MemeImage.jsx'


const usdFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
})

const assetLabels = {
  bitcoin: 'Bitcoin',
  ethereum: 'Ethereum',
  solana: 'Solana',
  cardano: 'Cardano',
  ripple: 'XRP',
  general: 'Crypto Market',
}

function OverviewAction({ children, sectionId, onNavigate }) {
  return (
    <button type="button" onClick={() => onNavigate(sectionId)}>
      {children} <span aria-hidden="true">↓</span>
    </button>
  )
}

function createInsightPreview(content, maximumLength = 140) {
  if (!content || content.length <= maximumLength) {
    return content
  }

  const shortened = content.slice(0, maximumLength)
  const lastSpace = shortened.lastIndexOf(' ')
  return `${shortened.slice(0, lastSpace)}…`
}

function DashboardOverview({ dashboard, onNavigate }) {
  const marketCoins = dashboard.market.slice(0, 2)
  const topStory = dashboard.news[0]
  const aiInsight = dashboard.ai_insight
  const meme = dashboard.meme

  return (
    <section className="dashboard-glance" aria-labelledby="glance-title">
      <header className="glance-heading">
        <div>
          <p className="eyebrow">Overview</p>
          <h2 id="glance-title">Today at a Glance</h2>
        </div>
      </header>

      <div className="overview-grid">
        <article className="overview-card overview-card--market">
          <p className="overview-card-label">Your Market</p>
          {dashboard.market_status === 'unavailable' || marketCoins.length === 0 ? (
            <p className="overview-empty">Market data unavailable</p>
          ) : (
            <div className="overview-market-list">
              {marketCoins.map((coin) => {
                const isPositive = coin.price_change_percentage_24h >= 0
                return (
                  <div key={coin.id}>
                    <div>
                      <strong>{coin.name}</strong>
                      <span>{coin.symbol.toUpperCase()}</span>
                    </div>
                    <div>
                      <strong>{usdFormatter.format(coin.current_price)}</strong>
                      <span className={isPositive ? 'overview-change--positive' : 'overview-change--negative'}>
                        {isPositive ? '+' : ''}{coin.price_change_percentage_24h.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
          <OverviewAction sectionId="market" onNavigate={onNavigate}>View Market</OverviewAction>
        </article>

        <article className="overview-card overview-card--news">
          <p className="overview-card-label">Top Story</p>
          {!topStory || dashboard.news_status === 'unavailable' ? (
            <p className="overview-empty">News unavailable</p>
          ) : (
            <div className="overview-story">
              <span>{topStory.related_assets.map((asset) => assetLabels[asset]).join(' · ')}</span>
              <h3>{topStory.title}</h3>
            </div>
          )}
          <OverviewAction sectionId="news" onNavigate={onNavigate}>View News</OverviewAction>
        </article>

        <article className="overview-card overview-card--ai">
          <div className="overview-future-mark" aria-hidden="true">AI</div>
          <p className="overview-card-label">
            {dashboard.ai_status === 'available' ? 'AI Insight' : 'Market Insight'}
          </p>
          <h3>{aiInsight ? createInsightPreview(aiInsight.content) : 'Insight temporarily unavailable'}</h3>
          {aiInsight && (
            <span className="coming-label">
              {dashboard.ai_status === 'available' ? 'Personalized with AI' : 'Personalized fallback'}
            </span>
          )}
          <OverviewAction sectionId="ai-insight" onNavigate={onNavigate}>View AI</OverviewAction>
        </article>

        <article className="overview-card overview-card--meme">
          {meme && (
            <MemeImage
              className="overview-meme-image"
              src={meme.image_url}
              alt={meme.alt_text}
            />
          )}
          <p className="overview-card-label">Crypto Mood</p>
          <h3>{meme ? meme.title : 'Crypto mood is temporarily unavailable.'}</h3>
          <OverviewAction sectionId="meme" onNavigate={onNavigate}>View Meme</OverviewAction>
        </article>
      </div>
    </section>
  )
}

export default DashboardOverview
