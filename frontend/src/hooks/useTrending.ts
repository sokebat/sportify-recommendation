'use client'

import { useQuery } from '@tanstack/react-query'
import { getTrending } from '@/services/api/spotify'

/** Spotify's own "Top 50 - Global" chart. staleTime matches the backend's
 * 1h cache; retry disabled because a failure usually means the upstream API
 * is down/rate-limited and the row just hides itself. */
export function useTrending({ limit = 12 }: { limit?: number } = {}) {
  return useQuery({
    queryKey: ['trending', limit],
    queryFn: ({ signal }) => getTrending({ limit }, { signal }),
    staleTime: 60 * 60 * 1000,
    retry: false,
  })
}
