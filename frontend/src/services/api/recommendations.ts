import { post } from './client'
import type { RecommendationsResponse } from '@/types/song'

interface RequestOptions {
  signal?: AbortSignal
}

export function getSimilarSongs(
  { songName, artist, n = 10 }: { songName: string; artist?: string; n?: number },
  options?: RequestOptions,
) {
  return post<RecommendationsResponse>('/recommend/similar-song', { song_name: songName, artist, n }, options)
}

export function getPlaylistRecommendations(
  { songs, n = 10 }: { songs: string[]; n?: number },
  options?: RequestOptions,
) {
  return post<RecommendationsResponse>('/recommend/playlist', { songs, n }, options)
}

export function getMoodRecommendations({ mood, n = 10 }: { mood: string; n?: number }, options?: RequestOptions) {
  return post<RecommendationsResponse>('/recommend/mood', { mood, n }, options)
}

export function getGenreRecommendations({ genre, n = 10 }: { genre: string; n?: number }, options?: RequestOptions) {
  return post<RecommendationsResponse>('/recommend/genre', { genre, n }, options)
}

export function getPopularityRecommendations(
  { genre, n = 10 }: { genre?: string; n?: number } = {},
  options?: RequestOptions,
) {
  return post<RecommendationsResponse>('/recommend/popularity', { genre, n }, options)
}

export function getArtistRecommendations(
  { artist, n = 10 }: { artist: string; n?: number },
  options?: RequestOptions,
) {
  return post<RecommendationsResponse>('/recommend/artist', { artist, n }, options)
}

export function searchSongs({ query, n = 10 }: { query: string; n?: number }, options?: RequestOptions) {
  return post<RecommendationsResponse>('/recommend/search-songs', { query, n }, options)
}
