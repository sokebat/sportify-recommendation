import type { RecommendationsResponse, Song } from './song'

/** Mirrors the backend's External* Pydantic schemas 1:1
 * (recommender/src/api/schemas.py) - live data proxied from the Spotify Web API. */

export interface ExternalTrack {
  spotify_id?: string | null
  artist: string
  track: string
  album?: string | null
  thumb_url?: string | null
  spotify_url?: string | null
  chart_place?: number | null
  in_catalog: boolean
  catalog_track_id?: string | null
}

export interface ExternalTracksResponse {
  results: ExternalTrack[]
}

export interface ArtistDetail {
  name: string
  /** Spotify has no artist biography field - genres/followers/popularity
   * stand in for it on the artist page hero. */
  genres: string[]
  followers?: number | null
  popularity?: number | null
  thumb_url?: string | null
  spotify_url?: string | null
  top_tracks: ExternalTrack[]
}

export interface TrackInfo {
  artist: string
  track: string
  album?: string | null
  thumb_url?: string | null
  spotify_url?: string | null
}

export interface ExternalRecommendationsResponse extends RecommendationsResponse {
  /** How the external track was bridged into the catalog - lets the UI
   * title the row honestly ("similar to X" vs "because you like Y"). */
  matched_by: 'track' | 'artist' | 'genre'
  seed?: Song | null
}

/** Adapts an external track to the Song shape so it flows through the
 * existing SongCard/SectionRow/player components unchanged. */
export function externalTrackToSong(track: ExternalTrack): Song {
  return {
    track_id: track.catalog_track_id ?? undefined,
    track_name: track.track,
    artists: track.artist,
    album_name: track.album ?? undefined,
    track_genre: '',
    cover_url: track.thumb_url,
    spotify_url: track.spotify_url,
    spotify_id: track.spotify_id,
  }
}
