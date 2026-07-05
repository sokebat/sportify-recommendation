'use client'

import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface CardProps {
  children: ReactNode
  className?: string
  onClick?: () => void
}

export function Card({ children, className, onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-spotify-elevated hover:bg-spotify-hover rounded-md p-4 transition-colors duration-200 cursor-pointer group',
        className,
      )}
    >
      {children}
    </div>
  )
}
