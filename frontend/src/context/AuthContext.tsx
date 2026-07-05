'use client'

import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

export interface AuthUser {
  email: string
  username: string
}

interface StoredAccount extends AuthUser {
  password: string
}

export interface AuthContextValue {
  user: AuthUser | null
  isHydrated: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, username: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

const ACCOUNTS_KEY = 'sportify_accounts'
const SESSION_KEY = 'sportify_session'

// Fake network latency so the loading state on the forms feels real.
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function readAccounts(): StoredAccount[] {
  try {
    return JSON.parse(localStorage.getItem(ACCOUNTS_KEY) ?? '[]')
  } catch {
    return []
  }
}

function writeAccounts(accounts: StoredAccount[]) {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts))
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isHydrated, setIsHydrated] = useState(false)

  // Session lives in localStorage so a refresh doesn't kick the user back
  // out to a logged-out state.
  useEffect(() => {
    try {
      const stored = localStorage.getItem(SESSION_KEY)
      if (stored) setUser(JSON.parse(stored))
    } catch {
      // corrupt/blocked storage — treat as logged out
    } finally {
      setIsHydrated(true)
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    await delay(500)
    const normalizedEmail = email.trim().toLowerCase()
    const account = readAccounts().find((a) => a.email === normalizedEmail)
    if (!account) {
      throw new Error('No account found with that email. Try signing up instead.')
    }
    if (account.password !== password) {
      throw new Error('Incorrect password. Please try again.')
    }
    const sessionUser: AuthUser = { email: account.email, username: account.username }
    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionUser))
    setUser(sessionUser)
  }, [])

  const signup = useCallback(async (email: string, username: string, password: string) => {
    await delay(500)
    const normalizedEmail = email.trim().toLowerCase()
    const accounts = readAccounts()
    if (accounts.some((a) => a.email === normalizedEmail)) {
      throw new Error('An account with that email already exists. Try logging in instead.')
    }
    const account: StoredAccount = { email: normalizedEmail, username: username.trim(), password }
    writeAccounts([...accounts, account])
    const sessionUser: AuthUser = { email: account.email, username: account.username }
    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionUser))
    setUser(sessionUser)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(SESSION_KEY)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, isHydrated, login, signup, logout }),
    [user, isHydrated, login, signup, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
