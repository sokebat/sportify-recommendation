'use client'

import { useState } from 'react'
import { SectionRow } from '@/components/music/SectionRow'
import { usePlayer } from '@/hooks/usePlayer'
import { useArtistDetail } from '@/hooks/useArtistDetail'
import { useArtistRecommendations } from '@/hooks/useArtistRecommendations'
import { externalTrackToSong } from '@/types/spotify'

function formatFollowers(count: number): string {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}K`
  return String(count)
}

export default function ArtistPage() {
  const { playSong } = usePlayer()
  const [artistInput, setArtistInput] = useState('')
  const [submittedArtist, setSubmittedArtist] = useState('')

  const { data, isLoading, error } = useArtistRecommendations({ artist: submittedArtist, n: 15 })
  // Live genres/images/followers/popularity from Spotify; a miss (404) just
  // renders the plain catalog view below. Spotify's API has no biography
  // field, so there's no text bio here - just real, current numbers.
  const detail = useArtistDetail({ name: submittedArtist })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmittedArtist(artistInput.trim())
  }

  const artist = detail.data

  return (
    <div className="pt-6">
      <h1 className="text-white text-2xl font-bold mb-6">Artist</h1>

      <form onSubmit={handleSubmit} className="flex gap-3 mb-8 max-w-xl">
        <input
          type="text"
          value={artistInput}
          onChange={(e) => setArtistInput(e.target.value)}
          placeholder="Artist name (e.g. Ed Sheeran)"
          className="flex-1 bg-spotify-elevated text-white text-sm rounded-md px-4 py-2.5 outline-none placeholder:text-spotify-text-secondary border border-spotify-border focus:border-white"
        />
        <button
          type="submit"
          className="bg-spotify-green text-black font-semibold text-sm rounded-md px-6 hover:bg-spotify-green-hover"
        >
          Search
        </button>
      </form>

      {artist && (
        <div className="relative rounded-lg overflow-hidden mb-8">
          {artist.thumb_url ? (
            // Spotify only gives one photo set, not a separate fanart image -
            // reuse it blurred as the background behind the sharp foreground thumb.
            // eslint-disable-next-line @next/next/no-img-element -- external CDN artwork, not a static/known-domain asset next/image can optimize
            <img src={artist.thumb_url} alt="" className="absolute inset-0 h-full w-full object-cover blur-2xl scale-110" />
          ) : (
            <div className="absolute inset-0 bg-gradient-to-br from-zinc-700 to-zinc-900" />
          )}
          <div className="absolute inset-0 bg-black/60" />

          <div className="relative p-6 pt-16 flex items-end gap-5">
            {artist.thumb_url && (
              // eslint-disable-next-line @next/next/no-img-element -- external CDN artwork, not a static/known-domain asset next/image can optimize
              <img
                src={artist.thumb_url}
                alt={artist.name}
                className="w-28 h-28 rounded-full object-cover border-2 border-white/20 shadow-lg shrink-0"
              />
            )}
            <div className="min-w-0">
              <p className="text-white text-4xl font-extrabold truncate">{artist.name}</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {artist.genres.slice(0, 4).map((genre) => (
                  <span key={genre} className="text-xs font-semibold text-white bg-white/15 rounded-full px-3 py-1">
                    {genre}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-4 mt-3 text-spotify-text-secondary text-sm">
                {typeof artist.followers === 'number' && <span>{formatFollowers(artist.followers)} followers</span>}
                {typeof artist.popularity === 'number' && (
                  <span className="flex items-center gap-2">
                    Popularity
                    <span className="w-24 h-1.5 rounded-full bg-white/15 overflow-hidden">
                      <span className="block h-full bg-spotify-green" style={{ width: `${artist.popularity}%` }} />
                    </span>
                  </span>
                )}
              </div>
              {artist.spotify_url && (
                <a
                  href={artist.spotify_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block mt-3 text-white text-sm font-semibold hover:underline"
                >
                  Open in Spotify
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {submittedArtist && (
        <SectionRow
          title={`Top songs by ${submittedArtist}`}
          songs={data?.results}
          isLoading={isLoading}
          error={error}
          onPlay={playSong}
        />
      )}

      {artist && artist.top_tracks.length > 0 && (
        <SectionRow
          title="Popular on Spotify"
          songs={artist.top_tracks.map(externalTrackToSong)}
          onPlay={playSong}
        />
      )}

      {error && <p className="text-red-500 text-sm">{error.message}</p>}
    </div>
  )
}
