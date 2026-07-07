'use client'

import { useQuery } from '@tanstack/react-query'
import { getArtistDetail } from '@/services/api/spotify'

/** Artist genres/images/followers/popularity/top-tracks from Spotify. 404
 * just means the artist is unknown there - don't retry, the page renders
 * without the hero. */
export function useArtistDetail({ name }: { name: string }) {
  return useQuery({
    queryKey: ['artist-detail', name],
    queryFn: ({ signal }) => getArtistDetail(name, { signal }),
    enabled: !!name,
    staleTime: 24 * 60 * 60 * 1000,
    retry: false,
  })
}
