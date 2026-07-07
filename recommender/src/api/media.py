"""
Album cover art, resolved via Spotify's public oEmbed endpoint. This is
deliberately NOT the authenticated Web API (spotify.py) - that surface can be
gated behind "active premium subscription required for the owner of the app"
for a given developer account, while oEmbed needs no client credentials at
all and works for any public Spotify track. The catalog's own track_id
values are real Spotify track IDs, so this is an exact lookup. The frontend
just does <img src="/cover/{track_id}"> and handles the 404 fallback itself
(SongCard's gradient placeholder).
"""
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["media"])

OEMBED_URL = "https://open.spotify.com/oembed"
REQUEST_TIMEOUT = 5.0

# In-memory cache: track_id -> cover image URL, or None if we've confirmed
# there isn't one (avoids re-hitting the API for the same track repeatedly).
_cover_cache: dict[str, str | None] = {}

_transport: httpx.AsyncBaseTransport | None = None  # tests swap in httpx.MockTransport


@router.get("/cover/{track_id}")
async def cover(track_id: str):
    if track_id in _cover_cache:
        cached_url = _cover_cache[track_id]
        if cached_url is None:
            raise HTTPException(status_code=404, detail="no cover art available")
        return RedirectResponse(cached_url)

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, transport=_transport) as client:
            response = await client.get(OEMBED_URL, params={"url": f"spotify:track:{track_id}"})
        response.raise_for_status()
        thumbnail_url = response.json().get("thumbnail_url")
    except Exception:
        thumbnail_url = None

    if not thumbnail_url:
        _cover_cache[track_id] = None
        raise HTTPException(status_code=404, detail="no cover art available")

    _cover_cache[track_id] = thumbnail_url
    return RedirectResponse(thumbnail_url)
