import { Link } from 'react-router-dom'
import PageHeader from './PageHeader.jsx'

function AuthLayout({ titleLines, description, titleId, formLabel, children }) {
  return (
    <main className="auth-page">
      <div className="auth-shell">
        <PageHeader />

        <div className="auth-layout">
          <section className="auth-intro" aria-labelledby={titleId}>
            <Link className="back-button" to="/" aria-label="Back to welcome">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m14.5 5-7 7 7 7" />
              </svg>
            </Link>

            <div className="auth-title">
              <h1 id={titleId}>
                {titleLines.map((line) => (
                  <span key={line}>{line}</span>
                ))}
              </h1>
              <p>{description}</p>
            </div>
          </section>

          <section className="auth-form-area" aria-label={formLabel}>
            <div className="auth-card">
              <div className="form-card-heading">
                <span>{formLabel}</span>
                <span>All fields required</span>
              </div>
              {children}
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}

export default AuthLayout
