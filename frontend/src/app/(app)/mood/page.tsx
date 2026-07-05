'use client'

import { useState } from 'react'
import { SectionRow } from '@/components/music/SectionRow'
import { usePlayer } from '@/hooks/usePlayer'
import { useMoodRecommendations } from '@/hooks/useMoodRecommendations'
import { moodTiles } from '@/lib/constants'
import { cn } from '@/lib/cn'

export default function MoodPage() {
  const { playSong } = usePlayer()
  const [selectedMood, setSelectedMood] = useState<string | null>(null)

  const { data, isLoading, error } = useMoodRecommendations({ mood: selectedMood, n: 15 })

  return (
    <div className="pt-6">
      <h1 className="text-white text-2xl font-bold mb-6">What&apos;s your mood?</h1>

      <div className="grid grid-cols-4 gap-4 mb-8">
        {moodTiles.map((mood) => (
          <button
            key={mood.id}
            onClick={() => setSelectedMood(mood.id)}
            className={cn(
              'h-32 rounded-lg bg-gradient-to-br flex items-end p-4 transition-transform hover:scale-105',
              mood.color,
              selectedMood === mood.id && 'ring-2 ring-white',
            )}
          >
            <span className="text-white text-xl font-bold">{mood.label}</span>
          </button>
        ))}
      </div>

      {selectedMood && (
        <SectionRow
          title={`${moodTiles.find((m) => m.id === selectedMood)?.label} songs`}
          songs={data?.results}
          isLoading={isLoading}
          error={error}
          onPlay={playSong}
        />
      )}
    </div>
  )
}
