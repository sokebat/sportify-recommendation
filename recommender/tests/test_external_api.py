"""
End-to-end tests for the Spotify-backed endpoints (/external/*,
/recommend/from-external) - fully offline and artifact-free: the app state
is populated with a small synthetic catalog (the bridge logic needs
externally styled names the real dataset can't guarantee) and the httpx
transport is swapped for httpx.MockTransport. Cover art (/cover) is a
separate, unauthenticated code path - see test_media.py.
"""
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.feature_extraction.text import TfidfVectorizer

import httpx

from src.api import spotify
from src.api.main import app
from src.api.state import state

TOKEN_RESPONSE = {"access_token": "test-token", "token_type": "bearer", "expires_in": 3600}
THUMB = "https://i.scdn.co/image/ab67616d0000b273abc"
SPOTIFY_URL_PREFIX = "https://open.spotify.com/track/"


def _track(track_id, name, artist, album="Album", popularity=90, images=None):
    return {
        "id": track_id,
        "name": name,
        "popularity": popularity,
        "artists": [{"name": artist}],
        "album": {"name": album, "images": images if images is not None else [{"url": THUMB, "width": 300}]},
        "external_urls": {"spotify": f"{SPOTIFY_URL_PREFIX}{track_id}"},
    }


TRENDING_PAYLOAD = {
    "items": [
        {"track": _track("t0", "Blinding Lights", "The Weeknd", "After Hours", 95)},
        {"track": _track("sp-unknown-99", "Zz Mystery Song", "Zz Unknown", images=[])},
    ]
}

QUEEN_ARTIST = {
    "name": "Queen",
    "genres": ["rock", "classic rock"],
    "followers": {"total": 50000000},
    "popularity": 85,
    "images": [{"url": "https://i.scdn.co/image/queen.jpg", "width": 300}],
    "external_urls": {"spotify": "https://open.spotify.com/artist/queen"},
}

QUEEN_TOP_TRACKS = [
    _track("t4", "Bohemian Rhapsody", "Queen", "A Night at the Opera", 92),
]

# Not a substring of any catalog `artists` value, so the artist-fallback
# step (a pure local lookup) can't accidentally succeed before genre fallback
# is reached - isolates the "no genre hint, ask Spotify" path.
FICTIONAL_ARTIST = {
    "name": "Fictional Rock Band",
    "genres": ["rock"],
    "followers": {"total": 100},
    "popularity": 1,
    "images": [],
    "external_urls": {},
}


def _api_handler(request: httpx.Request) -> httpx.Response:
    if request.url.host == "accounts.spotify.com":
        return httpx.Response(200, json=TOKEN_RESPONSE)

    path = request.url.path
    params = dict(request.url.params)

    if path.endswith("/items") and "playlists" in path:
        return httpx.Response(200, json=TRENDING_PAYLOAD)

    if path == "/v1/search":
        query = params.get("q", "")
        if params.get("type") == "artist":
            if "queen" in query.lower():
                return httpx.Response(200, json={"artists": {"items": [QUEEN_ARTIST]}})
            if "fictional rock band" in query.lower():
                return httpx.Response(200, json={"artists": {"items": [FICTIONAL_ARTIST]}})
            return httpx.Response(200, json={"artists": {"items": []}})
        if params.get("type") == "track":
            if query.lower().startswith('track:'):
                if "bohemian rhapsody" in query.lower():
                    return httpx.Response(200, json={"tracks": {"items": [QUEEN_TOP_TRACKS[0]]}})
                return httpx.Response(200, json={"tracks": {"items": []}})
            # artist-popularity search, e.g. q=artist:"Queen"
            if "queen" in query.lower():
                return httpx.Response(200, json={"tracks": {"items": QUEEN_TOP_TRACKS}})
            return httpx.Response(200, json={"tracks": {"items": []}})

    if path.startswith("/v1/tracks/"):
        track_id = path.rsplit("/", 1)[-1]
        if track_id == "t4":
            return httpx.Response(200, json=_track("t4", "Bohemian Rhapsody", "Queen"))
        return httpx.Response(404, json={"error": {"status": 404, "message": "not found"}})

    return httpx.Response(404)


def _make_tracks() -> pd.DataFrame:
    rows = [
        ("t0", "Blinding Lights", "The Weeknd", "After Hours", "pop", 95),
        ("t1", "Save Your Tears", "The Weeknd", "After Hours", "pop", 90),
        ("t2", "Levitating", "Dua Lipa;DaBaby", "Future Nostalgia", "pop", 88),
        ("t3", "Watermelon Sugar", "Harry Styles", "Fine Line", "pop", 85),
        ("t4", "Bohemian Rhapsody", "Queen", "A Night at the Opera", "rock", 92),
        ("t5", "Somebody to Love", "Queen", "A Day at the Races", "rock", 84),
        ("t6", "Yellow", "Coldplay", "Parachutes", "rock", 80),
        ("t7", "Blinding Lights", "Kidz Chartz", "Kidz Covers", "children", 10),
    ]
    tracks = pd.DataFrame(
        rows, columns=["track_id", "track_name", "artists", "album_name", "track_genre", "popularity"],
    )
    tracks["content_index"] = tracks.index
    return tracks


@pytest.fixture(scope="module", autouse=True)
def synthetic_state():
    saved = state.__dict__.copy()
    tracks = _make_tracks()
    vectorizer = TfidfVectorizer()
    state.tracks = tracks
    state.sound_matrix = np.random.RandomState(0).rand(len(tracks), 4)
    state.genre_matrix = vectorizer.fit_transform(tracks["track_genre"])
    state.genre_vectorizer = vectorizer
    state.loaded = True
    yield
    state.__dict__.update(saved)


@pytest.fixture(autouse=True)
def spotify_sandbox(monkeypatch):
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test-client-secret")
    spotify._cache.clear()
    spotify._token.clear()
    spotify._transport = httpx.MockTransport(_api_handler)
    yield
    spotify._cache.clear()
    spotify._token.clear()
    spotify._transport = None


@pytest.fixture(scope="module")
def client():
    # No `with`: lifespan (and its real-artifact state.load()) must not run -
    # the module uses the synthetic state above.
    return TestClient(app)


class TestTrending:
    def test_shape_and_catalog_flags(self, client):
        response = client.get("/external/trending")
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 2

        matched, unmatched = results
        assert matched["in_catalog"] is True
        assert matched["catalog_track_id"] == "t0"
        assert matched["thumb_url"] == THUMB
        assert matched["spotify_url"] == f"{SPOTIFY_URL_PREFIX}t0"
        assert matched["chart_place"] == 1
        assert unmatched["in_catalog"] is False
        assert unmatched["catalog_track_id"] is None
        assert unmatched["thumb_url"] is None

    def test_limit_respected(self, client):
        response = client.get("/external/trending", params={"limit": 1})
        assert len(response.json()["results"]) == 1

    def test_upstream_failure_returns_empty_200(self, client):
        spotify._transport = httpx.MockTransport(lambda request: httpx.Response(500))
        response = client.get("/external/trending")
        assert response.status_code == 200
        assert response.json()["results"] == []


class TestArtistDetail:
    def test_known_artist(self, client):
        response = client.get("/external/artist/Queen")
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "Queen"
        assert body["genres"] == ["rock", "classic rock"]
        assert body["followers"] == 50000000
        assert body["popularity"] == 85
        assert body["thumb_url"] == "https://i.scdn.co/image/queen.jpg"
        assert body["spotify_url"] == "https://open.spotify.com/artist/queen"
        top = body["top_tracks"][0]
        assert top["track"] == "Bohemian Rhapsody"
        assert top["in_catalog"] is True
        assert top["catalog_track_id"] == "t4"

    def test_unknown_artist_404(self, client):
        assert client.get("/external/artist/Zz Nobody").status_code == 404


class TestTrackInfo:
    def test_known_track(self, client):
        response = client.get(
            "/external/track", params={"artist": "Queen", "track": "Bohemian Rhapsody"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["spotify_url"] == f"{SPOTIFY_URL_PREFIX}t4"
        assert body["thumb_url"] == THUMB

    def test_unknown_track_404(self, client):
        response = client.get("/external/track", params={"artist": "Zz", "track": "Zz"})
        assert response.status_code == 404


class TestFromExternal:
    def test_spotify_id_fast_path(self, client):
        # Name is deliberately wrong; the exact Spotify ID match should still win.
        response = client.post(
            "/recommend/from-external",
            json={"artist": "Someone Else", "track": "Totally Different Title", "spotify_id": "t0"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["matched_by"] == "track"
        assert body["seed"]["track_id"] == "t0"

    def test_track_match_by_name(self, client):
        response = client.post(
            "/recommend/from-external", json={"artist": "The Weeknd", "track": "Blinding Lights"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["matched_by"] == "track"
        assert body["seed"]["track_id"] == "t0"
        assert len(body["results"]) > 0
        assert all(song["track_genre"] == "pop" for song in body["results"])
        assert all(song["track_id"] != "t0" for song in body["results"])

    def test_title_normalization_still_matches(self, client):
        response = client.post(
            "/recommend/from-external",
            json={"artist": "The Weeknd", "track": "Blinding Lights (Radio Edit)"},
        )
        assert response.json()["matched_by"] == "track"

    def test_artist_fallback(self, client):
        response = client.post(
            "/recommend/from-external", json={"artist": "Queen", "track": "Zz Not In Catalog"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["matched_by"] == "artist"
        assert body["seed"]["track_name"] == "Bohemian Rhapsody"
        assert len(body["results"]) > 0

    def test_genre_fallback_with_hint(self, client):
        response = client.post(
            "/recommend/from-external",
            json={"artist": "Zz Unknown", "track": "Zz Mystery Song", "genre": "rock"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["matched_by"] == "genre"
        assert body["seed"] is None
        assert all(song["track_genre"] == "rock" for song in body["results"])

    def test_genre_fetched_from_artist_when_no_hint(self, client):
        # Neither track nor artist bridge to the catalog and no genre hint is
        # given - Search-by-artist-name answers this artist's genres, whose
        # first entry ("rock") maps straight through.
        response = client.post(
            "/recommend/from-external", json={"artist": "Fictional Rock Band", "track": "Zz Cover Version"},
        )
        assert response.status_code == 200
        assert response.json()["matched_by"] == "genre"

    def test_unbridgeable_track_404(self, client):
        response = client.post(
            "/recommend/from-external", json={"artist": "Zz Nobody", "track": "Zz Nothing"},
        )
        assert response.status_code == 404
        assert "detail" in response.json()


class TestUnloadedCatalog:
    """Without the trained artifacts the server still boots: model endpoints
    answer 503, live Spotify endpoints keep working."""

    @pytest.fixture(autouse=True)
    def unloaded_state(self):
        state.loaded = False
        yield
        state.loaded = True

    def test_recommend_endpoints_return_503(self, client):
        response = client.post("/recommend/popularity", json={"n": 5})
        assert response.status_code == 503
        assert "Catalog not loaded" in response.json()["detail"]
        response = client.post(
            "/recommend/from-external", json={"artist": "Queen", "track": "Bohemian Rhapsody"},
        )
        assert response.status_code == 503

    def test_external_endpoints_still_work(self, client):
        response = client.get("/external/trending")
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 2
        assert all(item["in_catalog"] is False for item in results)

    def test_health_reports_not_loaded(self, client):
        assert client.get("/health").json()["status"] == "not_loaded"


