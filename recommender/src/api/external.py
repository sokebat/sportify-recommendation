"""
Live data endpoints backed by Spotify (see spotify.py). Each track gets
checked against the local catalog so we know if it can be used to seed the
recommendation models (/recommend/from-external).

If Spotify fails, we degrade instead of erroring - /trending just returns
an empty list, artist/track lookups 404 like a normal miss.
"""
from fastapi import APIRouter, HTTPException, Query

from src.api import spotify
from src.api.schemas import (
    ArtistDetailResponse,
    ExternalTrack,
    ExternalTracksResponse,
    TrackInfoResponse,
)
from src.api.state import state
from src.recommendation.catalog import resolve_external_track

router = APIRouter(prefix="/external", tags=["external"])


def _to_external_track(raw: dict, chart_place: int | None = None) -> ExternalTrack:
    artists = raw.get("artists") or []
    track = ExternalTrack(
        spotify_id=raw.get("id"),
        artist=artists[0]["name"] if artists else "",
        track=raw.get("name") or "",
        album=(raw.get("album") or {}).get("name"),
        thumb_url=spotify.image_url((raw.get("album") or {}).get("images")),
        spotify_url=(raw.get("external_urls") or {}).get("spotify"),
        chart_place=chart_place,
    )
    if state.loaded and track.track and track.artist:
        index = resolve_external_track(state.tracks, track.track, track.artist, spotify_id=track.spotify_id)
        if index is not None:
            track.in_catalog = True
            track.catalog_track_id = str(state.tracks.loc[index, "track_id"])
    return track


@router.get("/trending")
async def trending(limit: int = Query(20, ge=1, le=50)) -> ExternalTracksResponse:
    raw_tracks = await spotify.fetch_trending_tracks(limit=limit)
    results = [_to_external_track(raw, chart_place=i + 1) for i, raw in enumerate(raw_tracks[:limit])]
    return ExternalTracksResponse(results=[r for r in results if r.track and r.artist])


@router.get("/artist/{name}")
async def artist_detail(name: str) -> ArtistDetailResponse:
    raw = await spotify.fetch_artist_by_name(name)
    if raw is None:
        raise HTTPException(status_code=404, detail=f"Artist not found: {name!r}")

    top_tracks = await spotify.fetch_popular_tracks_by_artist(name)
    return ArtistDetailResponse(
        name=raw.get("name") or name,
        genres=raw.get("genres") or [],
        followers=(raw.get("followers") or {}).get("total"),
        popularity=raw.get("popularity"),
        thumb_url=spotify.image_url(raw.get("images")),
        spotify_url=(raw.get("external_urls") or {}).get("spotify"),
        top_tracks=[_to_external_track(item) for item in top_tracks],
    )


@router.get("/track")
async def track_info(artist: str = Query(...), track: str = Query(...)) -> TrackInfoResponse:
    raw = await spotify.fetch_track_by_name(artist, track)
    if raw is None:
        raise HTTPException(status_code=404, detail=f"Track not found: {track!r} by {artist!r}")
    artists = raw.get("artists") or []
    return TrackInfoResponse(
        artist=artists[0]["name"] if artists else artist,
        track=raw.get("name") or track,
        album=(raw.get("album") or {}).get("name"),
        thumb_url=spotify.image_url((raw.get("album") or {}).get("images")),
        spotify_url=(raw.get("external_urls") or {}).get("spotify"),
    )
