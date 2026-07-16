import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  test('App renders the initialization message', () => {
    render(<App />)
    expect(screen.getByText('TaskFlow Frontend Initialized')).toBeInTheDocument()
  })

  test('App exposes the message as a level-1 heading', () => {
    render(<App />)
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('TaskFlow Frontend Initialized')
  })

  test('App renders without throwing', () => {
    expect(() => render(<App />)).not.toThrow()
  })

  test('App displays the Nightshift pipeline message', () => {
    render(<App />)
    expect(
      screen.getByText('----Created this frontend for taskflow using Nightshift pipeline----')
    ).toBeInTheDocument()
  })
})
