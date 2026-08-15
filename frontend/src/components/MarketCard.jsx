const usdFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 4,
})

const marketCapFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  notation: 'compact',
  maximumFractionDigits: 1,
})

function MarketCard({ coin }) {
  const isPositive = coin.price_change_percentage_24h >= 0
  const formattedChange = `${isPositive ? '+' : ''}${coin.price_change_percentage_24h.toFixed(2)}% today`
  const accessibleChange = `${isPositive ? 'Up' : 'Down'} ${Math.abs(coin.price_change_percentage_24h).toFixed(2)} percent today`

  return (
    <article className="market-card">
      <header className="market-card-heading">
        <div>
          <h3>{coin.name}</h3>
          <span>{coin.symbol.toUpperCase()}</span>
        </div>
        <span className="market-card-dot" aria-hidden="true" />
      </header>

      <p className="market-price">{usdFormatter.format(coin.current_price)}</p>
      <p
        className={`market-change market-change--${isPositive ? 'positive' : 'negative'}`}
        aria-label={accessibleChange}
      >
        {formattedChange}
      </p>

      {coin.market_cap !== null && (
        <footer className="market-card-footer">
          <span>Market cap</span>
          <strong>{marketCapFormatter.format(coin.market_cap)}</strong>
        </footer>
      )}
    </article>
  )
}

export default MarketCard
