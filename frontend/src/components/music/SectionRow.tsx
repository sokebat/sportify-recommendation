import type { Song } from '@/types/song'
import { SongCard } from './SongCard'

interface SectionRowProps {
  title: string
  songs?: Song[]
  isLoading?: boolean
  error?: Error | null
  onPlay?: (song: Song) => void
}

export function SectionRow({ title, songs, isLoading, error, onPlay }: SectionRowProps) {
  if (error) return null // fail silently per row, don't break whole page

  return (
    <section className="mb-8">
      <h2 className="text-white text-xl font-bold mb-4">{title}</h2>

      {isLoading ? (
        <div className="flex gap-4 overflow-x-auto">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="w-44 h-60 bg-spotify-elevated rounded-md animate-pulse shrink-0" />
          ))}
        </div>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {songs?.map((song, i) => (
            <div key={song.track_id ?? i} className="w-44 shrink-0">
              <SongCard song={song} onPlay={onPlay} />
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
