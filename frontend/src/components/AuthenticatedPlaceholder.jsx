import useAuth from '../hooks/useAuth.js'
import PageHeader from './PageHeader.jsx'

function AuthenticatedPlaceholder({ eyebrow, title, description }) {
  const { logout } = useAuth()

  return (
    <main className="placeholder-page">
      <div className="placeholder-shell">
        <PageHeader />

        <section className="placeholder-content" aria-labelledby="page-title">
          <p className="eyebrow">{eyebrow}</p>
          <h1 id="page-title">{title}</h1>
          <p>{description}</p>
          <button className="button button--secondary" type="button" onClick={logout}>
            Logout
          </button>
        </section>
      </div>
    </main>
  )
}

export default AuthenticatedPlaceholder
