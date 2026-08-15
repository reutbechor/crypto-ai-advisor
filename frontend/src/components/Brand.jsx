import { Link } from 'react-router-dom'

function Brand({ className = '' }) {
  return (
    <Link className={`brand ${className}`.trim()} to="/" aria-label="CoinSight AI home">
      <span className="brand-mark" aria-hidden="true">
        <span />
      </span>
      <span>CoinSight AI</span>
    </Link>
  )
}

export default Brand
