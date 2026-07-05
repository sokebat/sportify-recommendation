'use client'

import { useQuery } from '@tanstack/react-query'
import { getArtistRecommendations } from '@/services/api/recommendations'

export function useArtistRecommendations({ artist, n = 10 }: { artist: string; n?: number }) {
  return useQuery({
    queryKey: ['artist', artist, n],
    queryFn: ({ signal }) => getArtistRecommendations({ artist, n }, { signal }),
    enabled: !!artist,
  })
}
