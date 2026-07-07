"""
Spotify client unit tests - fully offline: the httpx transport is swapped
for httpx.MockTransport (spotify._transport test seam), so these exercise
the Client Credentials token flow, caching and degradation logic, never the
real API.
"""
import asyncio

import httpx
import pytest

from src.api import spotify

TOKEN_RESPONSE = {"access_token": "test-token", "token_type": "bearer", "expires_in": 3600}


@pytest.fixture(autouse=True)
def sandbox(monkeypatch):
    spotify._cache.clear()
    spotify._token.clear()
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test-client-secret")
    yield
    spotify._cache.clear()
    spotify._token.clear()
    spotify._transport = None


class CountingHandler:
    def __init__(
        self, api_payload=None, api_status=200, api_exception=None,
        token_payload=TOKEN_RESPONSE, token_status=200, token_exception=None,
    ):
        self.token_calls = 0
        self.api_calls = 0
        self.api_payload = api_payload
        self.api_status = api_status
        self.api_exception = api_exception
        self.token_payload = token_payload
        self.token_status = token_status
        self.token_exception = token_exception

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.host == "accounts.spotify.com":
            self.token_calls += 1
            if self.token_exception:
                raise self.token_exception
            return httpx.Response(self.token_status, json=self.token_payload)
        self.api_calls += 1
        if self.api_exception:
            raise self.api_exception
        return httpx.Response(self.api_status, json=self.api_payload)


def _install(handler) -> None:
    spotify._transport = httpx.MockTransport(handler)


class TestToken:
    def test_missing_credentials_returns_none(self, monkeypatch):
        monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
        _install(CountingHandler())
        assert asyncio.run(spotify._get_token()) is None

    def test_fetches_and_caches_token(self):
        handler = CountingHandler()
        _install(handler)
        token1 = asyncio.run(spotify._get_token())
        token2 = asyncio.run(spotify._get_token())
        assert token1 == "test-token"
        assert token2 == "test-token"
        assert handler.token_calls == 1

    def test_token_failure_degrades_to_none(self):
        _install(CountingHandler(token_status=401, token_payload={"error": "invalid_client"}))
        assert asyncio.run(spotify._get_token()) is None

    def test_token_timeout_degrades_to_none(self):
        _install(CountingHandler(token_exception=httpx.ConnectTimeout("timed out")))
        assert asyncio.run(spotify._get_token()) is None


class TestFetchers:
    def test_trending_filters_null_tracks_and_maps_items(self):
        payload = {"items": [{"track": {"id": "1", "name": "Messy"}}, {"track": None}]}
        _install(CountingHandler(api_payload=payload))
        result = asyncio.run(spotify.fetch_trending_tracks())
        assert result == [{"id": "1", "name": "Messy"}]

    def test_artist_by_name_returns_first_match(self):
        payload = {"artists": {"items": [{"name": "Coldplay"}, {"name": "Coldplay Tribute"}]}}
        _install(CountingHandler(api_payload=payload))
        assert asyncio.run(spotify.fetch_artist_by_name("coldplay")) == {"name": "Coldplay"}

    def test_artist_by_name_no_match_returns_none(self):
        _install(CountingHandler(api_payload={"artists": {"items": []}}))
        assert asyncio.run(spotify.fetch_artist_by_name("nobody")) is None

    def test_popular_tracks_sorted_by_popularity_desc(self):
        payload = {
            "tracks": {"items": [{"name": "Low", "popularity": 20}, {"name": "High", "popularity": 90}]},
        }
        _install(CountingHandler(api_payload=payload))
        result = asyncio.run(spotify.fetch_popular_tracks_by_artist("Queen"))
        assert [t["name"] for t in result] == ["High", "Low"]

    def test_track_by_name_returns_first_match(self):
        payload = {"tracks": {"items": [{"name": "Yellow"}]}}
        _install(CountingHandler(api_payload=payload))
        assert asyncio.run(spotify.fetch_track_by_name("Coldplay", "Yellow")) == {"name": "Yellow"}

    def test_track_by_id(self):
        _install(CountingHandler(api_payload={"id": "abc", "name": "Yellow"}))
        assert asyncio.run(spotify.fetch_track_by_id("abc")) == {"id": "abc", "name": "Yellow"}

    def test_api_http_error_degrades(self):
        _install(CountingHandler(api_status=500))
        assert asyncio.run(spotify.fetch_trending_tracks()) == []
        assert asyncio.run(spotify.fetch_artist_by_name("x")) is None

    def test_api_timeout_degrades(self):
        _install(CountingHandler(api_exception=httpx.ConnectTimeout("timed out")))
        assert asyncio.run(spotify.fetch_trending_tracks()) == []


class TestCache:
    def test_second_call_served_from_cache_and_reuses_token(self):
        handler = CountingHandler(api_payload={"items": []})
        _install(handler)
        asyncio.run(spotify.fetch_trending_tracks())
        asyncio.run(spotify.fetch_trending_tracks())
        assert handler.api_calls == 1
        assert handler.token_calls == 1

    def test_stale_entry_served_when_refetch_fails(self):
        _install(CountingHandler(api_payload={"items": [{"track": {"id": "1", "name": "Messy"}}]}))
        first = asyncio.run(spotify.fetch_trending_tracks())
        spotify._cache.clear()
        _install(CountingHandler(api_status=500))
        # cache was cleared, so a failure with nothing cached degrades to empty
        assert asyncio.run(spotify.fetch_trending_tracks()) == []
        assert first == [{"id": "1", "name": "Messy"}]


class TestImageUrl:
    def test_picks_closest_to_target_width(self):
        images = [{"url": "big", "width": 640}, {"url": "mid", "width": 300}, {"url": "small", "width": 64}]
        assert spotify.image_url(images, target_width=300) == "mid"

    def test_empty_list_returns_none(self):
        assert spotify.image_url([]) is None
        assert spotify.image_url(None) is None

    def test_missing_width_falls_back_to_first(self):
        assert spotify.image_url([{"url": "only"}]) == "only"
