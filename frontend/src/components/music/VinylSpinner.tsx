import { cn } from '@/lib/cn'

type SpinnerSize = 'sm' | 'md' | 'lg'

const sizeClasses: Record<SpinnerSize, string> = {
  sm: 'w-10 h-10',
  md: 'w-14 h-14',
  lg: 'w-48 h-48',
}

export function VinylSpinner({ isPlaying = false, size = 'md' }: { isPlaying?: boolean; size?: SpinnerSize }) {
  return (
    <div
      className={cn(
        'rounded-full bg-zinc-900 border-4 border-zinc-800 flex items-center justify-center',
        sizeClasses[size],
        isPlaying && 'animate-spin-slow',
      )}
      style={{
        backgroundImage:
          'repeating-radial-gradient(circle, #1a1a1a 0px, #1a1a1a 2px, #0d0d0d 2px, #0d0d0d 4px)',
      }}
    >
      <div className="w-1/3 h-1/3 rounded-full bg-spotify-green" />
    </div>
  )
}
