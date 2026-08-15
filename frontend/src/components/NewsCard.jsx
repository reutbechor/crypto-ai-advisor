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

function NewsCard({ item }) {
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
        {item.url && (
          <a href={item.url} target="_blank" rel="noreferrer">
            Read brief
          </a>
        )}
      </footer>
    </article>
  )
}

export default NewsCard
