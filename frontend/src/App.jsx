import './App.css'

function App() {
  return (
    <main className="welcome-page">
      <div className="background-shape background-shape--left" aria-hidden="true" />
      <div className="background-shape background-shape--right" aria-hidden="true" />

      <section className="welcome-content" aria-labelledby="welcome-title">
        <div className="brand" aria-label="CoinSight AI">
          <span className="brand-mark" aria-hidden="true">
            <span />
          </span>
          <span>CoinSight AI</span>
        </div>

        <h1 id="welcome-title">Welcome to CoinSight AI</h1>
        <p className="subtitle">Personalized crypto insights powered by AI</p>

        <div className="welcome-actions">
          <button className="button button--primary" type="button">
            Get Started
          </button>
          <button className="button button--secondary" type="button">
            Sign In
          </button>
        </div>

        <p className="supporting-text">Smart insights. Simple decisions.</p>
      </section>
    </main>
  )
}

export default App
