'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { SongAutocomplete } from '@/components/music/SongAutocomplete'
import { UserMenu } from './UserMenu'
import { useAuth } from '@/hooks/useAuth'
import type { Song } from '@/types/song'

export function TopBar() {
  const router = useRouter()
  const { user, isHydrated } = useAuth()
  const [query, setQuery] = useState('')

  const handleSelect = (song: Song) => {
    const artist = song.artists.split(';')[0]
    router.push(`/search?q=${encodeURIComponent(song.track_name)}&artist=${encodeURIComponent(artist)}`)
    setQuery('')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`)
      setQuery('')
    }
  }

  return (
    <header className="h-16 flex items-center justify-between px-6 bg-spotify-black/80 backdrop-blur sticky top-0 z-10 gap-4">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="w-8 h-8 rounded-full bg-black/60 flex items-center justify-center text-white hover:bg-black"
        >
          ←
        </button>
        <button
          onClick={() => router.forward()}
          className="w-8 h-8 rounded-full bg-black/60 flex items-center justify-center text-white hover:bg-black"
        >
          →
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex-1 max-w-md">
        <SongAutocomplete
          value={query}
          onChange={setQuery}
          onSelect={handleSelect}
          placeholder="What do you want to play?"
        />
      </form>

      <div className="flex items-center gap-3">
        {!isHydrated ? (
          <div className="w-8 h-8 rounded-full bg-spotify-elevated animate-pulse" />
        ) : user ? (
          <UserMenu user={user} />
        ) : (
          <>
            <Button variant="outline" onClick={() => router.push('/login')}>
              Log in
            </Button>
            <Button variant="primary" onClick={() => router.push('/signup')}>
              Sign up
            </Button>
          </>
        )}
      </div>
    </header>
  )
}
