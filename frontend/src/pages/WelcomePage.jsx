import { Link } from 'react-router-dom'
import Brand from '../components/Brand.jsx'

function WelcomePage() {
  return (
    <main className="welcome-page">
      <div className="background-shape background-shape--left" aria-hidden="true" />
      <div className="background-shape background-shape--right" aria-hidden="true" />

      <section className="welcome-content" aria-labelledby="welcome-title">
        <Brand />

        <h1 id="welcome-title">Welcome to CoinSight AI</h1>
        <p className="subtitle">Personalized crypto insights powered by AI</p>

        <div className="welcome-actions">
          <Link className="button button--primary" to="/signup">
            Get Started
          </Link>
          <Link className="button button--secondary" to="/login">
            Sign In
          </Link>
        </div>

        <p className="supporting-text">Smart insights. Simple decisions.</p>
      </section>
    </main>
  )
}

export default WelcomePage
