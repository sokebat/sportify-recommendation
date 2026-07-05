# Sportify Recommendation

A Spotify UI clone backed by a real content-based recommender: pick a song, a
mood, a genre, or an artist, and get back tracks actually chosen by trained
models running over ~90k Spotify tracks - not mocked data.

```
┌───────────────────────┐        HTTP        ┌──────────────────────────┐
│  frontend (Next.js)   │ ──────────────────▶ │  recommender (FastAPI)   │
│  Spotify-styled UI     │ ◀────────────────── │  content-based models    │
└───────────────────────┘                     └──────────────────────────┘
```

## Structure

| Folder | What it is |
| --- | --- |
| [`frontend/`](frontend/README.md) | Next.js 16 + React 19 + TypeScript + Tailwind v4 - the Spotify-styled UI |
| [`recommender/`](recommender/README.md) | Notebooks (data cleaning → features → 4 trained models) + a FastAPI service that serves them |

## Features

- **Home** - popular tracks, mood and genre rows, all real recommendations
- **Search** - free-text song search with live autocomplete
- **Similar song** - cosine similarity over audio features, genre-gated
- **Mood** - happy / angry / sad / calm, ranked by a weighted centroid + popularity
- **Genre** - TF-IDF text matching over genre/mood/tempo descriptors
- **Build a playlist** - add several songs, get a popularity-weighted KNN blend of what fits them all
- **Artist lookup**, **album art** (proxied from Spotify's public oEmbed), and a **login → onboarding** flow that shows real picks for the genre/mood you chose

## Running it locally

Two servers, both need to be up for the UI to show real data.

**1. Backend** (from `recommender/`):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
 uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 # http://127.0.0.1:8000
```

Needs the processed catalog + trained model artifacts to already exist -
see [`recommender/README.md`](recommender/README.md) for which notebooks
produce them.

**2. Frontend** (from `frontend/`):

```bash
npm install   # or pnpm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL, defaults to the URL above
npm run dev   # http://localhost:3000
```

Without the backend running, pages still render (loading skeletons →
each row just fails silently) - see [`frontend/README.md`](frontend/README.md)
for the full page/feature list and folder layout.
 