import AuthenticatedPlaceholder from '../components/AuthenticatedPlaceholder.jsx'
import useAuth from '../hooks/useAuth.js'

function DashboardPage() {
  const { user } = useAuth()

  return (
    <AuthenticatedPlaceholder
      eyebrow="Your workspace"
      title={`Welcome, ${user.name}`}
      description="Your personalized dashboard is coming next."
    />
  )
}

export default DashboardPage
