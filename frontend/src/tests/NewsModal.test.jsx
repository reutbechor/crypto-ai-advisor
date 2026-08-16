import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import NewsModal from '../components/NewsModal.jsx'


const item = {
  id: 'btc-001',
  title: 'Bitcoin market structure',
  summary: 'Preview text.',
  content: 'First full paragraph.\n\nSecond full paragraph.',
  source: 'CoinSight Market Brief',
  published_at: '2026-01-15T09:00:00Z',
  related_assets: ['bitcoin'],
}


it('shows full content, focuses the dialog, and closes by button or Escape', () => {
  const onClose = vi.fn()
  const props = { currentVote: null, item, onClose, onVote: vi.fn().mockResolvedValue() }
  const firstRender = render(<NewsModal {...props} />)

  const dialog = screen.getByRole('dialog')
  expect(dialog).toHaveFocus()
  expect(screen.getByText('First full paragraph.')).toBeInTheDocument()
  expect(screen.getByText('Second full paragraph.')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Close' }))
  expect(onClose).toHaveBeenCalledTimes(1)

  firstRender.unmount()
  render(<NewsModal {...props} />)
  fireEvent.keyDown(document, { key: 'Escape' })
  expect(onClose).toHaveBeenCalledTimes(2)
})

