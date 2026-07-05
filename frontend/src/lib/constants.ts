export const navItems = [
  { href: '/', label: 'Home', icon: '🏠' },
  { href: '/mood', label: 'Mood', icon: '🎭' },
  { href: '/genre', label: 'Genres', icon: '🎸' },
  { href: '/playlist', label: 'Build Playlist', icon: '📋' },
  { href: '/artist', label: 'Artist', icon: '🎤' },
] as const

export const moodTiles = [
  { id: 'happy', label: 'Happy', color: 'from-yellow-500 to-yellow-700' },
  { id: 'angry', label: 'Angry', color: 'from-red-600 to-red-800' },
  { id: 'sad', label: 'Sad', color: 'from-blue-600 to-blue-900' },
  { id: 'calm', label: 'Calm', color: 'from-green-600 to-green-800' },
] as const

export const genreTiles = [
  { id: 'pop', label: 'Pop', color: '#8C1932' },
  { id: 'rock', label: 'Rock', color: '#E8115B' },
  { id: 'hip-hop', label: 'Hip-Hop', color: '#BC5900' },
  { id: 'jazz', label: 'Jazz', color: '#8D67AB' },
  { id: 'classical', label: 'Classical', color: '#1E3264' },
  { id: 'edm', label: 'EDM', color: '#148A08' },
  { id: 'country', label: 'Country', color: '#E1118C' },
  { id: 'k-pop', label: 'K-Pop', color: '#777777' },
] as const

export const onboardingGenres = [
  'Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Classical',
  'EDM', 'Country', 'K-Pop', 'R&B', 'Metal',
  'Folk', 'Indie', 'Latin', 'Reggae', 'Blues',
] as const

export const onboardingMoods = [
  { id: 'happy', label: 'Happy', emoji: '😊' },
  { id: 'angry', label: 'Angry', emoji: '😤' },
  { id: 'sad', label: 'Sad', emoji: '😢' },
  { id: 'calm', label: 'Calm', emoji: '😌' },
] as const

// A handful of onboarding genre labels don't match the catalog's own genre
// spelling 1:1 (e.g. the dataset uses "r-n-b", not "r&b") - everything else
// just needs lowercasing.
const genreLabelOverrides: Record<string, string> = {
  'R&B': 'r-n-b',
}

export function toGenreApiId(label: string): string {
  return genreLabelOverrides[label] ?? label.toLowerCase()
}
