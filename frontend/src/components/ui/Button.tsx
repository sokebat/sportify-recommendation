'use client'

import type { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-spotify-green text-black hover:bg-spotify-green-hover',
  secondary: 'bg-white text-black hover:scale-105',
  outline: 'border border-spotify-border text-white hover:border-white',
  ghost: 'text-spotify-text-secondary hover:text-white',
}

export function Button({ children, variant = 'primary', className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'rounded-full font-semibold px-6 py-2.5 text-sm transition-colors duration-150',
        variantClasses[variant],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  )
}
