'use client'

import { useQuery } from '@tanstack/react-query'
import { searchSongs } from '@/services/api/recommendations'

/** Live song search, e.g. for autocomplete. Enabled once the query is at least 2 characters. */
export function useSongSearch({ query, n = 8 }: { query: string; n?: number }) {
  return useQuery({
    queryKey: ['search-songs', query, n],
    queryFn: ({ signal }) => searchSongs({ query, n }, { signal }),
    enabled: query.trim().length >= 2,
  })
}
