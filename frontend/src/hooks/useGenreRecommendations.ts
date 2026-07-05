'use client'

import { useQuery } from '@tanstack/react-query'
import { getGenreRecommendations } from '@/services/api/recommendations'

export function useGenreRecommendations({ genre, n = 10 }: { genre: string | null; n?: number }) {
  return useQuery({
    queryKey: ['genre', genre, n],
    queryFn: ({ signal }) => getGenreRecommendations({ genre: genre as string, n }, { signal }),
    enabled: !!genre,
  })
}
