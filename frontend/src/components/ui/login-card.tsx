import * as React from "react"
import { Button } from "./button"
import { Input } from "./input"
import { Label } from "./label"

interface LoginCardProps {
  onSubmit: (email: string, password: string) => void
  onSSOClick?: () => void
}

export default function LoginCard({ onSubmit, onSSOClick }: LoginCardProps) {
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(email, password)
  }

  return (
    <div style={{ position: 'relative', width: '100%', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
      {/* Gradient Background */}
      <div style={{ position: 'absolute', inset: '0', background: 'linear-gradient(135deg, #1f2937 0%, #581c87 50%, #5b21b6 100%)' }}>
        <div style={{ position: 'absolute', inset: '0', backgroundImage: 'url(https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=2070)', backgroundSize: 'cover', backgroundPosition: 'center', opacity: '0.2' }}></div>
        <div style={{ position: 'absolute', inset: '0', backgroundColor: 'rgba(0, 0, 0, 0.4)' }}></div>
      </div>

      {/* Login Card */}
      <div style={{ position: 'relative', backgroundColor: 'white', width: '100%', maxWidth: '28rem', padding: '2rem', borderRadius: '0.75rem', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', zIndex: '10' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>Meetstream AI</h2>
          <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>AI-Powered Sales Intelligence</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ marginTop: '0.25rem' }}
            />
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ marginTop: '0.25rem' }}
            />
          </div>

          <Button type="submit" style={{ width: '100%', marginTop: '0.5rem', backgroundColor: '#9333ea' }}>
            Sign In
          </Button>
        </form>

        {onSSOClick && (
          <>
            <div style={{ position: 'relative', margin: '1.5rem 0' }}>
              <div style={{ position: 'absolute', inset: '0', display: 'flex', alignItems: 'center' }}>
                <div style={{ width: '100%', borderTop: '1px solid #d1d5db' }} />
              </div>
              <div style={{ position: 'relative', display: 'flex', justifyContent: 'center', fontSize: '0.875rem' }}>
                <span style={{ padding: '0 0.5rem', backgroundColor: 'white', color: '#6b7280' }}>or</span>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={onSSOClick}
              style={{ width: '100%' }}
            >
              Enterprise SSO Login
            </Button>
          </>
        )}

        <p style={{ textAlign: 'center', fontSize: '0.875rem', color: '#6b7280', marginTop: '1.5rem' }}>
          Don't have an account?{' '}
          <a href="#" style={{ color: '#9333ea', fontWeight: '500', textDecoration: 'none' }}>
            Contact sales
          </a>
        </p>
      </div>

      {/* Footer */}
      <div style={{ position: 'absolute', bottom: '1rem', left: '0', right: '0', textAlign: 'center', color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem', zIndex: '20' }}>
        © 2025 Meetstream AI. AI-Powered Sales Intelligence Platform.
      </div>
    </div>
  )
}
