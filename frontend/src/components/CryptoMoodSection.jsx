import MemeImage from './MemeImage.jsx'


function CryptoMoodSection({ meme }) {
  return (
    <section
      className="dashboard-crypto-mood dashboard-anchor-section"
      id="meme"
      aria-labelledby="meme-title"
      tabIndex="-1"
    >
      <header className="crypto-mood-heading">
        <div>
          <p className="eyebrow">Crypto Mood</p>
          <h2 id="meme-title">A lighter take on the market.</h2>
        </div>
      </header>

      {!meme ? (
        <div className="crypto-mood-unavailable" role="status">
          <h3>Crypto mood is temporarily unavailable.</h3>
          <p>Your market dashboard is still up to date.</p>
        </div>
      ) : (
        <div className="crypto-mood-content">
          <MemeImage
            className="crypto-mood-image"
            src={meme.image_url}
            alt={meme.alt_text}
          />
          <div className="crypto-mood-copy">
            <span>Today&apos;s mood</span>
            <h3>{meme.title}</h3>
            <p>
              Source: <strong>{meme.source}</strong>
            </p>
            {meme.source_url && (
              <a href={meme.source_url} target="_blank" rel="noopener noreferrer">
                View Source <span aria-hidden="true">↗</span>
              </a>
            )}
          </div>
        </div>
      )}
    </section>
  )
}

export default CryptoMoodSection
