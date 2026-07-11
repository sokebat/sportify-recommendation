import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from src.api.schemas import (
    ArtistRequest,
    ExternalRecommendationsResponse,
    ExternalRecommendRequest,
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
from src.api.spotify import fetch_artist_by_name
from src.api.state import state
from src.recommendation.catalog import (
    RESULT_COLUMNS,
    normalize_artist,
    popular_songs,
    resolve_external_track,
    search_songs,
    songs_by_artist,
)
from src.recommendation.discover import recommend_discover
from src.recommendation.genre import recommend_by_genre
from src.recommendation.mood import recommend_by_mood
from src.recommendation.playlist import recommend_for_playlist
from src.recommendation.similar_song import recommend_similar_songs

def require_catalog() -> None:
    """Returns 503 if the model files aren't loaded yet, instead of crashing."""
    if not state.loaded:
        raise HTTPException(
            status_code=503,
            detail=(
                "Catalog not loaded - run notebooks/01-09 to build "
                "data/processed and models/content_based, then restart the API."
            ),
        )


router = APIRouter(prefix="/recommend", tags=["recommendations"], dependencies=[Depends(require_catalog)])

# Spotify uses genres like "dance pop" or "alt z" that don't match our
# catalog genres directly. Map the common ones here.
SPOTIFY_GENRE_ALIASES = {
    "r&b": "r-n-b",
    "rhythm and blues": "r-n-b",
    "hip hop": "hip-hop",
    "trap": "hip-hop",
    "dance pop": "pop",
    "pop rap": "hip-hop",
    "electronica": "electronic",
    "edm": "electronic",
    "singer-songwriter pop": "singer-songwriter",
}


def _to_response(df: pd.DataFrame) -> RecommendationsResponse:
    return RecommendationsResponse(results=[Song(**row) for row in df.to_dict(orient="records")])


def _to_songs(df: pd.DataFrame) -> list[Song]:
    return [Song(**row) for row in df.to_dict(orient="records")]


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


@router.post("/from-external")
async def from_external(payload: ExternalRecommendRequest) -> ExternalRecommendationsResponse:
    """Recommends songs from a Spotify track instead of a catalog one. Tries
    an exact match first, then the artist's top song, then just the genre."""
    index = resolve_external_track(state.tracks, payload.track, payload.artist, spotify_id=payload.spotify_id)
    if index is not None:
        seed = state.tracks.loc[[index], RESULT_COLUMNS].to_dict(orient="records")[0]
        recs = recommend_similar_songs(
            state.tracks, state.sound_matrix, seed["track_name"], seed["artists"], top_n=payload.n,
        )
        return ExternalRecommendationsResponse(
            results=_to_songs(recs), matched_by="track", seed=Song(**seed),
        )

    artist_songs = songs_by_artist(state.tracks, normalize_artist(payload.artist), limit=1)
    if not artist_songs.empty:
        seed = artist_songs.to_dict(orient="records")[0]
        recs = recommend_similar_songs(
            state.tracks, state.sound_matrix, seed["track_name"], seed["artists"], top_n=payload.n,
        )
        if recs is not None:
            return ExternalRecommendationsResponse(
                results=_to_songs(recs), matched_by="artist", seed=Song(**seed),
            )

    # Last resort: just recommend by genre. Trending tracks already have
    # one; otherwise ask Spotify for the artist's genres.
    genre = payload.genre
    if not genre:
        artist_info = await fetch_artist_by_name(payload.artist)
        genres = (artist_info or {}).get("genres") or []
        genre = genres[0] if genres else None
    if genre:
        genre = SPOTIFY_GENRE_ALIASES.get(genre.strip().lower(), genre)
        recs = recommend_by_genre(
            state.tracks, state.genre_matrix, state.genre_vectorizer, genre, top_n=payload.n,
        )
        if not recs.empty:
            return ExternalRecommendationsResponse(results=_to_songs(recs), matched_by="genre")

    raise HTTPException(
        status_code=404,
        detail=f"Could not match {payload.track!r} by {payload.artist!r} to the catalog",
    )


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
