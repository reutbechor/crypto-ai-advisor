import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import DashboardNav from '../components/DashboardNav.jsx'


it('renders personalized navigation and reports the selected section', () => {
  const onNavigate = vi.fn()
  const items = [
    { id: 'overview', label: 'Overview' },
    { id: 'meme', label: 'Meme' },
    { id: 'market', label: 'Market' },
  ]

  render(<DashboardNav activeSection="meme" items={items} onNavigate={onNavigate} />)

  expect(screen.getAllByRole('button').map((button) => button.textContent))
    .toEqual(['Overview', 'Meme', 'Market'])
  expect(screen.getByRole('button', { name: 'Meme' })).toHaveAttribute('aria-current', 'location')
  fireEvent.click(screen.getByRole('button', { name: 'Market' }))
  expect(onNavigate).toHaveBeenCalledWith('market')
})

