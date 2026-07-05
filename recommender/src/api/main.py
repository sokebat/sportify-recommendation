"""

Run with (from the recommender/ project root):
    uvicorn src.api.main:app --reload --port 8000


(sportify-recommendation/frontend/src/services/api/):
    GET  /health
    GET  /cover/{track_id}
    POST /recommend/similar-song
    POST /recommend/playlist
    POST /recommend/mood
    POST /recommend/genre
    POST /recommend/popularity
    POST /recommend/artist
    POST /recommend/search-songs
    POST /recommend/discover
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.media import router as media_router
from src.api.router import health_router, router
from src.api.state import state


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.load()
    yield


app = FastAPI(
    title="Sportify Recommender API",
    description=(
        "Content-based song recommender over Spotify audio features - cosine "
        "similarity (similar song), popularity-weighted KNN (playlist), "
        "weighted mood centroids (mood), TF-IDF genre matching (genre), and a "
        "hybrid audio+categorical+text nearest-neighbor space for cross-genre "
        "discovery (discover)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Local dev only: the frontend (Next.js on :3000) and this API (:8000) run as
# separate origins, so the browser needs CORS to call across.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(media_router)
app.include_router(router)
