"""Request/response models for the API. Song matches the frontend's Song
type, External* models match frontend/src/types/spotify.ts."""
from typing import Literal

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


class ExternalTrack(BaseModel):
    """A track from Spotify, not our catalog. `in_catalog`/`catalog_track_id`
    say if it matched a catalog row and can seed the recommenders directly.
    `spotify_id` lets us match it exactly instead of guessing by name."""
    spotify_id: str | None = None
    artist: str
    track: str
    album: str | None = None
    thumb_url: str | None = None
    spotify_url: str | None = None
    chart_place: int | None = None
    in_catalog: bool = False
    catalog_track_id: str | None = None


class ExternalTracksResponse(BaseModel):
    results: list[ExternalTrack]


class ArtistDetailResponse(BaseModel):
    """Spotify has no artist bio field, so we build the artist page from
    genres, followers, and popularity instead."""
    name: str
    genres: list[str] = []
    followers: int | None = None
    popularity: int | None = None
    thumb_url: str | None = None
    spotify_url: str | None = None
    top_tracks: list[ExternalTrack] = []


class TrackInfoResponse(BaseModel):
    artist: str
    track: str
    album: str | None = None
    thumb_url: str | None = None
    spotify_url: str | None = None


class ExternalRecommendRequest(BaseModel):
    artist: str = Field(min_length=1)
    track: str = Field(min_length=1)
    spotify_id: str | None = None  # exact match if we have it, see resolve_external_track
    genre: str | None = None  # hint from the payload if we have one, saves an API call
    n: int = Field(10, ge=1, le=50)


class ExternalRecommendationsResponse(RecommendationsResponse):
    """Same `results` shape as RecommendationsResponse so the frontend can
    reuse its components. `matched_by`/`seed` say how we matched the
    external track to the catalog."""
    matched_by: Literal["track", "artist", "genre"]
    seed: Song | None = None
