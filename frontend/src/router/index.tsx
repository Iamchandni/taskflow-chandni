import { createBrowserRouter, useRouteError, type RouteObject } from 'react-router-dom'
import { AppLayout } from '../layouts/AppLayout'
import Dashboard from '../pages/Dashboard'
import Projects from '../pages/Projects'
import Tasks from '../pages/Tasks'
import Statistics from '../pages/Statistics'
import Login from '../pages/Login'

function RouteError() {
  const error = useRouteError()
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <pre>{error instanceof Error ? error.message : String(error)}</pre>
    </div>
  )
}

export const routes: RouteObject[] = [
  { path: '/login', element: <Login /> },
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <RouteError />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'projects', element: <Projects /> },
      { path: 'tasks', element: <Tasks /> },
      { path: 'statistics', element: <Statistics /> },
    ],
  },
]

export const router = createBrowserRouter(routes)
