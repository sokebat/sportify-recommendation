'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function SignupPage() {
  const router = useRouter()
  const { signup } = useAuth()
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!EMAIL_RE.test(email.trim())) {
      setError('Please enter a valid email address.')
      return
    }
    if (username.trim().length < 2) {
      setError('Username must be at least 2 characters.')
      return
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsSubmitting(true)
    try {
      await signup(email, username, password)
      // onboarding lives on the login flow — signup drops straight into the app
      router.push('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-spotify-black flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-full bg-spotify-green flex items-center justify-center mb-4">
            <span className="text-black text-2xl">♫</span>
          </div>
          <h1 className="text-white text-3xl font-bold mb-1">Create your account</h1>
          <p className="text-spotify-text-secondary text-sm">Fake auth, stored only in this browser</p>
        </div>

        <form onSubmit={handleSubmit} noValidate className="w-full flex flex-col gap-4">
          {error && (
            <div
              role="alert"
              className="bg-red-500/10 border border-red-500/40 text-red-400 text-sm rounded-md px-4 py-3"
            >
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="text-white text-sm font-medium mb-1 block">
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              disabled={isSubmitting}
              className="w-full bg-spotify-elevated text-white text-sm rounded-md px-4 py-3 outline-none placeholder:text-spotify-text-secondary border border-spotify-border focus:border-white disabled:opacity-60"
            />
          </div>

          <div>
            <label htmlFor="username" className="text-white text-sm font-medium mb-1 block">
              Username
            </label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              disabled={isSubmitting}
              className="w-full bg-spotify-elevated text-white text-sm rounded-md px-4 py-3 outline-none placeholder:text-spotify-text-secondary border border-spotify-border focus:border-white disabled:opacity-60"
            />
          </div>

          <div>
            <label htmlFor="password" className="text-white text-sm font-medium mb-1 block">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password (min. 6 characters)"
              disabled={isSubmitting}
              className="w-full bg-spotify-elevated text-white text-sm rounded-md px-4 py-3 outline-none placeholder:text-spotify-text-secondary border border-spotify-border focus:border-white disabled:opacity-60"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="text-white text-sm font-medium mb-1 block">
              Confirm password
            </label>
            <input
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter your password"
              disabled={isSubmitting}
              className="w-full bg-spotify-elevated text-white text-sm rounded-md px-4 py-3 outline-none placeholder:text-spotify-text-secondary border border-spotify-border focus:border-white disabled:opacity-60"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-spotify-green text-black font-bold py-3 rounded-full hover:bg-spotify-green-hover mt-2 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isSubmitting && (
              <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
            )}
            {isSubmitting ? 'Creating account…' : 'Create Account'}
          </button>

          <p className="text-spotify-text-secondary text-sm text-center mt-4">
            Already have an account?{' '}
            <Link href="/login" className="text-white underline hover:text-spotify-green">
              Log in
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
