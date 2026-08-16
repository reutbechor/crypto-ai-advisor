import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import MemeImage from '../components/MemeImage.jsx'


it('replaces a failed meme image with accessible fallback content', () => {
  render(<MemeImage src="https://example.test/meme.png" alt="Daily crypto meme" />)

  fireEvent.error(screen.getByRole('img', { name: 'Daily crypto meme' }))

  expect(screen.getByRole('img', { name: 'Daily crypto meme' }))
    .toHaveTextContent('Image temporarily unavailable')
})

