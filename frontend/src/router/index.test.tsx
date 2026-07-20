import { render, screen, fireEvent } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { routes } from './index'

describe('Router', () => {
  test('root path redirects to Dashboard', () => {
    const router = createMemoryRouter(routes, { initialEntries: ['/'] })
    render(<RouterProvider router={router} />)
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })

  test('navigating between pages swaps content without a reload', () => {
    const router = createMemoryRouter(routes, { initialEntries: ['/dashboard'] })
    render(<RouterProvider router={router} />)

    fireEvent.click(screen.getByRole('link', { name: 'Tasks' }))

    expect(screen.getByRole('heading', { name: 'Tasks' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Dashboard' })).toBeNull()
    expect(screen.getByRole('link', { name: 'Tasks' })).toHaveAttribute('aria-current', 'page')
  })

  test('/login renders outside the layout', () => {
    const router = createMemoryRouter(routes, { initialEntries: ['/login'] })
    render(<RouterProvider router={router} />)

    expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument()
    expect(screen.queryByRole('navigation')).toBeNull()
    expect(screen.queryByLabelText('Sidebar')).toBeNull()
  })

  test('routing errors are surfaced, not swallowed', () => {
    const rootRoute = routes.find(r => r.path === '/')
    expect(rootRoute?.errorElement).toBeDefined()
  })
})
