import { render, screen } from '@testing-library/react'
import { Header } from './Header'

describe('Header', () => {
  test('renders the header banner with branding', () => {
    render(<Header />)
    expect(screen.getByRole('banner')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'TaskFlow' })).toBeInTheDocument()
  })
})
