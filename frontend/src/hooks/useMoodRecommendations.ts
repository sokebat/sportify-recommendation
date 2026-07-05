'use client'

import { useQuery } from '@tanstack/react-query'
import { getMoodRecommendations } from '@/services/api/recommendations'

export function useMoodRecommendations({ mood, n = 10 }: { mood: string | null; n?: number }) {
  return useQuery({
    queryKey: ['mood', mood, n],
    queryFn: ({ signal }) => getMoodRecommendations({ mood: mood as string, n }, { signal }),
    enabled: !!mood,
  })
}
