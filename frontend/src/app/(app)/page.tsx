'use client'

import { useRouter } from 'next/navigation'
import { SectionRow } from '@/components/music/SectionRow'
import { usePlayer } from '@/hooks/usePlayer'
import { usePopularityRecommendations } from '@/hooks/usePopularityRecommendations'
import { useMoodRecommendations } from '@/hooks/useMoodRecommendations'
import { useGenreRecommendations } from '@/hooks/useGenreRecommendations'
import { useTrending } from '@/hooks/useTrending'
import { externalTrackToSong } from '@/types/spotify'
import type { Song } from '@/types/song'

export default function HomePage() {
  const { playSong } = usePlayer()
  const router = useRouter()

  const trending = useTrending({ limit: 12 })
  const popular = usePopularityRecommendations({ n: 10 })
  const happy = useMoodRecommendations({ mood: 'happy', n: 10 })
  const rock = useGenreRecommendations({ genre: 'rock', n: 10 })
  const pop = useGenreRecommendations({ genre: 'pop', n: 10 })

  // Trending tracks are Spotify's live "Top 50 - Global" chart, usually not
  // in the older static catalog - play them and land on the search page in
  // external mode, where the backend bridges them into the models (Spotify
  // ID/name -> artist -> genre).
  const playTrendingSong = (song: Song) => {
    playSong(song)
    const params = new URLSearchParams({ q: song.track_name, artist: song.artists, src: 'external' })
    if (song.spotify_id) params.set('spotifyId', song.spotify_id)
    router.push(`/search?${params.toString()}`)
  }

  return (
    <div className="pt-6">
      <h1 className="text-white text-2xl font-bold mb-6">Good evening</h1>

      {(trending.isLoading || trending.data?.results.length) ? (
        <SectionRow
          title="Global Top 50"
          songs={trending.data?.results.map(externalTrackToSong)}
          isLoading={trending.isLoading}
          error={trending.error}
          onPlay={playTrendingSong}
        />
      ) : null}

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
