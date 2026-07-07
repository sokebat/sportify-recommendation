"""
Cover art tests - fully offline: httpx transport is swapped for
httpx.MockTransport (media._transport test seam). Deliberately decoupled
from the Spotify Web API/catalog test infra (test_external_api.py) since
/cover uses the unauthenticated oEmbed endpoint and never touches either.
"""
import httpx
import pytest
from fastapi.testclient import TestClient

from src.api import media
from src.api.main import app

THUMB = "https://image-cdn-ak.spotifycdn.com/image/ab67616d00001e02abc"


@pytest.fixture(autouse=True)
def sandbox():
    media._cover_cache.clear()
    yield
    media._cover_cache.clear()
    media._transport = None


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def _install(handler) -> None:
    media._transport = httpx.MockTransport(handler)


class TestCover:
    def test_redirects_to_thumbnail(self, client):
        _install(lambda request: httpx.Response(200, json={"thumbnail_url": THUMB}))
        response = client.get("/cover/3nqQXoyQOWXiESFLlDF1hG", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == THUMB

    def test_no_thumbnail_in_response_404s(self, client):
        _install(lambda request: httpx.Response(200, json={"title": "no art here"}))
        assert client.get("/cover/does-not-exist", follow_redirects=False).status_code == 404

    def test_upstream_error_404s(self, client):
        _install(lambda request: httpx.Response(404))
        assert client.get("/cover/bad-id", follow_redirects=False).status_code == 404

    def test_timeout_404s(self, client):
        def handler(request):
            raise httpx.ConnectTimeout("timed out")
        _install(handler)
        assert client.get("/cover/whatever", follow_redirects=False).status_code == 404

    def test_second_call_served_from_cache(self, client):
        handler_calls = []

        def handler(request):
            handler_calls.append(request)
            return httpx.Response(200, json={"thumbnail_url": THUMB})

        _install(handler)
        client.get("/cover/abc", follow_redirects=False)
        client.get("/cover/abc", follow_redirects=False)
        assert len(handler_calls) == 1

    def test_requests_oembed_with_spotify_uri(self, client):
        captured = {}

        def handler(request: httpx.Request):
            captured["url"] = str(request.url)
            return httpx.Response(200, json={"thumbnail_url": THUMB})

        _install(handler)
        client.get("/cover/xyz123", follow_redirects=False)
        assert "open.spotify.com/oembed" in captured["url"]
        assert "spotify%3Atrack%3Axyz123" in captured["url"] or "spotify:track:xyz123" in captured["url"]
