'use client'

import type { ReactNode } from 'react'
import { PlayerProvider } from '@/context/PlayerContext'
import { usePlayer } from '@/hooks/usePlayer'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { NowPlayingBar } from './NowPlayingBar'

function AppShellContent({ children }: { children: ReactNode }) {
  const { currentSong, isPlaying, togglePlay } = usePlayer()

  return (
    <div className="h-screen flex flex-col bg-spotify-black">
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <TopBar />
          <div className="px-6 pb-6">{children}</div>
        </main>
      </div>
      <NowPlayingBar currentSong={currentSong} isPlaying={isPlaying} onTogglePlay={togglePlay} />
    </div>
  )
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <PlayerProvider>
      <AppShellContent>{children}</AppShellContent>
    </PlayerProvider>
  )
}
