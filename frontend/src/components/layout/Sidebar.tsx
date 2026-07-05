'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/cn'
import { navItems } from '@/lib/constants'

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-60 bg-black h-full flex flex-col px-2 py-4 gap-2">
      <div className="px-3 py-2 mb-4">
        <h1 className="text-white text-xl font-bold">Spotify</h1>
      </div>

      <nav className="flex flex-col gap-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-4 px-3 py-2.5 rounded text-sm font-medium transition-colors',
                isActive ? 'bg-spotify-hover text-white' : 'text-spotify-text-secondary hover:text-white',
              )}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
