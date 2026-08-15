import { Navigate, Outlet } from 'react-router-dom'
import useAuth from '../hooks/useAuth.js'

function IncompleteOnboardingRoute() {
  const { user } = useAuth()

  if (user.onboarding_completed) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export default IncompleteOnboardingRoute
