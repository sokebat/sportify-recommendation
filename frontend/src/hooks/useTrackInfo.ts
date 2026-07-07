'use client'

import { useQuery } from '@tanstack/react-query'
import { getTrackInfo } from '@/services/api/spotify'

/** Per-track metadata (artwork, Spotify link) via Search, for tracks not
 * already carrying it. 404 means the track is unknown there - don't retry,
 * callers just render less. */
export function useTrackInfo({ artist, track, enabled = true }: { artist: string; track: string; enabled?: boolean }) {
  return useQuery({
    queryKey: ['track-info', artist, track],
    queryFn: ({ signal }) => getTrackInfo({ artist, track }, { signal }),
    enabled: enabled && !!artist && !!track,
    staleTime: 24 * 60 * 60 * 1000,
    retry: false,
  })
}
