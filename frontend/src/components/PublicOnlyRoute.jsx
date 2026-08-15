import { Navigate, Outlet } from 'react-router-dom'
import useAuth from '../hooks/useAuth.js'
import RouteLoading from './RouteLoading.jsx'

function PublicOnlyRoute() {
  const { isAuthenticated, loading, user } = useAuth()

  if (loading) {
    return <RouteLoading />
  }

  if (isAuthenticated) {
    const destination = user.onboarding_completed ? '/dashboard' : '/onboarding'
    return <Navigate to={destination} replace />
  }

  return <Outlet />
}

export default PublicOnlyRoute
