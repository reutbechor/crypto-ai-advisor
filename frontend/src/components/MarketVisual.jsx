function EthereumIcon() {
  return (
    <svg viewBox="0 0 48 76" aria-hidden="true">
      <path d="M24 0 0 39l24 14 24-14L24 0Z" />
      <path d="m24 58-24-14 24 32 24-32-24 14Z" />
      <path className="eth-detail" d="m24 7-17 31 17 10V7Z" />
    </svg>
  )
}

function MarketVisual() {
  return (
    <aside className="market-visual" aria-label="Cryptocurrency portfolio illustration">
      <div className="visual-heading">
        <span>Crypto market</span>
        <span>Live perspective</span>
      </div>

      <div className="crypto-coins" aria-hidden="true">
        <div className="bitcoin-coin">
          <span className="bitcoin-symbol">₿</span>
          <small>Bitcoin</small>
        </div>
        <div className="ethereum-coin">
          <EthereumIcon />
          <small>Ethereum</small>
        </div>
      </div>

      <div className="chart-panel">
        <div className="chart-heading">
          <div>
            <span>Market growth</span>
            <strong>Positive momentum</strong>
          </div>
          <p>+24.8%</p>
        </div>

        <svg
          className="growth-chart"
          viewBox="0 0 640 230"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <path className="chart-area" d="M0 198 C68 184 100 196 154 162 S234 177 292 120 S386 142 434 92 S526 106 640 22 L640 230 L0 230Z" />
          <path className="chart-line" d="M0 198 C68 184 100 196 154 162 S234 177 292 120 S386 142 434 92 S526 106 640 22" />
          <circle cx="640" cy="22" r="7" />
        </svg>

        <div className="chart-axis" aria-hidden="true">
          <span>BTC</span>
          <span>ETH</span>
          <span>AI Index</span>
        </div>
      </div>

      <div className="portfolio-card">
        <span>Balanced Portfolio</span>
        <strong>+12.4%</strong>
      </div>
    </aside>
  )
}

export default MarketVisual
