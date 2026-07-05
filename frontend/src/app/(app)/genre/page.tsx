'use client'

import { useState } from 'react'
import { SectionRow } from '@/components/music/SectionRow'
import { usePlayer } from '@/hooks/usePlayer'
import { useGenreRecommendations } from '@/hooks/useGenreRecommendations'
import { genreTiles } from '@/lib/constants'
import { GenreTile } from './GenreTile'

export default function GenrePage() {
  const { playSong } = usePlayer()
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null)

  const { data, isLoading, error } = useGenreRecommendations({ genre: selectedGenre, n: 15 })

  return (
    <div className="pt-6">
      <h1 className="text-white text-2xl font-bold mb-6">Browse Genres</h1>

      <div className="grid grid-cols-4 gap-4 mb-8">
        {genreTiles.map((genre) => (
          <GenreTile
            key={genre.id}
            genre={genre}
            isSelected={selectedGenre === genre.id}
            onClick={() => setSelectedGenre(genre.id)}
          />
        ))}
      </div>

      {selectedGenre && (
        <SectionRow
          title={`${genreTiles.find((g) => g.id === selectedGenre)?.label} essentials`}
          songs={data?.results}
          isLoading={isLoading}
          error={error}
          onPlay={playSong}
        />
      )}
    </div>
  )
}
