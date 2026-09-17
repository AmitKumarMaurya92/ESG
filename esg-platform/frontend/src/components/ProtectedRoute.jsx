import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

/**
 * Higher-order component that wraps authenticated routes.
 * Redirects unauthenticated users to the login page.
 */
export default function ProtectedRoute({ children }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0d1117' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2" style={{ borderColor: '#14b869' }}></div>
      </div>
    )
  }

  if (!user) {
    // Redirect to login if there is no active session
    return <Navigate to="/login" replace />
  }

  return children
}
