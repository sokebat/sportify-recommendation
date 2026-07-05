# Sportify Frontend

A Spotify UI clone built with Next.js (App Router), React 19, TypeScript,
Tailwind v4, and TanStack Query. All recommendation data comes from the
FastAPI backend in [`../recommender`](../recommender) - see the
[top-level README](../README.md) for running both together.

## Setup

```bash
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL, defaults to http://127.0.0.1:8000
npm run dev                  # http://localhost:3000
```

Other scripts: `npm run build`, `npm run start` (serve the production
build), `npm run lint`.

## Pages

| Route | What it does |
| --- | --- |
| `/` | Popular / mood / genre rows, all fetched live |
| `/search?q=&artist=` | Free-text song search with a "similar songs" row |
| `/mood` | Pick happy / angry / sad / calm, see matching tracks |
| `/genre` | Browse by genre tile |
| `/playlist` | Add several songs, get recommendations that fit all of them |
| `/artist` | Top tracks by an artist |
| `/login`, `/signup` | Fake auth, no real backend - accounts + session live in `localStorage` (see `AuthContext`); login leads into `/onboarding`, signup goes straight home |
| `/onboarding` | Pick genres + moods, then see real recommendations for them before finishing |

## Project structure

```text
src/
├── app/
│   ├── (app)/          # Routes behind the sidebar/top bar/now-playing shell
│   ├── (auth)/          # Login, signup, onboarding - no shell
│   ├── layout.tsx        # Root layout: fonts, metadata, <Providers>
│   └── providers.tsx     # TanStack Query client
├── components/
│   ├── layout/           # AppShell, Sidebar, TopBar, NowPlayingBar
│   ├── music/             # SongCard, SectionRow, SongAutocomplete, TrackCoverImage, VinylSpinner
│   └── ui/                 # Button, Card
├── context/               # PlayerContext (current song / play-pause state)
├── hooks/                  # One hook per recommendation type, wrapping useQuery
├── services/api/            # fetch client, typed ApiError, per-endpoint functions, cover-art URLs
├── lib/                      # constants (nav items, genre/mood tiles), cn() classname helper
└── types/                     # Song / RecommendationsResponse types
```

**Data flow:** a page calls a hook (e.g. `useMoodRecommendations`) → the hook
wraps `@tanstack/react-query`'s `useQuery` around a function in
`services/api/recommendations.ts` → that function POSTs to the backend and
returns `{ results: Song[] }`. Errors surface as a typed `ApiError` (`status`
+ `detail`, matching the backend's `{"detail": "..."}` shape); in-flight
requests are cancelled via React Query's `AbortSignal` when a query goes
stale (e.g. fast typing in the search autocomplete).

## Design system

Spotify's own dark palette, defined once as Tailwind v4 theme tokens in
`src/app/globals.css`: `spotify-black`, `spotify-elevated`, `spotify-hover`,
`spotify-green` (+ `-hover`), `spotify-text-secondary`, `spotify-border`.
Album art comes from the backend's `/cover/{track_id}` redirect; a missing
or failed image falls back to a gradient placeholder (`TrackCoverImage`).
