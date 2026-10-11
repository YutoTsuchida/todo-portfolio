import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import App from '../src/App'

// REQ-NF-001, REQ-T-009: the React entry screen renders in the test environment.
test('renders the initial application screen', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: 'Todo Portfolio' })).toBeInTheDocument()
})
