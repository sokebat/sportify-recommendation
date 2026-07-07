"""
Spotify Web API client: trending charts, artist info and track lookups that
dress the catalog-backed recommendations up with live, real-world data. Auth
is the Client Credentials Flow (app-only, no user login) - requires
SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET from a Spotify Developer Dashboard app.

As of the February 2026 Developer Mode restrictions, a freshly created app
can no longer use: batch track/artist lookups, Get Artist's Top Tracks, Get
New Releases, or Get Several Browse Categories. What's still available and
used here: single Get Track, single Get Artist, Get Playlist/Playlist Items,
and Search (capped at limit<=10). See external.py for how these substitute
for the removed endpoints (e.g. Search stands in for Artist's Top Tracks).

Every fetcher degrades to None/[] on any failure - missing credentials,
timeouts, HTTP errors, empty search results - so callers render less instead
of breaking. An in-process TTL cache avoids re-fetching unchanged data; the
bearer token is cached and refreshed before it expires.
"""
import base64
import os
import time
from typing import Any

import httpx

ACCOUNTS_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"

# Spotify's own editorial "Top 50 - Global" playlist - a real, currently
# accurate chart, and a great substitute for the no-longer-available
# Recommendations/New Releases endpoints for a "trending" feature.
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
    """Spotify returns an `images` array of {url, width, height} - pick
    whichever is closest to `target_width` rather than assuming an order."""
    if not images:
        return None
    sized = [img for img in images if img.get("width")]
    if not sized:
        return images[0].get("url")
    closest = min(sized, key=lambda img: abs(img["width"] - target_width))
    return closest.get("url")


async def _get_token() -> str | None:
    """Cached bearer token via the Client Credentials Flow. Returns None
    (rather than raising) when credentials are missing or the auth call
    fails, so callers degrade gracefully instead of crashing the request."""
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
    """Cached, authenticated GET against the Web API. A stale cache entry
    beats returning nothing when the token or request fails."""
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
    """Track objects from Spotify's own "Top 50 - Global" playlist, each
    already carrying album art and popularity - no per-track lookup needed."""
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
    """Search substitutes for the removed Get Artist's Top Tracks endpoint -
    tracks by this artist, ranked by Spotify's own popularity score."""
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
    """Exact-ID track lookup - used for cover art, since the local catalog's
    track_id values are themselves real Spotify IDs."""
    return await _get_json(f"/tracks/{track_id}", None, LOOKUP_TTL)
