import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Leaf, ArrowLeft, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { supabase } from '../lib/supabase'

export default function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [organization, setOrganization] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // 1. Sign up with Supabase Auth
      const { data, error: signUpError } = await register(email, password, {
        full_name: name,
        organization_name: organization
      })
      
      if (signUpError) throw signUpError

      // Wait a moment for session to establish
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
         // Some Supabase configurations require email confirmation
         setError("Registration successful! Please check your email to confirm your account.")
         setIsLoading(false)
         return
      }

      // 2. Synchronize user and organization with our backend
      const response = await fetch('/api/v1/auth/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          full_name: name,
          organization_name: organization
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        console.error('Sync error:', errorData)
        // We don't throw here because they are authenticated, but we might want to alert them
      }

      // 3. Navigate to dashboard
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Failed to create account')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: '#0d1117' }}
    >
      <div
        className="w-full max-w-md rounded-2xl p-8 shadow-2xl border my-8"
        style={{
          background: 'rgba(22, 27, 34, 0.9)',
          borderColor: 'rgba(255,255,255,0.08)',
          backdropFilter: 'blur(20px)',
        }}
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #14b869, #059669)' }}
          >
            <Leaf size={20} className="text-white" />
          </div>
          <span className="font-bold text-xl text-white">
            ESG<span style={{ color: '#14b869' }}>Intelligence</span>
          </span>
        </div>

        {/* Heading */}
        <h1 className="text-2xl font-bold text-center text-white mb-2">Create your account</h1>
        <p className="text-center mb-8" style={{ color: '#8b949e' }}>
          Start your ESG journey today
        </p>

        {error && (
          <div className="mb-6 p-4 rounded-lg flex items-start gap-3" style={{ background: 'rgba(248, 81, 73, 0.1)', border: '1px solid rgba(248, 81, 73, 0.4)' }}>
            <AlertCircle size={18} style={{ color: '#f85149', marginTop: '2px', flexShrink: 0 }} />
            <p className="text-sm" style={{ color: '#f85149' }}>{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="register-name"
              className="block text-sm font-medium mb-2"
              style={{ color: '#c9d1d9' }}
            >
              Full Name
            </label>
            <input
              id="register-name"
              type="text"
              placeholder="Jane Smith"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-lg text-sm outline-none transition-all duration-200"
              style={{
                background: 'rgba(13, 17, 23, 0.8)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#f0f6fc',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#14b869')}
              onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.1)')}
            />
          </div>

          <div className="mb-4">
            <label
              htmlFor="register-email"
              className="block text-sm font-medium mb-2"
              style={{ color: '#c9d1d9' }}
            >
              Work Email
            </label>
            <input
              id="register-email"
              type="email"
              placeholder="you@company.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-lg text-sm outline-none transition-all duration-200"
              style={{
                background: 'rgba(13, 17, 23, 0.8)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#f0f6fc',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#14b869')}
              onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.1)')}
            />
          </div>

          <div className="mb-4">
            <label
              htmlFor="register-org"
              className="block text-sm font-medium mb-2"
              style={{ color: '#c9d1d9' }}
            >
              Organization Name
            </label>
            <input
              id="register-org"
              type="text"
              placeholder="Acme Corp"
              required
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              className="w-full px-4 py-3 rounded-lg text-sm outline-none transition-all duration-200"
              style={{
                background: 'rgba(13, 17, 23, 0.8)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#f0f6fc',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#14b869')}
              onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.1)')}
            />
          </div>

          <div className="mb-6">
            <label
              htmlFor="register-password"
              className="block text-sm font-medium mb-2"
              style={{ color: '#c9d1d9' }}
            >
              Password
            </label>
            <input
              id="register-password"
              type="password"
              placeholder="••••••••"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-lg text-sm outline-none transition-all duration-200"
              style={{
                background: 'rgba(13, 17, 23, 0.8)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#f0f6fc',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#14b869')}
              onBlur={(e) => (e.target.style.borderColor = 'rgba(255,255,255,0.1)')}
            />
          </div>

          <button
            id="register-submit-btn"
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-lg text-sm font-semibold transition-all duration-200 hover:opacity-90 cursor-pointer disabled:opacity-50"
            style={{
              background: 'linear-gradient(135deg, #14b869, #059669)',
              color: '#fff',
            }}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        {/* Footer */}
        <p className="text-center mt-6 text-sm" style={{ color: '#8b949e' }}>
          Already have an account?{' '}
          <Link to="/login" className="font-medium" style={{ color: '#14b869' }}>
            Sign in
          </Link>
        </p>

        <Link
          to="/"
          className="flex items-center justify-center gap-1 mt-4 text-xs transition-colors duration-200"
          style={{ color: '#8b949e' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#f0f6fc')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#8b949e')}
        >
          <ArrowLeft size={14} /> Back to home
        </Link>
      </div>
    </div>
  )
}
