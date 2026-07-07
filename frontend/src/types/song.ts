export interface Song {
  track_id?: string
  track_name: string
  artists: string
  album_name?: string
  track_genre: string
  popularity?: number
  /** Direct artwork URL for externally sourced tracks (Spotify CDN);
   * catalog tracks resolve art through /cover/{track_id} instead. */
  cover_url?: string | null
  /** Link to the track on open.spotify.com. For catalog tracks this is
   * derivable from track_id alone (see NowPlayingBar); externally sourced
   * tracks carry it directly since they may not have a catalog track_id. */
  spotify_url?: string | null
  /** The real Spotify track ID for an externally sourced, not-yet-bridged
   * song (in_catalog=false, so track_id is unset) - lets the recommend-from
   * -external bridge match by exact ID instead of fuzzy name matching. */
  spotify_id?: string | null
}

export interface RecommendationsResponse {
  results: Song[]
}
