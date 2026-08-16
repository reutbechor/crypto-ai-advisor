import DailyDateLabel from './DailyDateLabel.jsx'

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

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})

function AIInsightSection({ dailyDate, insight, status }) {
  const isGenerated = status === 'available'

  return (
    <section
      className="dashboard-ai-insight"
      id="ai-insight"
      aria-labelledby="ai-insight-title"
      tabIndex="-1"
    >
      <header className="ai-insight-heading">
        <div>
          <p className="eyebrow">{isGenerated ? 'AI generated' : 'Market insight'}</p>
          <h2 id="ai-insight-title">AI Insight</h2>
        </div>
        <div className="ai-insight-heading-meta">
          <p>Personalized perspective based on your profile and followed assets.</p>
          <DailyDateLabel date={dailyDate} label="Daily AI Insight" />
        </div>
      </header>

      {insight ? (
        <article className="ai-insight-content">
          <aside className="ai-insight-context" aria-label="Insight personalization">
            <span className="ai-state-label">
              {isGenerated ? 'Generated with AI' : 'Personalized fallback'}
            </span>
            <strong>{investorLabels[insight.generated_for.investor_type]}</strong>
            <div>
              {insight.generated_for.crypto_assets.map((asset) => (
                <span key={asset}>{assetLabels[asset]}</span>
              ))}
            </div>
            <time dateTime={insight.generated_at}>
              {dateFormatter.format(new Date(insight.generated_at))}
            </time>
          </aside>

          <div className="ai-insight-copy">
            <h3>{insight.title}</h3>
            {insight.content.split('\n\n').map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
          </div>
        </article>
      ) : (
        <div className="ai-insight-unavailable" role="status">
          Insight is temporarily unavailable.
        </div>
      )}
    </section>
  )
}

export default AIInsightSection
