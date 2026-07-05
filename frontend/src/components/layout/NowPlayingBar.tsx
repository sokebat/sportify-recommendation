'use client'

import { VinylSpinner } from '@/components/music/VinylSpinner'
import type { Song } from '@/types/song'

interface NowPlayingBarProps {
  currentSong: Song | null
  isPlaying: boolean
  onTogglePlay: () => void
}

export function NowPlayingBar({ currentSong, isPlaying, onTogglePlay }: NowPlayingBarProps) {
  if (!currentSong) {
    return (
      <footer className="h-20 bg-spotify-elevated border-t border-spotify-border flex items-center justify-center">
        <p className="text-spotify-text-secondary text-sm">No song playing</p>
      </footer>
    )
  }

  return (
    <footer className="h-20 bg-spotify-elevated border-t border-spotify-border flex items-center justify-between px-4">
      <div className="flex items-center gap-3 w-1/3 min-w-0">
        <VinylSpinner size="sm" isPlaying={isPlaying} />
        <div className="min-w-0">
          <p className="text-white text-sm font-medium truncate">{currentSong.track_name}</p>
          <p className="text-spotify-text-secondary text-xs truncate">{currentSong.artists}</p>
        </div>
      </div>

      <div className="flex flex-col items-center gap-2 w-1/3">
        <button
          onClick={onTogglePlay}
          className="w-9 h-9 rounded-full bg-white flex items-center justify-center hover:scale-105 transition-transform"
        >
          {isPlaying ? (
            <svg viewBox="0 0 24 24" fill="black" className="w-4 h-4">
              <rect x="6" y="5" width="4" height="14" />
              <rect x="14" y="5" width="4" height="14" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="black" className="w-4 h-4 ml-0.5">
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </button>
      </div>

      <div className="w-1/3" />
    </footer>
  )
}
