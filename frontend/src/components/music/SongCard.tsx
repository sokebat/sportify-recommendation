import { TrackCoverImage } from './TrackCoverImage'
import type { Song } from '@/types/song'

export function SongCard({ song, onPlay }: { song: Song; onPlay?: (song: Song) => void }) {
  return (
    <div
      onClick={() => onPlay?.(song)}
      className="bg-spotify-elevated hover:bg-spotify-hover rounded-md p-3 transition-colors duration-200 cursor-pointer group flex flex-col gap-3"
    >
      <div className="relative aspect-square w-full rounded overflow-hidden">
        <TrackCoverImage trackId={song.track_id} className="absolute inset-0 h-full w-full" />
        <button
          className="absolute bottom-2 right-2 w-10 h-10 rounded-full bg-spotify-green flex items-center justify-center opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-200 shadow-lg"
        >
          <svg viewBox="0 0 24 24" fill="black" className="w-5 h-5 ml-0.5">
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>
      </div>

      <div className="min-w-0">
        <p className="text-white text-sm font-semibold truncate">{song.track_name}</p>
        <p className="text-spotify-text-secondary text-xs truncate mt-1">{song.artists}</p>
      </div>
    </div>
  )
}
