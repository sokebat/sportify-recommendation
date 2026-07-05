'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useClickOutside } from '@/hooks/useClickOutside'
import { cn } from '@/lib/cn'
import type { AuthUser } from '@/context/AuthContext'

export function UserMenu({ user }: { user: AuthUser }) {
  const router = useRouter()
  const { logout } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const ref = useClickOutside<HTMLDivElement>(() => setIsOpen(false))
  const initial = (user.username || user.email).charAt(0).toUpperCase()

  const handleLogout = () => {
    setIsOpen(false)
    logout()
    router.push('/')
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-8 h-8 rounded-full bg-spotify-elevated border border-spotify-border flex items-center justify-center text-white text-sm font-bold hover:border-white transition-colors"
        aria-haspopup="menu"
        aria-expanded={isOpen}
      >
        {initial}
      </button>

      <div
        role="menu"
        className={cn(
          'absolute right-0 mt-2 w-56 rounded-md bg-spotify-elevated border border-spotify-border shadow-xl py-1 origin-top-right transition-all',
          isOpen ? 'opacity-100 scale-100 pointer-events-auto' : 'opacity-0 scale-95 pointer-events-none',
        )}
      >
        <div className="px-4 py-3 border-b border-spotify-border">
          <p className="text-white text-sm font-semibold truncate">{user.username}</p>
          <p className="text-spotify-text-secondary text-xs truncate">{user.email}</p>
        </div>
        <button
          role="menuitem"
          onClick={handleLogout}
          className="w-full text-left px-4 py-2.5 text-sm text-white hover:bg-spotify-hover transition-colors"
        >
          Log out
        </button>
      </div>
    </div>
  )
}
