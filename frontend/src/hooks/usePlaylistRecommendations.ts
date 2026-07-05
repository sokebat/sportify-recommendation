'use client'

import { useQuery } from '@tanstack/react-query'
import { getPlaylistRecommendations } from '@/services/api/recommendations'

export function usePlaylistRecommendations({
  songs,
  n = 10,
  enabled,
}: {
  songs: string[]
  n?: number
  enabled: boolean
}) {
  return useQuery({
    queryKey: ['playlist', songs, n],
    queryFn: ({ signal }) => getPlaylistRecommendations({ songs, n }, { signal }),
    enabled: enabled && songs.length > 0,
  })
}
