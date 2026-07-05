'use client'

import { cn } from '@/lib/cn'

interface GenreTileProps {
  genre: { id: string; label: string; color: string }
  isSelected: boolean
  onClick: () => void
}

export function GenreTile({ genre, isSelected, onClick }: GenreTileProps) {
  return (
    <button
      onClick={onClick}
      style={{ backgroundColor: genre.color }}
      className={cn(
        'relative h-32 rounded-lg p-4 overflow-hidden text-left transition-transform hover:scale-[1.02]',
        isSelected && 'ring-2 ring-white',
      )}
    >
      <span className="text-white text-xl font-bold relative z-10">{genre.label}</span>
      <div
        className="absolute -right-3 -bottom-4 w-20 h-20 rounded-md rotate-[25deg] shadow-xl"
        style={{ backgroundColor: 'rgba(0,0,0,0.25)' }}
      />
    </button>
  )
}
