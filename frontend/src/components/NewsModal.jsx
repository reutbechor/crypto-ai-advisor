import { useEffect, useRef } from 'react'


const assetLabels = {
  bitcoin: 'Bitcoin',
  ethereum: 'Ethereum',
  solana: 'Solana',
  cardano: 'Cardano',
  ripple: 'XRP',
  general: 'Crypto Market',
}

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
})

function NewsModal({ item, onClose }) {
  const dialogRef = useRef(null)

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const dialog = dialogRef.current

    document.body.style.overflow = 'hidden'
    dialog?.focus()

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
        return
      }

      if (event.key !== 'Tab' || !dialog) {
        return
      }

      const focusableElements = [...dialog.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])')]
        .filter((element) => !element.disabled)

      if (focusableElements.length === 0) {
        event.preventDefault()
        dialog.focus()
        return
      }

      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault()
        lastElement.focus()
      } else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault()
        firstElement.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow
    }
  }, [item.id, onClose])

  function handleBackdropMouseDown(event) {
    if (event.target === event.currentTarget) {
      onClose()
    }
  }

  return (
    <div className="news-modal-backdrop" onMouseDown={handleBackdropMouseDown}>
      <article
        className="news-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="news-modal-title"
        aria-describedby="news-modal-content"
        ref={dialogRef}
        tabIndex="-1"
      >
        <button
          className="news-modal-close-icon"
          type="button"
          aria-label="Close full brief"
          onClick={onClose}
        >
          <span aria-hidden="true">×</span>
        </button>

        <div className="news-assets" aria-label="Related assets">
          {item.related_assets.map((asset) => (
            <span key={asset}>{assetLabels[asset]}</span>
          ))}
        </div>

        <h2 id="news-modal-title">{item.title}</h2>

        <p className="news-modal-byline">
          <strong>{item.source}</strong>
          <span aria-hidden="true">·</span>
          <time dateTime={item.published_at}>
            {dateFormatter.format(new Date(item.published_at))}
          </time>
        </p>

        <div className="news-modal-content" id="news-modal-content">
          {item.content.split('\n\n').map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>

        <div className="news-modal-actions">
          <button className="button button--secondary" type="button" onClick={onClose}>
            Close
          </button>
        </div>
      </article>
    </div>
  )
}

export default NewsModal
