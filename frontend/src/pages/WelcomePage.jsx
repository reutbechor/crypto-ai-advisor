import { Link } from 'react-router-dom'
import MarketVisual from '../components/MarketVisual.jsx'
import PageHeader from '../components/PageHeader.jsx'

function WelcomePage() {
  return (
    <main className="welcome-page">
      <div className="welcome-shell">
        <PageHeader />

        <div className="welcome-layout">
          <section className="welcome-copy" aria-labelledby="welcome-title">
            <p className="eyebrow">AI Crypto Advisor</p>
            <h1 id="welcome-title">
              <span>Crypto</span>
              <span>intelligence,</span>
              <span>made personal.</span>
            </h1>
            <p className="welcome-description">
              Market data, news and AI-powered insights tailored to the way you invest.
            </p>
            <div className="welcome-actions">
              <Link className="button button--primary" to="/signup">
                <span>Get Started</span>
                <span aria-hidden="true">→</span>
              </Link>
              <Link className="button button--secondary" to="/login">
                <span>Sign In</span>
                <span aria-hidden="true">→</span>
              </Link>
            </div>
          </section>

          <MarketVisual />
        </div>
      </div>
    </main>
  )
}

export default WelcomePage
