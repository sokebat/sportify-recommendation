'use client'

import { useState } from 'react'
import { useClickOutside } from '@/hooks/useClickOutside'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'
import { useSongSearch } from '@/hooks/useSongSearch'
import type { Song } from '@/types/song'

interface SongAutocompleteProps {
  value: string
  onChange: (value: string) => void
  onSelect: (song: Song) => void
  placeholder?: string
}

export function SongAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = 'Search a song...',
}: SongAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useClickOutside<HTMLDivElement>(() => setIsOpen(false))

  const debouncedValue = useDebouncedValue(value, 250)
  const { data, isLoading } = useSongSearch({ query: debouncedValue, n: 8 })

  const handleChange = (newValue: string) => {
    onChange(newValue)
    setIsOpen(newValue.trim().length >= 2)
  }

  const handleSelect = (song: Song) => {
    onSelect(song)
    setIsOpen(false)
  }

  const showDropdown = isOpen && value.trim().length >= 2

  return (
    <div ref={containerRef} className="relative flex-1">
      <input
        type="text"
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        onFocus={() => value.trim().length >= 2 && setIsOpen(true)}
        placeholder={placeholder}
        className="w-full bg-spotify-elevated text-white text-sm rounded-md px-4 py-2.5 outline-none placeholder:text-spotify-text-secondary border border-spotify-border focus:border-white"
      />

      {showDropdown && (
        <div className="absolute z-20 mt-1 w-full bg-spotify-elevated border border-spotify-border rounded-md shadow-xl max-h-72 overflow-y-auto">
          {isLoading && <p className="text-spotify-text-secondary text-sm px-4 py-3">Searching...</p>}

          {!isLoading && data?.results?.length === 0 && (
            <p className="text-spotify-text-secondary text-sm px-4 py-3">No matches found</p>
          )}

          {!isLoading &&
            data?.results?.map((song, i) => (
              <button
                key={song.track_id ?? i}
                onClick={() => handleSelect(song)}
                className="w-full text-left px-4 py-2.5 hover:bg-spotify-hover transition-colors flex flex-col"
              >
                <span className="text-white text-sm font-medium truncate">{song.track_name}</span>
                <span className="text-spotify-text-secondary text-xs truncate">
                  {song.artists} · {song.track_genre}
                </span>
              </button>
            ))}
        </div>
      )}
    </div>
  )
}
