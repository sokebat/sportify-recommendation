'use client'

import { SectionRow } from '@/components/music/SectionRow'
import { usePlayer } from '@/hooks/usePlayer'
import { usePopularityRecommendations } from '@/hooks/usePopularityRecommendations'
import { useMoodRecommendations } from '@/hooks/useMoodRecommendations'
import { useGenreRecommendations } from '@/hooks/useGenreRecommendations'

export default function HomePage() {
  const { playSong } = usePlayer()

  const popular = usePopularityRecommendations({ n: 10 })
  const happy = useMoodRecommendations({ mood: 'happy', n: 10 })
  const rock = useGenreRecommendations({ genre: 'rock', n: 10 })
  const pop = useGenreRecommendations({ genre: 'pop', n: 10 })

  return (
    <div className="pt-6">
      <h1 className="text-white text-2xl font-bold mb-6">Good evening</h1>

      <SectionRow
        title="Popular right now"
        songs={popular.data?.results}
        isLoading={popular.isLoading}
        error={popular.error}
        onPlay={playSong}
      />

      <SectionRow
        title="Happy vibes"
        songs={happy.data?.results}
        isLoading={happy.isLoading}
        error={happy.error}
        onPlay={playSong}
      />

      <SectionRow
        title="Rock essentials"
        songs={rock.data?.results}
        isLoading={rock.isLoading}
        error={rock.error}
        onPlay={playSong}
      />

      <SectionRow
        title="Pop essentials"
        songs={pop.data?.results}
        isLoading={pop.isLoading}
        error={pop.error}
        onPlay={playSong}
      />
    </div>
  )
}
