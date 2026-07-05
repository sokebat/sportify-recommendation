export interface Song {
  track_id?: string
  track_name: string
  artists: string
  album_name?: string
  track_genre: string
  popularity?: number
}

export interface RecommendationsResponse {
  results: Song[]
}
