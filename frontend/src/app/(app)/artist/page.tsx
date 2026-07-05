'use client'

import { useState } from 'react'
import { SectionRow } from '@/components/music/SectionRow'
import { usePlayer } from '@/hooks/usePlayer'
import { useArtistRecommendations } from '@/hooks/useArtistRecommendations'

export default function ArtistPage() {
  const { playSong } = usePlayer()
  const [artistInput, setArtistInput] = useState('')
  const [submittedArtist, setSubmittedArtist] = useState('')

  const { data, isLoading, error } = useArtistRecommendations({ artist: submittedArtist, n: 15 })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmittedArtist(artistInput.trim())
  }

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

      {submittedArtist && (
        <SectionRow
          title={`Top songs by ${submittedArtist}`}
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
