import pandas as pd
from fastapi import APIRouter, HTTPException

from src.api.schemas import (
    ArtistRequest,
    GenreRequest,
    HealthResponse,
    MoodRequest,
    PlaylistRequest,
    PopularityRequest,
    RecommendationsResponse,
    SearchRequest,
    SimilarSongRequest,
    Song,
)
from src.api.state import state
from src.recommendation.catalog import popular_songs, search_songs, songs_by_artist
from src.recommendation.discover import recommend_discover
from src.recommendation.genre import recommend_by_genre
from src.recommendation.mood import recommend_by_mood
from src.recommendation.playlist import recommend_for_playlist
from src.recommendation.similar_song import recommend_similar_songs

router = APIRouter(prefix="/recommend", tags=["recommendations"])


def _to_response(df: pd.DataFrame) -> RecommendationsResponse:
    return RecommendationsResponse(results=[Song(**row) for row in df.to_dict(orient="records")])


@router.post("/similar-song")
def similar_song(payload: SimilarSongRequest) -> RecommendationsResponse:
    recs = recommend_similar_songs(
        state.tracks, state.sound_matrix, payload.song_name, payload.artist, top_n=payload.n,
    )
    if recs is None:
        raise HTTPException(status_code=404, detail=f"Song not found: {payload.song_name!r}")
    return _to_response(recs)


@router.post("/playlist")
def playlist(payload: PlaylistRequest) -> RecommendationsResponse:
    recs = recommend_for_playlist(
        state.tracks, state.sound_matrix, payload.songs, top_n=payload.n, metric=state.knn_metric,
    )
    return _to_response(recs)


@router.post("/mood")
def mood(payload: MoodRequest) -> RecommendationsResponse:
    recs = recommend_by_mood(state.tracks, state.mood_matrix, payload.mood, top_n=payload.n)
    return _to_response(recs)


@router.post("/genre")
def genre(payload: GenreRequest) -> RecommendationsResponse:
    recs = recommend_by_genre(state.tracks, state.genre_matrix, state.genre_vectorizer, payload.genre, top_n=payload.n)
    return _to_response(recs)


@router.post("/popularity")
def popularity(payload: PopularityRequest) -> RecommendationsResponse:
    recs = popular_songs(state.tracks, genre=payload.genre, limit=payload.n)
    return _to_response(recs)


@router.post("/artist")
def artist(payload: ArtistRequest) -> RecommendationsResponse:
    recs = songs_by_artist(state.tracks, payload.artist, limit=payload.n)
    return _to_response(recs)


@router.post("/search-songs")
def search(payload: SearchRequest) -> RecommendationsResponse:
    recs = search_songs(state.tracks, payload.query, limit=payload.n)
    return _to_response(recs)


@router.post("/discover")
def discover(payload: SimilarSongRequest) -> RecommendationsResponse:
    recs = recommend_discover(
        state.tracks, state.hybrid_model, state.hybrid_matrix, payload.song_name, payload.artist, top_n=payload.n,
    )
    if recs is None:
        raise HTTPException(status_code=404, detail=f"Song not found: {payload.song_name!r}")
    return _to_response(recs)


health_router = APIRouter(tags=["health"])


@health_router.get("/health")
def health() -> HealthResponse:
    if not state.loaded:
        return HealthResponse(status="not_loaded")
    return HealthResponse(
        status="ok",
        n_songs=int(len(state.tracks)),
        n_genres=int(state.tracks["track_genre"].nunique()),
    )
