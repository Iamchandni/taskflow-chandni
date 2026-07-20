import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Sidebar } from './Sidebar'

describe('Sidebar', () => {
  test('renders all four navigation links with correct hrefs', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Sidebar />
      </MemoryRouter>
    )
    expect(screen.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('href', '/dashboard')
    expect(screen.getByRole('link', { name: 'Projects' })).toHaveAttribute('href', '/projects')
    expect(screen.getByRole('link', { name: 'Tasks' })).toHaveAttribute('href', '/tasks')
    expect(screen.getByRole('link', { name: 'Statistics' })).toHaveAttribute('href', '/statistics')
  })

  test('highlights the active route only', () => {
    render(
      <MemoryRouter initialEntries={['/projects']}>
        <Sidebar />
      </MemoryRouter>
    )
    const projectsLink = screen.getByRole('link', { name: 'Projects' })
    expect(projectsLink).toHaveAttribute('aria-current', 'page')
    expect(projectsLink.className).toContain('active')

    const dashboardLink = screen.getByRole('link', { name: 'Dashboard' })
    expect(dashboardLink).not.toHaveAttribute('aria-current', 'page')
    expect(dashboardLink.className).not.toContain('active')
  })
})
