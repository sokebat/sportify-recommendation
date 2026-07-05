'use client'

import { useQuery } from '@tanstack/react-query'
import { getPopularityRecommendations } from '@/services/api/recommendations'

export function usePopularityRecommendations({ genre, n = 10 }: { genre?: string; n?: number } = {}) {
  return useQuery({
    queryKey: ['popularity', genre ?? null, n],
    queryFn: ({ signal }) => getPopularityRecommendations({ genre, n }, { signal }),
  })
}
