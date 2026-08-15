import { Link } from 'react-router-dom'
import Brand from './Brand.jsx'

function AuthLayout({ title, description, titleId, children }) {
  return (
    <main className="auth-page">
      <div className="background-shape background-shape--left" aria-hidden="true" />
      <div className="background-shape background-shape--right" aria-hidden="true" />

      <section className="auth-panel" aria-labelledby={titleId}>
        <Link className="back-link" to="/">
          <span aria-hidden="true">←</span>
          Back to welcome
        </Link>

        <Brand className="auth-brand" />

        <header className="auth-heading">
          <h1 id={titleId}>{title}</h1>
          <p>{description}</p>
        </header>

        {children}
      </section>
    </main>
  )
}

export default AuthLayout
