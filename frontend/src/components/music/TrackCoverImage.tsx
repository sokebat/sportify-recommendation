'use client'

import { useState } from 'react'
import { cn } from '@/lib/cn'
import { getCoverUrl } from '@/services/api/covers'

/** Album art for a track: a direct URL when the caller already has one
 * (externally sourced tracks carry Spotify CDN art), otherwise resolved
 * through the backend's /cover/{track_id} redirect. Falls back to a plain
 * gradient tile - with no art, no track_id, or a broken image load -
 * instead of a dead <img>. */
export function TrackCoverImage({
  trackId,
  src,
  className,
}: {
  trackId?: string
  src?: string | null
  className?: string
}) {
  const [imageFailed, setImageFailed] = useState(false)
  const coverUrl = src ?? getCoverUrl(trackId)

  if (!coverUrl || imageFailed) {
    return (
      <div className={cn('bg-gradient-to-br from-zinc-700 to-zinc-900 flex items-center justify-center', className)}>
        <span className="text-zinc-500 text-xs">No Cover</span>
      </div>
    )
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element -- external, redirect-resolved cover art; not a static/known-domain asset next/image can optimize
    <img src={coverUrl} alt="" className={cn('object-cover', className)} onError={() => setImageFailed(true)} />
  )
}
