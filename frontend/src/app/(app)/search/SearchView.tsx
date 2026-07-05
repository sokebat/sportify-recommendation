'use client'

import { useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { SectionRow } from '@/components/music/SectionRow'
import { SongAutocomplete } from '@/components/music/SongAutocomplete'
import { TrackCoverImage } from '@/components/music/TrackCoverImage'
import { usePlayer } from '@/hooks/usePlayer'
import { useSimilarSongs } from '@/hooks/useSimilarSongs'
import { useSongSearch } from '@/hooks/useSongSearch'
import type { Song } from '@/types/song'

export function SearchView() {
  const { playSong } = usePlayer()
  const searchParams = useSearchParams()
  const initialQuery = searchParams.get('q') || ''
  const initialArtist = searchParams.get('artist') || ''

  const [songName, setSongName] = useState(initialQuery)
  const [artist, setArtist] = useState('')
  const [submittedQuery, setSubmittedQuery] = useState(initialQuery)
  const [submittedArtist, setSubmittedArtist] = useState(initialArtist)

  // Re-sync local state when the URL's ?q=/&artist= change (e.g. a fresh
  // TopBar search) without remounting this component. Adjusting state during
  // render — rather than in an effect — avoids an extra cascading re-render.
  const [syncedQuery, setSyncedQuery] = useState(initialQuery)
  if (initialQuery && initialQuery !== syncedQuery) {
    setSyncedQuery(initialQuery)
    setSongName(initialQuery)
    setSubmittedQuery(initialQuery)
    setSubmittedArtist(initialArtist)
  }

  // fetch the exact searched song itself (top match) to show as hero
  const { data: exactMatchData } = useSongSearch({ query: submittedQuery, n: 1 })

  const { data, isLoading, error } = useSimilarSongs({
    songName: submittedQuery,
    artist: submittedArtist || undefined,
    n: 15,
  })

  const handleSelect = (song: Song) => {
    const firstArtist = song.artists.split(';')[0]
    setSongName(song.track_name)
    setArtist(firstArtist)
    setSubmittedQuery(song.track_name)
    setSubmittedArtist(firstArtist)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmittedQuery(songName.trim())
    setSubmittedArtist(artist.trim())
  }

  const exactSong = exactMatchData?.results?.[0]

  return (
    <div className="pt-6">
      <h1 className="text-white text-2xl font-bold mb-6">Find songs like...</h1>

      <form onSubmit={handleSubmit} className="flex gap-3 mb-8 max-w-xl">
        <SongAutocomplete
          value={songName}
          onChange={setSongName}
          onSelect={handleSelect}
          placeholder="Song name (e.g. Shape of You)"
        />
        <button
          type="submit"
          className="bg-spotify-green text-black font-semibold text-sm rounded-md px-6 hover:bg-spotify-green-hover"
        >
          Search
        </button>
      </form>

      {exactSong && (
        <div
          onClick={() => playSong(exactSong)}
          className="flex items-center gap-4 bg-spotify-elevated hover:bg-spotify-hover rounded-md p-4 mb-8 max-w-xl cursor-pointer group"
        >
          <div className="relative w-16 h-16 rounded overflow-hidden shrink-0">
            <TrackCoverImage trackId={exactSong.track_id} className="absolute inset-0 h-full w-full" />
            <svg
              viewBox="0 0 24 24"
              fill="white"
              className="absolute inset-0 m-auto w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity drop-shadow"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
          <div className="min-w-0">
            <p className="text-spotify-text-secondary text-xs uppercase tracking-wide mb-1">Now playing</p>
            <p className="text-white font-semibold truncate">{exactSong.track_name}</p>
            <p className="text-spotify-text-secondary text-sm truncate">{exactSong.artists}</p>
          </div>
        </div>
      )}

      {submittedQuery && (
        <SectionRow
          title={`Songs similar to "${submittedQuery}"`}
          songs={data?.results}
          isLoading={isLoading}
          error={error}
          onPlay={playSong}
        />
      )}

      {error && <p className="text-red-500 text-sm">{error.message}</p>}
    </div>
  )
}
