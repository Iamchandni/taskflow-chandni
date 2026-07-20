import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  test('mounts the router and shows the default layout', () => {
    render(<App />)
    expect(screen.getByRole('navigation')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })
})
