import { API_BASE_URL } from './client'

/** URL for a track's album art, proxied through the backend's /cover/{track_id}
 * redirect. No fetch needed here - <img src> follows the redirect itself, and
 * a missing track_id or unavailable art just fails the <img> load, which
 * callers handle with onError. */
export function getCoverUrl(trackId: string | undefined): string | undefined {
  if (!trackId) return undefined
  return `${API_BASE_URL}/cover/${encodeURIComponent(trackId)}`
}
