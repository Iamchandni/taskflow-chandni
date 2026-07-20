import { NavLink } from 'react-router-dom'

export const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/projects', label: 'Projects' },
  { to: '/tasks', label: 'Tasks' },
  { to: '/statistics', label: 'Statistics' },
] as const

export function Navigation() {
  return (
    <nav aria-label="Primary">
      <ul>
        {NAV_ITEMS.map(i => (
          <li key={i.to}>
            <NavLink to={i.to} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              {i.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
