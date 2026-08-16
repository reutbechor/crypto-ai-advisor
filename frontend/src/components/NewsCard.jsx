const assetLabels = {
  bitcoin: 'Bitcoin',
  ethereum: 'Ethereum',
  solana: 'Solana',
  cardano: 'Cardano',
  ripple: 'XRP',
  general: 'Crypto Market',
}

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
})

function NewsCard({ item, onRead }) {
  return (
    <article className="news-card">
      <div className="news-assets" aria-label="Related assets">
        {item.related_assets.map((asset) => (
          <span key={asset}>{assetLabels[asset]}</span>
        ))}
      </div>

      <h3>{item.title}</h3>
      <p>{item.summary}</p>

      <footer className="news-card-footer">
        <div>
          <strong>{item.source}</strong>
          <time dateTime={item.published_at}>
            {dateFormatter.format(new Date(item.published_at))}
          </time>
        </div>
        <button type="button" onClick={(event) => onRead(item, event)}>
          Read Full Brief <span aria-hidden="true">→</span>
        </button>
      </footer>
    </article>
  )
}

export default NewsCard
