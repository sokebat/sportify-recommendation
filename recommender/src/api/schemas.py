"""Request/response models for the recommendation API - the response shapes
match the frontend's Song type 1:1 (sportify-recommendation/frontend/src/types/song.ts)."""
from pydantic import BaseModel, Field


class Song(BaseModel):
    track_id: str
    track_name: str
    artists: str
    album_name: str
    track_genre: str
    popularity: int


class RecommendationsResponse(BaseModel):
    results: list[Song]


class SimilarSongRequest(BaseModel):
    song_name: str
    artist: str | None = None
    n: int = Field(10, ge=1, le=50)


class PlaylistRequest(BaseModel):
    songs: list[str]
    n: int = Field(10, ge=1, le=50)


class MoodRequest(BaseModel):
    mood: str
    n: int = Field(10, ge=1, le=50)


class GenreRequest(BaseModel):
    genre: str
    n: int = Field(10, ge=1, le=50)


class PopularityRequest(BaseModel):
    genre: str | None = None
    n: int = Field(10, ge=1, le=50)


class ArtistRequest(BaseModel):
    artist: str
    n: int = Field(10, ge=1, le=50)


class SearchRequest(BaseModel):
    query: str
    n: int = Field(10, ge=1, le=50)


class HealthResponse(BaseModel):
    status: str
    n_songs: int | None = None
    n_genres: int | None = None
