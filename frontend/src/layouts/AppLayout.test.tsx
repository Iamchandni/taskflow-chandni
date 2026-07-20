import { render, screen, within } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { routes } from '../router/index'

describe('AppLayout', () => {
  test('composes sidebar, header, and routed content', () => {
    const router = createMemoryRouter(routes, { initialEntries: ['/dashboard'] })
    render(<RouterProvider router={router} />)

    expect(screen.getByLabelText('Sidebar')).toBeInTheDocument()
    expect(screen.getByRole('banner')).toBeInTheDocument()
    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(
      within(screen.getByRole('main')).getByRole('heading', { name: 'Dashboard' })
    ).toBeInTheDocument()
  })
})
