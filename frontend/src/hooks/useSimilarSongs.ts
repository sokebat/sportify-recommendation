'use client'

import { useQuery } from '@tanstack/react-query'
import { getSimilarSongs } from '@/services/api/recommendations'

export function useSimilarSongs({ songName, artist, n = 10 }: { songName: string; artist?: string; n?: number }) {
  return useQuery({
    queryKey: ['similar-song', songName, artist, n],
    queryFn: ({ signal }) => getSimilarSongs({ songName, artist, n }, { signal }),
    enabled: !!songName,
  })
}
