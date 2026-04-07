import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

const AuthCallback = ({ onLogin }) => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [error, setError] = useState(null)

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')

      if (!code) {
        setError('No authorization code received')
        return
      }

      try {
        // Exchange code for tokens via backend
        const response = await fetch(
          `http://localhost:8000/auth/scalekit/callback?code=${code}&redirect_uri=http://localhost:5173/auth/callback`
        )
        const data = await response.json()

        if (response.ok) {
          // Store tokens (in production, use HttpOnly cookies)
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)

          // Login with user data
          onLogin({
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            organization_id: data.user.organization_id,
            roles: data.user.roles || []
          })

          // Redirect to dashboard
          navigate('/')
        } else {
          throw new Error(data.detail || 'Authentication failed')
        }
      } catch (error) {
        console.error('Callback error:', error)
        setError(error.message)
      }
    }

    handleCallback()
  }, [searchParams, navigate, onLogin])

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="card text-center">
          {!error ? (
            <>
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Completing Sign In...
              </h2>
              <p className="text-gray-600">
                Please wait while we authenticate you with Scalekit
              </p>
            </>
          ) : (
            <>
              <div className="text-red-600 text-5xl mb-4">!</div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Authentication Error
              </h2>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={() => navigate('/login')}
                className="btn-primary"
              >
                Back to Login
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default AuthCallback
