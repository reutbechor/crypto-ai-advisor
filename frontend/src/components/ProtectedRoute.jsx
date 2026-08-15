import { Navigate, Outlet, useLocation } from 'react-router-dom'
import useAuth from '../hooks/useAuth.js'
import RouteLoading from './RouteLoading.jsx'

function ProtectedRoute() {
  const location = useLocation()
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <RouteLoading />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}

export default ProtectedRoute
