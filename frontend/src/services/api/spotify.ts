import { get, post } from './client'
import type {
  ArtistDetail,
  ExternalRecommendationsResponse,
  ExternalTracksResponse,
  TrackInfo,
} from '@/types/spotify'

interface RequestOptions {
  signal?: AbortSignal
}

export function getTrending({ limit = 20 }: { limit?: number } = {}, options?: RequestOptions) {
  return get<ExternalTracksResponse>(`/external/trending?limit=${limit}`, options)
}

export function getArtistDetail(name: string, options?: RequestOptions) {
  return get<ArtistDetail>(`/external/artist/${encodeURIComponent(name)}`, options)
}

export function getTrackInfo({ artist, track }: { artist: string; track: string }, options?: RequestOptions) {
  return get<TrackInfo>(
    `/external/track?artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(track)}`,
    options,
  )
}

export function recommendFromExternal(
  { artist, track, spotifyId, genre, n = 10 }: {
    artist: string
    track: string
    spotifyId?: string
    genre?: string
    n?: number
  },
  options?: RequestOptions,
) {
  return post<ExternalRecommendationsResponse>(
    '/recommend/from-external',
    { artist, track, spotify_id: spotifyId, genre, n },
    options,
  )
}
