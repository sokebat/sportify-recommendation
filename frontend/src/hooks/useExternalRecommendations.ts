'use client'

import { useQuery } from '@tanstack/react-query'
import { recommendFromExternal } from '@/services/api/spotify'

/** Model recommendations seeded by an external (Spotify) track - the backend
 * bridges it into the catalog by Spotify ID/name -> artist -> genre. */
export function useExternalRecommendations({
  artist,
  track,
  spotifyId,
  genre,
  n = 10,
  enabled = true,
}: {
  artist: string
  track: string
  spotifyId?: string
  genre?: string
  n?: number
  enabled?: boolean
}) {
  return useQuery({
    queryKey: ['from-external', artist, track, spotifyId, genre, n],
    queryFn: ({ signal }) => recommendFromExternal({ artist, track, spotifyId, genre, n }, { signal }),
    enabled: enabled && !!artist && !!track,
    retry: false,
  })
}
