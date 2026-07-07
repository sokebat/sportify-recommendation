'use client'

import { useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { SectionRow } from '@/components/music/SectionRow'
import { SongAutocomplete } from '@/components/music/SongAutocomplete'
import { TrackCoverImage } from '@/components/music/TrackCoverImage'
import { usePlayer } from '@/hooks/usePlayer'
import { useExternalRecommendations } from '@/hooks/useExternalRecommendations'
import { useSimilarSongs } from '@/hooks/useSimilarSongs'
import { useSongSearch } from '@/hooks/useSongSearch'
import type { Song } from '@/types/song'

export function SearchView() {
  const { playSong } = usePlayer()
  const searchParams = useSearchParams()
  const initialQuery = searchParams.get('q') || ''
  const initialArtist = searchParams.get('artist') || ''
  // src=external marks a track that came from live data (e.g. the Trending
  // row) rather than the catalog: recommendations then go through the
  // backend's bridge endpoint instead of the catalog-only similar-song one.
  const initialIsExternal = searchParams.get('src') === 'external'
  const initialGenre = searchParams.get('genre') || ''
  const initialSpotifyId = searchParams.get('spotifyId') || ''

  const [songName, setSongName] = useState(initialQuery)
  const [artist, setArtist] = useState('')
  const [submittedQuery, setSubmittedQuery] = useState(initialQuery)
  const [submittedArtist, setSubmittedArtist] = useState(initialArtist)
  const [externalMode, setExternalMode] = useState(initialIsExternal)

  // Re-sync local state when the URL's ?q=/&artist= change (e.g. a fresh
  // TopBar search) without remounting this component. Adjusting state during
  // render — rather than in an effect — avoids an extra cascading re-render.
  const [syncedQuery, setSyncedQuery] = useState(initialQuery)
  if (initialQuery && initialQuery !== syncedQuery) {
    setSyncedQuery(initialQuery)
    setSongName(initialQuery)
    setSubmittedQuery(initialQuery)
    setSubmittedArtist(initialArtist)
    setExternalMode(initialIsExternal)
  }

  // fetch the exact searched song itself (top match) to show as hero;
  // external tracks aren't in the catalog, so skip it in external mode
  const { data: exactMatchData } = useSongSearch({ query: externalMode ? '' : submittedQuery, n: 1 })

  const similar = useSimilarSongs({
    songName: externalMode ? '' : submittedQuery,
    artist: submittedArtist || undefined,
    n: 15,
  })

  const external = useExternalRecommendations({
    artist: submittedArtist,
    track: submittedQuery,
    spotifyId: initialSpotifyId || undefined,
    genre: initialGenre || undefined,
    n: 15,
    enabled: externalMode,
  })

  const { data, isLoading, error } = externalMode ? external : similar

  const handleSelect = (song: Song) => {
    const firstArtist = song.artists.split(';')[0]
    setSongName(song.track_name)
    setArtist(firstArtist)
    setSubmittedQuery(song.track_name)
    setSubmittedArtist(firstArtist)
    setExternalMode(false)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmittedQuery(songName.trim())
    setSubmittedArtist(artist.trim())
    setExternalMode(false)
  }

  // In external mode the hero is the catalog track the backend actually
  // seeded the models with (absent on a genre-only match).
  const heroSong = externalMode ? external.data?.seed : exactMatchData?.results?.[0]

  const matchedBy = externalMode ? external.data?.matched_by : undefined
  const rowTitle =
    matchedBy === 'artist'
      ? `Because you like ${submittedArtist}`
      : matchedBy === 'genre'
        ? initialGenre
          ? `More ${initialGenre} for you`
          : 'Songs for you'
        : `Songs similar to "${submittedQuery}"`

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

      {heroSong && (
        <div
          onClick={() => playSong(heroSong)}
          className="flex items-center gap-4 bg-spotify-elevated hover:bg-spotify-hover rounded-md p-4 mb-8 max-w-xl cursor-pointer group"
        >
          <div className="relative w-16 h-16 rounded overflow-hidden shrink-0">
            <TrackCoverImage
              trackId={heroSong.track_id}
              src={heroSong.cover_url}
              className="absolute inset-0 h-full w-full"
            />
            <svg
              viewBox="0 0 24 24"
              fill="white"
              className="absolute inset-0 m-auto w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity drop-shadow"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
          <div className="min-w-0">
            <p className="text-spotify-text-secondary text-xs uppercase tracking-wide mb-1">
              {matchedBy === 'artist' ? 'Seeded from' : 'Now playing'}
            </p>
            <p className="text-white font-semibold truncate">{heroSong.track_name}</p>
            <p className="text-spotify-text-secondary text-sm truncate">{heroSong.artists}</p>
          </div>
        </div>
      )}

      {submittedQuery && (
        <SectionRow
          title={rowTitle}
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
