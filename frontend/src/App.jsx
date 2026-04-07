import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ProfileSetup from './pages/ProfileSetup'
import MeetingPrep from './pages/MeetingPrep'
import PastMeetings from './pages/PastMeetings'
import AuthCallback from './pages/AuthCallback'
import Navbar from './components/Navbar'
import './index.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      setUser(JSON.parse(storedUser))
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    setIsAuthenticated(true)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('user')
  }

  return (
    <Router>
      <div className="min-h-screen">
        {isAuthenticated && <Navbar user={user} onLogout={handleLogout} />}

        <Routes>
          {!isAuthenticated ? (
            <>
              <Route path="/login" element={<Login onLogin={handleLogin} />} />
              <Route path="/auth/callback" element={<AuthCallback onLogin={handleLogin} />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </>
          ) : (
            <>
              <Route path="/" element={<Dashboard user={user} />} />
              <Route path="/profile" element={<ProfileSetup user={user} />} />
              <Route path="/meeting-prep" element={<MeetingPrep user={user} />} />
              <Route path="/past-meetings" element={<PastMeetings user={user} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </>
          )}
        </Routes>
      </div>
    </Router>
  )
}

export default App
