import { useState } from 'react'


function ThumbIcon({ direction }) {
  const isUp = direction === 'up'

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d={isUp ? 'M7 10v12H3a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h4Z' : 'M7 14V2H3a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h4Z'} />
      <path d={isUp
        ? 'M7 10h2l3.5-7a2.7 2.7 0 0 1 3.4 3.5L14.5 10H20a2 2 0 0 1 1.9 2.6l-2.2 7A2 2 0 0 1 17.8 21H7'
        : 'M7 14h2l3.5 7a2.7 2.7 0 0 0 3.4-3.5L14.5 14H20a2 2 0 0 0 1.9-2.6l-2.2-7A2 2 0 0 0 17.8 3H7'}
      />
    </svg>
  )
}

function FeedbackButtons({ currentVote, onVote, prompt, subject }) {
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  async function handleVote(vote) {
    setIsSaving(true)
    setError('')

    try {
      await onVote(vote)
    } catch {
      setError('Unable to save feedback. Try again.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="feedback-control" aria-busy={isSaving}>
      <span className="feedback-prompt">{prompt}</span>
      <div className="feedback-actions" aria-label={`Feedback for ${subject}`}>
        {['up', 'down'].map((vote) => (
          <button
            className={`feedback-button${currentVote === vote ? ' feedback-button--selected' : ''}`}
            type="button"
            key={vote}
            aria-label={`${vote === 'up' ? 'Like' : 'Dislike'} this ${subject}`}
            aria-pressed={currentVote === vote}
            disabled={isSaving}
            onClick={() => handleVote(vote)}
          >
            <ThumbIcon direction={vote} />
          </button>
        ))}
      </div>
      {isSaving && <span className="sr-only" role="status">Saving feedback.</span>}
      {error && <span className="feedback-error" role="status">{error}</span>}
    </div>
  )
}

export default FeedbackButtons
