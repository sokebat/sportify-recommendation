'use client'

import { VinylSpinner } from '@/components/music/VinylSpinner'
import type { Song } from '@/types/song'

interface NowPlayingBarProps {
  currentSong: Song | null
  isPlaying: boolean
  onTogglePlay: () => void
}

export function NowPlayingBar({ currentSong, isPlaying, onTogglePlay }: NowPlayingBarProps) {
  // Externally sourced songs already carry their own spotify_url; catalog
  // songs don't need a fetch for this at all - their track_id IS a real
  // Spotify track ID, so the link is fully derivable client-side.
  const spotifyUrl =
    currentSong?.spotify_url ?? (currentSong?.track_id ? `https://open.spotify.com/track/${currentSong.track_id}` : undefined)

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

      <div className="w-1/3 flex items-center justify-end">
        {spotifyUrl && (
          <a
            href={spotifyUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 text-spotify-text-secondary hover:text-white text-xs font-semibold transition-colors"
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor">
              <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" />
              <path
                d="M7 9.5c2.8-.8 6.4-.6 8.7.8M7.3 12.3c2.3-.6 5.3-.4 7.2.7M7.6 14.9c1.9-.4 4.3-.3 5.9.6"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.4"
                strokeLinecap="round"
              />
            </svg>
            Open in Spotify
          </a>
        )}
      </div>
    </footer>
  )
}
