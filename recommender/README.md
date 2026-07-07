# Sportify Recommender

Content-based song recommender built from the Spotify tracks dataset:
notebooks handle data cleaning, EDA, feature engineering, and model
training/evaluation; `src/` serves the trained models over HTTP for the
Next.js frontend (`sportify-recommendation/frontend`).

## Project Structure

```text
recommender/
├── data/
│   ├── raw/              # Original untouched data
│   ├── interim/          # Temporary transformed data
│   ├── processed/        # Cleaned/engineered catalog (output of notebooks 01-04)
│   └── external/         # Third-party data
├── notebooks/            # The actual ML pipeline: cleaning, EDA, feature
│                          # engineering, and one notebook per model (05-09),
│                          # evaluated and compared in 10-11
├── src/
│   ├── recommendation/   # Content-based recommenders (ported from notebooks 05-09), pure logic
│   └── api/              # FastAPI web layer serving the recommenders
├── models/               # Saved model artifacts (output of notebooks 05-09)
├── reports/              # Evaluation metrics and comparison tables
├── tests/                # Unit tests for src/recommendation and src/api
├── logs/                 # Runtime logs
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── Makefile
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

## Run Tests

```bash
pytest
```

## Run the Recommendation API

Serves the content-based recommenders (trained via `notebooks/05`-`09`) over HTTP for
the Next.js frontend (`sportify-recommendation/frontend`):

```bash
  uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs at `http://127.0.0.1:8000/docs` once running. Endpoints:

| Endpoint                       | Model                          | Use case              |
| ------------------------------- | ------------------------------- | ---------------------- |
| `GET  /health`                  | -                                | liveness / catalog size |
| `GET  /cover/{track_id}`        | Spotify oEmbed (unauthenticated) | album art               |
| `POST /recommend/similar-song`  | Cosine similarity (`05`)        | "songs like this one", gated to the seed's genre |
| `POST /recommend/playlist`      | Popularity-weighted KNN (`06`)  | fits a whole playlist  |
| `POST /recommend/mood`          | Weighted mood centroid (`07`)   | happy / angry / sad / calm |
| `POST /recommend/genre`         | TF-IDF genre match (`08`)       | browse by genre        |
| `POST /recommend/discover`      | Hybrid audio+categorical+text KNN (`09`) | "songs like this one", *not* genre-gated - higher diversity/novelty, lower genre precision |
| `POST /recommend/popularity`    | plain catalog lookup            | most popular overall/by genre |
| `POST /recommend/artist`        | plain catalog lookup            | top tracks by artist   |
| `POST /recommend/search-songs`  | plain catalog lookup            | autocomplete / search  |
| `GET  /external/trending`       | Spotify (proxied + catalog-matched) | Global Top 50 chart |
| `GET  /external/artist/{name}`  | Spotify (proxied)               | artist genres/images/followers/popular tracks |
| `GET  /external/track`          | Spotify (proxied)               | track art / Spotify link |
| `POST /recommend/from-external` | bridge -> cosine or TF-IDF model | recommend from a live/external track (matched by Spotify ID/name -> artist -> genre) |

Live data comes from the [Spotify Web API](https://developer.spotify.com/documentation/web-api)
via the Client Credentials Flow (app-only, no user login) - create an app at the
[Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and set
`SPOTIFY_CLIENT_ID`/`SPOTIFY_CLIENT_SECRET` (see `.env.example`). All external
endpoints degrade gracefully (empty lists / 404s) when the API is unreachable, rate
limited, or credentials are missing.

Since February 2026, freshly created ("Development Mode") Spotify apps lose access to
batch track/artist lookups, Get Artist's Top Tracks, Get New Releases and Get Several
Browse Categories. This integration only relies on endpoints still available to a new
app: single Get Track, single Get Artist, Get Playlist/Playlist Items, and Search -
e.g. "trending" is Spotify's own editorial Top 50 - Global playlist, and "top tracks"
on the artist page is a Search-based popularity ranking rather than the (now
unavailable) official top-tracks endpoint. Spotify's API also has no artist biography
field, so the artist page shows genres/followers/popularity instead of a bio.

**Known gotcha:** if every `/external/*` call comes back empty/404 even though the
token endpoint succeeds, check for a `403: Active premium subscription required for
the owner of the app` on the underlying Web API calls (visible in server logs only if
you inspect the response manually - the endpoints degrade to empty/404 by design).
This is an account-level gate: the Spotify account that owns the Developer Dashboard
app must have an active Premium subscription, or every authenticated Web API data
endpoint is blocked regardless of app code. It's unrelated to the Client Credentials
Flow itself (the token issues fine) and isn't fixable from this codebase - either use
a Premium account's app credentials, or wait, since the app still runs and looks
correct with `/external/*` simply empty in the meantime.

Album art (`/cover/{track_id}`) is unaffected by this gate - it deliberately doesn't
use the authenticated Web API at all, instead calling Spotify's public oEmbed
endpoint (`open.spotify.com/oembed`), which needs no client credentials and works for
any public track regardless of the app account's subscription status.

Requires the processed catalog and model artifacts to exist first - run
`notebooks/01` through `09` to produce `data/processed/content_tracks_engineered.csv`
and `models/content_based/*`. Every notebook's artifact is loaded at startup
(see `src/recommendation/loader.py`) and `10`/`11` (evaluation + comparison)
are what justified each model's assigned endpoint above.

## Notes

- Keep raw data unchanged.
- All ML logic (cleaning, features, training, evaluation) lives in the
  notebooks - `src/` only serves already-trained artifacts, it doesn't
  retrain anything.
- Save trained models inside `models/`.
