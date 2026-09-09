import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useForm } from '../hooks/useForm'
import { Button, Input, Card, CardContent, Alert } from '../components/UI'
import { Shield, Mail, Lock, User, Eye, EyeOff, CheckCircle2, ArrowRight } from 'lucide-react'
import { classNames } from '../utils/helpers'

export function LoginPage() {
  const navigate = useNavigate()
  const { login, isAuthenticated } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { values, errors, handleChange, handleBlur, handleSubmit, setFieldValue } = useForm({
    initialValues: { email: '', password: '' },
    validate: (values) => {
      const errs = {}
      if (!values.email) errs.email = 'Email is required'
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) errs.email = 'Invalid email format'
      if (!values.password) errs.password = 'Password is required'
      else if (values.password.length < 8) errs.password = 'Password must be at least 8 characters'
      return errs
    },
    onSubmit: async (values) => {
      setError('')
      setLoading(true)
      try {
        await login(values)
        navigate('/dashboard')
      } catch (err) {
        let errMsg = 'Invalid email or password'
        const detail = err.response?.data?.detail
        if (detail) {
          if (Array.isArray(detail)) {
            errMsg = detail.map(e => `${e.loc ? e.loc.join('.') + ': ' : ''}${e.msg}`).join(', ')
          } else if (typeof detail === 'object') {
            errMsg = JSON.stringify(detail)
          } else {
            errMsg = String(detail)
          }
        }
        setError(errMsg)
      } finally {
        setLoading(false)
      }
    },
  })

  if (isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-surface-elevated flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Link to="/" className="flex items-center gap-2" aria-label="CivicSense Home">
            <div className="w-12 h-12 rounded-xl bg-primary-500 flex items-center justify-center">
              <Shield className="h-7 w-7 text-white" />
            </div>
            <span className="text-heading-xl font-bold text-text-primary">CivicSense</span>
          </Link>
        </div>

        <Card className="bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6 sm:p-8">
            <div className="text-center mb-8">
              <h1 className="text-heading-lg font-bold text-text-primary">Welcome Back</h1>
              <p className="text-body text-text-secondary mt-2">Sign in to track complaints and report issues</p>
            </div>

            {error && (
              <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <Input
                label="Email"
                type="email"
                name="email"
                value={values.email}
                onChange={handleChange}
                onBlur={handleBlur}
                error={errors.email}
                placeholder="you@example.com"
                autoComplete="email"
                disabled={loading}
              />

              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={values.password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={errors.password}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-[38px] text-text-muted hover:text-text-primary"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-border text-primary-500 focus:ring-primary-500"
                  />
                  <span className="text-body-sm text-text-secondary">Remember me</span>
                </label>
                <Link to="/forgot-password" className="text-body-sm text-primary-500 hover:text-primary-600">
                  Forgot password?
                </Link>
              </div>

              <Button type="submit" className="w-full" size="lg" loading={loading}>
                Sign In
                <ArrowRight className="h-4 w-4" />
              </Button>
            </form>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-body-sm">
                <span className="px-4 bg-white/80 backdrop-blur-sm text-text-muted">Or continue with</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Button variant="secondary" type="button" className="w-full">
                <svg className="h-5 w-5" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/></svg>
                Google
              </Button>
              <Button variant="secondary" type="button" className="w-full">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.37 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.28-1.56 3.285-1.23 3.285-1.23.66 1.65.24 2.88.12 3.18.765.855 1.23 1.92 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                GitHub
              </Button>
            </div>

            <p className="mt-6 text-center text-body-sm text-text-secondary">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary-500 font-medium hover:text-primary-600">
                Create one
              </Link>
            </p>
          </CardContent>
        </Card>

        <p className="mt-6 text-center text-caption text-text-muted">
          Demo credentials: admin@city.gov / admin123 | citizen@example.com / citizen123
        </p>
      </div>
    </div>
  )
}

function NavigateToDashboard() {
  return null // Will redirect via useEffect in parent
}

export function RegisterPage() {
  const navigate = useNavigate()
  const { register, isAuthenticated } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [role, setRole] = useState('citizen')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [termsAgreed, setTermsAgreed] = useState(false)

  const { values, errors, handleChange, handleBlur, handleSubmit } = useForm({
    initialValues: {
      full_name: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: '',
    },
    validate: (values) => {
      const errs = {}
      if (!values.full_name.trim()) errs.full_name = 'Full name is required'
      if (!values.email) errs.email = 'Email is required'
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) errs.email = 'Invalid email format'
      if (!values.phone) errs.phone = 'Phone is required'
      else if (!/^\+?[\d\s-]{10,}$/.test(values.phone)) errs.phone = 'Invalid phone number'
      if (!values.password) errs.password = 'Password is required'
      else if (values.password.length < 8) errs.password = 'Password must be at least 8 characters'
      if (values.password !== values.confirmPassword) errs.confirmPassword = 'Passwords do not match'
      return errs
    },
    onSubmit: async (values) => {
      setError('')
      setLoading(true)
      try {
        const { confirmPassword, ...registrationData } = values
        await register({
          user_data: {
            ...registrationData,
            role,
          }
        })
        navigate('/dashboard')
      } catch (err) {
        let errMsg = 'Registration failed. Please try again.'
        const detail = err.response?.data?.detail
        if (detail) {
          if (Array.isArray(detail)) {
            errMsg = detail.map(e => `${e.loc ? e.loc.join('.') + ': ' : ''}${e.msg}`).join(', ')
          } else if (typeof detail === 'object') {
            errMsg = JSON.stringify(detail)
          } else {
            errMsg = String(detail)
          }
        }
        setError(errMsg)
      } finally {
        setLoading(false)
      }
    },
  })

  if (isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-surface-elevated flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <Link to="/" className="flex items-center gap-2" aria-label="CivicSense Home">
            <div className="w-12 h-12 rounded-xl bg-primary-500 flex items-center justify-center">
              <Shield className="h-7 w-7 text-white" />
            </div>
            <span className="text-heading-xl font-bold text-text-primary">CivicSense</span>
          </Link>
        </div>

        <Card className="bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6 sm:p-8">
            <div className="text-center mb-8">
              <h1 className="text-heading-lg font-bold text-text-primary">Create Account</h1>
              <p className="text-body text-text-secondary mt-2">Join CivicSense to report and track civic issues</p>
            </div>

            {error && (
              <Alert variant="danger" className="mb-6" dismissible onClose={() => setError('')}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div className="space-y-3 mb-4">
                <p className="text-body-sm font-medium text-text-secondary">Register as</p>
                <div className="grid grid-cols-2 gap-3">
                  {['citizen', 'admin'].map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setRole(r)}
                      className={classNames(
                        'flex items-center justify-center gap-2 px-4 py-3 rounded-button border-2 transition-all',
                        role === r
                          ? 'border-primary-500 bg-primary-50 text-primary-600'
                          : 'border-border text-text-secondary hover:border-primary-300 hover:bg-surface-hover'
                      )}
                    >
                      <User className="h-5 w-5" />
                      <span className="capitalize">{r}</span>
                    </button>
                  ))}
                </div>
              </div>

              <Input
                label="Full Name"
                type="text"
                name="full_name"
                value={values.full_name}
                onChange={handleChange}
                onBlur={handleBlur}
                error={errors.full_name}
                placeholder="John Doe"
                autoComplete="name"
                disabled={loading}
              />

              <Input
                label="Email"
                type="email"
                name="email"
                value={values.email}
                onChange={handleChange}
                onBlur={handleBlur}
                error={errors.email}
                placeholder="you@example.com"
                autoComplete="email"
                disabled={loading}
              />

              <Input
                label="Phone"
                type="tel"
                name="phone"
                value={values.phone}
                onChange={handleChange}
                onBlur={handleBlur}
                error={errors.phone}
                placeholder="+91 98765 43210"
                autoComplete="tel"
                disabled={loading}
              />

              <div className="relative">
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={values.password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={errors.password}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-[38px] text-text-muted hover:text-text-primary"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>

              <Input
                label="Confirm Password"
                type={showPassword ? 'text' : 'password'}
                name="confirmPassword"
                value={values.confirmPassword}
                onChange={handleChange}
                onBlur={handleBlur}
                error={errors.confirmPassword}
                placeholder="••••••••"
                autoComplete="new-password"
                disabled={loading}
              />

              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  id="terms"
                  required
                  checked={termsAgreed}
                  onChange={(e) => setTermsAgreed(e.target.checked)}
                  className="mt-1 w-4 h-4 rounded border-border text-primary-500 focus:ring-primary-500"
                />
                <label htmlFor="terms" className="text-body-sm text-text-secondary">
                  I agree to the{' '}
                  <Link to="/terms" className="text-primary-500 hover:underline">Terms of Service</Link>
                  {' '}and{' '}
                  <Link to="/privacy" className="text-primary-500 hover:underline">Privacy Policy</Link>
                </label>
              </div>

              <Button type="submit" className="w-full" size="lg" loading={loading} disabled={!termsAgreed}>
                Create Account
                <ArrowRight className="h-4 w-4" />
              </Button>
            </form>

            <p className="mt-6 text-center text-body-sm text-text-secondary">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-500 font-medium hover:text-primary-600">
                Sign in
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
