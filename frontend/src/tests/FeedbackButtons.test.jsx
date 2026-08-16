import { act, fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import FeedbackButtons from '../components/FeedbackButtons.jsx'


const baseProps = {
  onVote: vi.fn().mockResolvedValue(undefined),
  prompt: 'Was this useful?',
  subject: 'insight',
}


it('renders neutral and selected vote states with accessible pressed values', () => {
  const { rerender } = render(<FeedbackButtons {...baseProps} currentVote={null} />)
  const like = screen.getByRole('button', { name: 'Like this insight' })
  const dislike = screen.getByRole('button', { name: 'Dislike this insight' })

  expect(like).toHaveAttribute('aria-pressed', 'false')
  expect(dislike).toHaveAttribute('aria-pressed', 'false')

  rerender(<FeedbackButtons {...baseProps} currentVote="up" />)
  expect(like).toHaveAttribute('aria-pressed', 'true')
  expect(dislike).toHaveAttribute('aria-pressed', 'false')

  rerender(<FeedbackButtons {...baseProps} currentVote="down" />)
  expect(like).toHaveAttribute('aria-pressed', 'false')
  expect(dislike).toHaveAttribute('aria-pressed', 'true')
})


it('disables both controls while saving and shows an inline failure message', async () => {
  let rejectSave
  const onVote = vi.fn(() => new Promise((_resolve, reject) => {
    rejectSave = reject
  }))
  render(<FeedbackButtons {...baseProps} onVote={onVote} currentVote={null} />)

  fireEvent.click(screen.getByRole('button', { name: 'Like this insight' }))
  expect(screen.getByRole('button', { name: 'Like this insight' })).toBeDisabled()
  expect(screen.getByRole('button', { name: 'Dislike this insight' })).toBeDisabled()
  expect(screen.getByRole('status')).toHaveTextContent('Saving feedback.')

  await act(async () => {
    rejectSave(new Error('provider detail'))
  })

  expect(screen.getByRole('status')).toHaveTextContent('Unable to save feedback. Try again.')
  expect(screen.getByRole('button', { name: 'Like this insight' })).toBeEnabled()
  expect(screen.queryByText('provider detail')).not.toBeInTheDocument()
})

