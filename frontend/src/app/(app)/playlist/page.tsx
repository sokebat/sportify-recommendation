'use client'

import { useState } from 'react'
import { SectionRow } from '@/components/music/SectionRow'
import { SongAutocomplete } from '@/components/music/SongAutocomplete'
import { usePlayer } from '@/hooks/usePlayer'
import { usePlaylistRecommendations } from '@/hooks/usePlaylistRecommendations'
import type { Song } from '@/types/song'

export default function PlaylistPage() {
  const { playSong } = usePlayer()
  const [songInput, setSongInput] = useState('')
  const [playlistSongs, setPlaylistSongs] = useState<string[]>([])
  const [submitted, setSubmitted] = useState(false)

  const { data, isLoading, error } = usePlaylistRecommendations({
    songs: playlistSongs,
    n: 15,
    enabled: submitted,
  })

  const addSongByName = (name: string) => {
    const trimmed = name.trim()
    if (trimmed && !playlistSongs.includes(trimmed)) {
      setPlaylistSongs([...playlistSongs, trimmed])
      setSongInput('')
      setSubmitted(false)
    }
  }

  const handleSelect = (song: Song) => {
    addSongByName(song.track_name)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addSongByName(songInput)
  }

  const removeSong = (song: string) => {
    setPlaylistSongs(playlistSongs.filter((s) => s !== song))
    setSubmitted(false)
  }

  const getRecommendations = () => {
    if (playlistSongs.length > 0) setSubmitted(true)
  }

  return (
    <div className="pt-6">
      <h1 className="text-white text-2xl font-bold mb-6">Build a Playlist</h1>

      <form onSubmit={handleSubmit} className="flex gap-3 mb-4 max-w-xl">
        <SongAutocomplete
          value={songInput}
          onChange={setSongInput}
          onSelect={handleSelect}
          placeholder="Add a song (e.g. Blinding Lights)"
        />
        <button
          type="submit"
          className="bg-white text-black font-semibold text-sm rounded-md px-6 hover:scale-105 transition-transform"
        >
          Add
        </button>
      </form>

      {playlistSongs.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          {playlistSongs.map((song) => (
            <span
              key={song}
              className="bg-spotify-elevated text-white text-sm rounded-full pl-4 pr-2 py-1.5 flex items-center gap-2"
            >
              {song}
              <button
                onClick={() => removeSong(song)}
                className="w-5 h-5 rounded-full bg-spotify-hover hover:bg-zinc-700 flex items-center justify-center text-xs"
              >
                ✕
              </button>
            </span>
          ))}
        </div>
      )}

      {playlistSongs.length > 0 && (
        <button
          onClick={getRecommendations}
          className="bg-spotify-green text-black font-semibold text-sm rounded-full px-6 py-2.5 mb-8 hover:bg-spotify-green-hover"
        >
          Get Recommendations
        </button>
      )}

      {submitted && (
        <SectionRow
          title="Picked for your playlist"
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
