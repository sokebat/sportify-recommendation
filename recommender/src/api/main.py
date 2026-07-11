"""
Run with (from the recommender/ project root):
    uvicorn src.api.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.external import router as external_router
from src.api.media import router as media_router
from src.api.router import health_router, router
from src.api.state import state

load_dotenv()  # SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET (see .env.example)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Don't crash if artifacts are missing. /external/* still works without
    # them, /recommend/* just returns 503 (see require_catalog).
    try:
        state.load()
    except FileNotFoundError as error:
        print(f"WARNING: {error}")
        print(
            "WARNING: starting WITHOUT the catalog - /recommend/* and /cover "
            "return 503/404 until the artifacts exist; /external/* still works.",
        )
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

# Frontend runs on :3000, API on :8000 - different origins, so we need
# CORS for local dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(media_router)
app.include_router(external_router)
app.include_router(router)
