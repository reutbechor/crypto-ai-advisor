import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import DailyDateLabel from '../components/DailyDateLabel.jsx'


it('formats the backend daily date in UTC and renders nothing without a date', () => {
  const { rerender } = render(<DailyDateLabel date="2026-08-16" label="Daily brief" />)

  expect(screen.getByText('Daily brief')).toBeInTheDocument()
  expect(screen.getByText('Aug 16, 2026')).toHaveAttribute('datetime', '2026-08-16')

  rerender(<DailyDateLabel date={null} label="Daily brief" />)
  expect(screen.queryByText('Daily brief')).not.toBeInTheDocument()
})

