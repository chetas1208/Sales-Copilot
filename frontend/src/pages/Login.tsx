import { useState } from 'react'
import LoginCard from '../components/ui/login-card'

interface LoginProps {
  onLogin: (userData: { id: number; email: string; name: string }) => void
}

const Login = ({ onLogin }: LoginProps) => {
  const [isLoading, setIsLoading] = useState(false)

  const handleEmailLogin = async (email: string, password: string) => {
    setIsLoading(true)

    // Simulate API call
    setTimeout(() => {
      onLogin({
        id: Date.now(),
        email,
        name: email.split('@')[0],
      })
      setIsLoading(false)
    }, 1000)
  }

  const handleScalekitLogin = async () => {
    setIsLoading(true)

    try {
      // Call backend to get Scalekit authorization URL
      const response = await fetch('http://localhost:8000/auth/scalekit/login?redirect_uri=http://localhost:5173/auth/callback')
      const data = await response.json()

      if (response.ok && data.authorization_url) {
        // Redirect to Scalekit hosted login page
        window.location.href = data.authorization_url
      } else {
        throw new Error(data.detail || 'Failed to initiate Scalekit login')
      }
    } catch (error) {
      console.error('Scalekit login error:', error)
      alert(error instanceof Error ? error.message : 'Scalekit SSO is not configured yet. Please add SCALEKIT_* environment variables to backend/.env')
      setIsLoading(false)
    }
  }

  return <LoginCard onSubmit={handleEmailLogin} onSSOClick={handleScalekitLogin} />
}

export default Login
