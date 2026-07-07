"""Request/response models for the recommendation API - the response shapes
match the frontend's Song type 1:1 (sportify-recommendation/frontend/src/types/song.ts).
External* models mirror frontend/src/types/spotify.ts the same way."""
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
    """A track sourced live from Spotify rather than the local catalog.
    `in_catalog`/`catalog_track_id` say whether it bridged to a catalog row
    (and can therefore seed the recommendation models directly). `spotify_id`
    is the real Spotify track ID, which - since the local catalog's own
    track_id values are real Spotify IDs too - lets the bridge match exactly
    instead of by fuzzy name matching."""
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
    """Spotify's API has no artist biography text, so the hero is built from
    what it does provide: genres, follower count and a popularity score."""
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
    spotify_id: str | None = None  # exact catalog match when present - see resolve_external_track
    genre: str | None = None  # optional hint (e.g. from a trending payload); saves an API call
    n: int = Field(10, ge=1, le=50)


class ExternalRecommendationsResponse(RecommendationsResponse):
    """`results` stays shape-identical to RecommendationsResponse so the
    frontend reuses its components; `matched_by`/`seed` say how the external
    track was bridged into the catalog so the UI can title the row honestly."""
    matched_by: Literal["track", "artist", "genre"]
    seed: Song | None = None
