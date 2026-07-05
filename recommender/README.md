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
├── configs/              # YAML config files
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
| `GET  /cover/{track_id}`        | Spotify oEmbed (proxied)        | album art               |
| `POST /recommend/similar-song`  | Cosine similarity (`05`)        | "songs like this one", gated to the seed's genre |
| `POST /recommend/playlist`      | Popularity-weighted KNN (`06`)  | fits a whole playlist  |
| `POST /recommend/mood`          | Weighted mood centroid (`07`)   | happy / angry / sad / calm |
| `POST /recommend/genre`         | TF-IDF genre match (`08`)       | browse by genre        |
| `POST /recommend/discover`      | Hybrid audio+categorical+text KNN (`09`) | "songs like this one", *not* genre-gated - higher diversity/novelty, lower genre precision |
| `POST /recommend/popularity`    | plain catalog lookup            | most popular overall/by genre |
| `POST /recommend/artist`        | plain catalog lookup            | top tracks by artist   |
| `POST /recommend/search-songs`  | plain catalog lookup            | autocomplete / search  |

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
