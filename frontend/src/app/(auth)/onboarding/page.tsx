'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { SectionRow } from '@/components/music/SectionRow'
import { useGenreRecommendations } from '@/hooks/useGenreRecommendations'
import { useMoodRecommendations } from '@/hooks/useMoodRecommendations'
import { cn } from '@/lib/cn'
import { onboardingGenres, onboardingMoods, toGenreApiId } from '@/lib/constants'

export default function OnboardingPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [selectedGenres, setSelectedGenres] = useState<string[]>([])
  const [selectedMoods, setSelectedMoods] = useState<string[]>([])

  const toggleGenre = (genre: string) => {
    setSelectedGenres((prev) => (prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]))
  }

  const toggleMood = (mood: string) => {
    setSelectedMoods((prev) => (prev.includes(mood) ? prev.filter((m) => m !== mood) : [...prev, mood]))
  }

  const primaryGenre = selectedGenres[0]
  const primaryMood = selectedMoods[0]
  const primaryMoodLabel = onboardingMoods.find((m) => m.id === primaryMood)?.label

  // Only fetch once the listener actually reaches the results step, not
  // while they're still picking genres/moods on steps 1-2.
  const genreRecs = useGenreRecommendations({
    genre: step === 3 && primaryGenre ? toGenreApiId(primaryGenre) : null,
    n: 6,
  })
  const moodRecs = useMoodRecommendations({ mood: step === 3 ? primaryMood : null, n: 6 })

  const handleFinish = () => {
    // in real app → save preferences to backend/context
    router.push('/')
  }

  return (
    <div className="min-h-screen bg-spotify-black flex flex-col items-center justify-center px-6 py-12">
      <div className={cn('w-full transition-all', step === 3 ? 'max-w-4xl' : 'max-w-lg')}>
        {/* progress bar */}
        <div className="flex gap-2 mb-10">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={cn('h-1 flex-1 rounded-full transition-colors', s <= step ? 'bg-spotify-green' : 'bg-spotify-elevated')}
            />
          ))}
        </div>

        {step === 1 && (
          <>
            <h1 className="text-white text-2xl font-bold mb-2">What kind of music do you like?</h1>
            <p className="text-spotify-text-secondary text-sm mb-6">Pick at least 3 genres to get started.</p>

            <div className="flex flex-wrap gap-3 mb-10">
              {onboardingGenres.map((genre) => (
                <button
                  key={genre}
                  onClick={() => toggleGenre(genre)}
                  className={cn(
                    'px-4 py-2 rounded-full text-sm font-medium border transition-colors',
                    selectedGenres.includes(genre)
                      ? 'bg-spotify-green text-black border-spotify-green'
                      : 'bg-transparent text-white border-spotify-border hover:border-white',
                  )}
                >
                  {genre}
                </button>
              ))}
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={selectedGenres.length < 3}
              className="w-full bg-spotify-green text-black font-bold py-3 rounded-full hover:bg-spotify-green-hover disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </>
        )}

        {step === 2 && (
          <>
            <h1 className="text-white text-2xl font-bold mb-2">What&apos;s your vibe?</h1>
            <p className="text-spotify-text-secondary text-sm mb-6">Pick one or more moods that match how you feel.</p>

            <div className="grid grid-cols-2 gap-4 mb-10">
              {onboardingMoods.map((mood) => (
                <button
                  key={mood.id}
                  onClick={() => toggleMood(mood.id)}
                  className={cn(
                    'h-24 rounded-lg flex flex-col items-center justify-center gap-2 border-2 transition-colors',
                    selectedMoods.includes(mood.id)
                      ? 'border-spotify-green bg-spotify-green/10'
                      : 'border-spotify-border bg-spotify-elevated hover:border-white',
                  )}
                >
                  <span className="text-3xl">{mood.emoji}</span>
                  <span className="text-white font-medium">{mood.label}</span>
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 border border-spotify-border text-white font-bold py-3 rounded-full hover:border-white"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={selectedMoods.length === 0}
                className="flex-1 bg-spotify-green text-black font-bold py-3 rounded-full hover:bg-spotify-green-hover disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <h1 className="text-white text-2xl font-bold mb-2">Here&apos;s what we found for you</h1>
            <p className="text-spotify-text-secondary text-sm mb-8">
              Picked from {primaryGenre} and your {primaryMoodLabel?.toLowerCase()} mood.
            </p>

            <SectionRow
              title={`${primaryGenre} picks`}
              songs={genreRecs.data?.results}
              isLoading={genreRecs.isLoading}
              error={genreRecs.error}
            />
            <SectionRow
              title={`${primaryMoodLabel} vibes`}
              songs={moodRecs.data?.results}
              isLoading={moodRecs.isLoading}
              error={moodRecs.error}
            />

            <div className="flex gap-3 mt-2">
              <button
                onClick={() => setStep(2)}
                className="flex-1 border border-spotify-border text-white font-bold py-3 rounded-full hover:border-white"
              >
                Back
              </button>
              <button
                onClick={handleFinish}
                className="flex-1 bg-spotify-green text-black font-bold py-3 rounded-full hover:bg-spotify-green-hover"
              >
                Let&apos;s Go!
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
