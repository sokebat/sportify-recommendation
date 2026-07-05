"""
Album cover art, resolved via Spotify's public oEmbed endpoint (no API key
required) since the catalog itself only has track_id/track_name/artists, not
artwork. The frontend just does <img src="/cover/{track_id}"> and handles the
404 fallback itself (SongCard's gradient placeholder).
"""
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["media"])

# In-memory cache: track_id -> cover image URL, or None if we've confirmed
# there isn't one (avoids re-hitting Spotify for the same track repeatedly).
_cover_cache: dict[str, str | None] = {}


@router.get("/cover/{track_id}")
async def cover(track_id: str):
    if track_id in _cover_cache:
        cached_url = _cover_cache[track_id]
        if cached_url is None:
            raise HTTPException(status_code=404, detail="no cover art available")
        return RedirectResponse(cached_url)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://open.spotify.com/oembed",
                params={"url": f"spotify:track:{track_id}"},
            )
        response.raise_for_status()
        thumbnail_url = response.json().get("thumbnail_url")
        if not thumbnail_url:
            raise ValueError("no thumbnail_url in oEmbed response")
    except Exception:
        _cover_cache[track_id] = None
        raise HTTPException(status_code=404, detail="no cover art available")

    _cover_cache[track_id] = thumbnail_url
    return RedirectResponse(thumbnail_url)
