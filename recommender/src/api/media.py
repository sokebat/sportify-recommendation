"""
Gets cover art from Spotify's public oEmbed endpoint instead of the
authenticated Web API (spotify.py), since that can 403 with "premium
required" for the dev app owner. oEmbed doesn't need credentials. Catalog
track_ids are real Spotify IDs, so this is a direct lookup.
"""
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["media"])

OEMBED_URL = "https://open.spotify.com/oembed"
REQUEST_TIMEOUT = 5.0

# Caches track_id -> cover URL (or None if we already know there's no
# cover), so we don't hit the API again for the same track.
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
