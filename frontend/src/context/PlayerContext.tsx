'use client'

import { createContext, useCallback, useMemo, useState, type ReactNode } from 'react'
import type { Song } from '@/types/song'

export interface PlayerContextValue {
  currentSong: Song | null
  isPlaying: boolean
  playSong: (song: Song) => void
  togglePlay: () => void
}

export const PlayerContext = createContext<PlayerContextValue | null>(null)

export function PlayerProvider({ children }: { children: ReactNode }) {
  const [currentSong, setCurrentSong] = useState<Song | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const playSong = useCallback((song: Song) => {
    setCurrentSong(song)
    setIsPlaying(true)
  }, [])

  const togglePlay = useCallback(() => {
    setIsPlaying((prev) => !prev)
  }, [])

  const value = useMemo(
    () => ({ currentSong, isPlaying, playSong, togglePlay }),
    [currentSong, isPlaying, playSong, togglePlay],
  )

  return <PlayerContext.Provider value={value}>{children}</PlayerContext.Provider>
}
