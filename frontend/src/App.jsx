import './App.css'

const assets = [
  {
    symbol: 'BTC',
    name: 'Bitcoin',
    price: '$67,842.21',
    change: '+2.4%',
    direction: 'positive',
    bars: [38, 52, 44, 64, 58, 76, 68, 86, 79, 94],
  },
  {
    symbol: 'ETH',
    name: 'Ethereum',
    price: '$3,487.92',
    change: '-0.8%',
    direction: 'negative',
    bars: [72, 66, 78, 62, 57, 64, 48, 53, 44, 38],
  },
]

const features = [
  {
    number: '01',
    title: 'Personalized Insights',
    description:
      'Market context shaped around the assets, topics, and signals that matter to you.',
  },
  {
    number: '02',
    title: 'Real-Time Market Data',
    description:
      'A focused view of price movements and market activity without the noise.',
  },
  {
    number: '03',
    title: 'Smarter Recommendations',
    description:
      'AI-assisted takeaways that turn complex information into clear next steps.',
  },
]

function MiniChart({ bars, direction }) {
  return (
    <div className={`mini-chart mini-chart--${direction}`} aria-hidden="true">
      {bars.map((height, index) => (
        <span key={`${height}-${index}`} style={{ height: `${height}%` }} />
      ))}
    </div>
  )
}

function DashboardPreview() {
  return (
    <div className="preview-frame" id="preview">
      <div className="preview-glow" aria-hidden="true" />
      <section className="dashboard-card" aria-label="Mock crypto dashboard preview">
        <div className="dashboard-header">
          <div>
            <p className="dashboard-label">Market overview</p>
            <h2>Watchlist</h2>
          </div>
          <span className="mock-label">Mock data</span>
        </div>

        <div className="asset-list">
          {assets.map((asset) => (
            <article className="asset-row" key={asset.symbol}>
              <div className={`coin-mark coin-mark--${asset.symbol.toLowerCase()}`}>
                {asset.symbol.slice(0, 1)}
              </div>
              <div className="asset-name">
                <h3>{asset.name}</h3>
                <p>{asset.symbol}</p>
              </div>
              <MiniChart bars={asset.bars} direction={asset.direction} />
              <div className="asset-price">
                <strong>{asset.price}</strong>
                <span className={`change change--${asset.direction}`}>
                  {asset.change}
                </span>
              </div>
            </article>
          ))}
        </div>

        <article className="insight-card">
          <div className="insight-heading">
            <span className="insight-spark" aria-hidden="true">✦</span>
            <div>
              <p className="dashboard-label">Daily AI Insight</p>
              <h3>Momentum is building</h3>
            </div>
            <span className="confidence">82% confidence</span>
          </div>
          <p>
            Bitcoin is showing steady positive momentum while Ethereum remains
            range-bound. Watch volume near key resistance levels.
          </p>
        </article>
      </section>
    </div>
  )
}

function FeatureCard({ number, title, description }) {
  return (
    <article className="feature-card">
      <span className="feature-number" aria-hidden="true">{number}</span>
      <h3>{title}</h3>
      <p>{description}</p>
    </article>
  )
}

function App() {
  return (
    <div className="site-shell">
      <header className="site-header">
        <nav className="nav-container" aria-label="Primary navigation">
          <a className="brand" href="#top" aria-label="CoinSight AI home">
            <span className="brand-mark" aria-hidden="true">
              <span />
            </span>
            <span className="brand-copy">
              <strong>CoinSight AI</strong>
              <small>AI Crypto Advisor</small>
            </span>
          </a>

          <div className="nav-actions">
            <button className="button button--quiet" type="button">Sign In</button>
            <button className="button button--compact button--primary" type="button">
              Get Started
            </button>
          </div>
        </nav>
      </header>

      <main id="top">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-content">
            <p className="eyebrow">
              <span aria-hidden="true" />
              Personalized crypto intelligence
            </p>
            <h1 id="hero-title">
              Crypto insights,
              <span>personalized for you.</span>
            </h1>
            <p className="hero-description">
              CoinSight combines market data, breaking news, and AI-powered
              analysis to surface the insights that match your interests.
            </p>
            <div className="hero-actions">
              <button className="button button--primary button--large" type="button">
                Get Started
                <span aria-hidden="true">→</span>
              </button>
              <a className="button button--secondary button--large" href="#preview">
                Explore Dashboard
              </a>
            </div>
          </div>

          <DashboardPreview />
        </section>

        <section className="features" id="features" aria-labelledby="features-title">
          <div className="section-heading">
            <p className="section-kicker">A clearer market perspective</p>
            <h2 id="features-title">Intelligence that works around you</h2>
          </div>
          <div className="feature-grid">
            {features.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="footer-content">
          <a className="footer-brand" href="#top">CoinSight AI</a>
          <p>Built for the Moveo coding assignment</p>
        </div>
      </footer>
    </div>
  )
}

export default App
