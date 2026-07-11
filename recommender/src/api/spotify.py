"""
Spotify Web API client. Needs SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET, auth
is Client Credentials Flow.

New Spotify apps (since Feb 2026) can't use batch lookups, Get Artist's Top
Tracks, Get New Releases, or Get Several Browse Categories anymore. Only
single Get Track/Artist, Get Playlist Items, and Search (limit<=10) still
work - see external.py for how we work around that.

If a call fails, functions here just return None/[] instead of raising.
Responses and the auth token get cached for a while.
"""
import base64
import os
import time
from typing import Any

import httpx

ACCOUNTS_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"

# Spotify's "Top 50 - Global" playlist. We use this since the
# Recommendations/New Releases endpoints got removed.
TRENDING_PLAYLIST_ID = "37i9dQZEVXbMDoHDwVN2tF"

TRENDING_TTL = 60 * 60  # charts refresh slowly; 1h keeps calls low
LOOKUP_TTL = 24 * 60 * 60  # artist/track metadata is effectively static
REQUEST_TIMEOUT = 5.0
TOKEN_REFRESH_MARGIN = 60  # refresh this many seconds before actual expiry

_cache: dict[str, tuple[float, Any]] = {}  # cache key -> (expires_at, payload)
_token: dict[str, Any] = {}  # {"access_token": str, "expires_at": float} or {}
_transport: httpx.AsyncBaseTransport | None = None  # tests swap in httpx.MockTransport


def _client_id() -> str | None:
    return os.getenv("SPOTIFY_CLIENT_ID")


def _client_secret() -> str | None:
    return os.getenv("SPOTIFY_CLIENT_SECRET")


def image_url(images: list[dict] | None, target_width: int = 300) -> str | None:
    """Spotify gives an `images` list of {url, width, height} in no fixed
    order, so we just pick whichever is closest to `target_width`."""
    if not images:
        return None
    sized = [img for img in images if img.get("width")]
    if not sized:
        return images[0].get("url")
    closest = min(sized, key=lambda img: abs(img["width"] - target_width))
    return closest.get("url")


async def _get_token() -> str | None:
    """Gets a cached bearer token. Returns None instead of raising if
    credentials are missing or the auth call fails."""
    if _token and time.monotonic() < _token["expires_at"]:
        return _token["access_token"]

    client_id, client_secret = _client_id(), _client_secret()
    if not client_id or not client_secret:
        return None

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, transport=_transport) as client:
            response = await client.post(
                ACCOUNTS_URL,
                headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": "client_credentials"},
            )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    _token["access_token"] = payload["access_token"]
    _token["expires_at"] = time.monotonic() + payload["expires_in"] - TOKEN_REFRESH_MARGIN
    return _token["access_token"]


async def _get_json(endpoint: str, params: dict[str, str] | None, ttl: float) -> Any | None:
    """Authenticated GET with caching. If the token or request fails, we
    return the stale cached value instead of nothing."""
    params = params or {}
    key = endpoint + "?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    cached = _cache.get(key)
    if cached and time.monotonic() < cached[0]:
        return cached[1]

    token = await _get_token()
    if token is None:
        return cached[1] if cached else None

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, transport=_transport) as client:
            response = await client.get(
                f"{API_BASE_URL}{endpoint}", params=params, headers={"Authorization": f"Bearer {token}"},
            )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return cached[1] if cached else None

    _cache[key] = (time.monotonic() + ttl, payload)
    return payload


async def fetch_trending_tracks(limit: int = 20) -> list[dict]:
    """Gets tracks from Spotify's "Top 50 - Global" playlist - already has
    album art and popularity, so no extra lookup needed."""
    payload = await _get_json(
        f"/playlists/{TRENDING_PLAYLIST_ID}/items",
        {"limit": str(limit), "market": "US", "fields": "items(track(id,name,popularity,artists,album,external_urls))"},
        TRENDING_TTL,
    )
    if not isinstance(payload, dict):
        return []
    items = payload.get("items") or []
    # Local files / unavailable items surface as a null "track".
    return [item["track"] for item in items if item.get("track")]


async def fetch_artist_by_name(name: str) -> dict | None:
    """Best artist match by name (genres, images, followers, popularity)."""
    payload = await _get_json("/search", {"q": name, "type": "artist", "limit": "1"}, LOOKUP_TTL)
    if not isinstance(payload, dict):
        return None
    items = (payload.get("artists") or {}).get("items") or []
    return items[0] if items else None


async def fetch_popular_tracks_by_artist(name: str, limit: int = 10) -> list[dict]:
    """Get Artist's Top Tracks got removed, so we search instead and sort
    the results by popularity ourselves."""
    payload = await _get_json(
        "/search", {"q": f'artist:"{name}"', "type": "track", "limit": str(min(limit, 10))}, LOOKUP_TTL,
    )
    if not isinstance(payload, dict):
        return []
    items = (payload.get("tracks") or {}).get("items") or []
    return sorted(items, key=lambda track: track.get("popularity", 0), reverse=True)


async def fetch_track_by_name(artist: str, track: str) -> dict | None:
    """Best track match by artist + title."""
    payload = await _get_json(
        "/search", {"q": f'track:"{track}" artist:"{artist}"', "type": "track", "limit": "1"}, LOOKUP_TTL,
    )
    if not isinstance(payload, dict):
        return None
    items = (payload.get("tracks") or {}).get("items") or []
    return items[0] if items else None


async def fetch_track_by_id(track_id: str) -> dict | None:
    """Looks up a track by its exact Spotify ID. Used for cover art since
    catalog track_ids are real Spotify IDs."""
    return await _get_json(f"/tracks/{track_id}", None, LOOKUP_TTL)
