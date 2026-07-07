"""
End-to-end tests through the FastAPI app itself (routing, request
validation, response shape) rather than the recommendation logic directly -
that's covered by test_similar_song.py / test_mood.py / test_genre.py /
test_playlist.py / test_catalog.py.
"""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.state import state


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        if not state.loaded:
            pytest.skip("catalog artifacts not built - run notebooks/01-09 (see README)")
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["n_songs"] > 0


def test_similar_song(client):
    response = client.post("/recommend/similar-song", json={"song_name": "Blinding Lights", "n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 5


def test_similar_song_not_found(client):
    response = client.post("/recommend/similar-song", json={"song_name": "not a real song xyz123"})
    assert response.status_code == 404
    assert "detail" in response.json()


def test_playlist(client):
    response = client.post("/recommend/playlist", json={"songs": ["Blinding Lights", "Shape of You"], "n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 5


def test_mood(client):
    response = client.post("/recommend/mood", json={"mood": "happy", "n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 5


def test_genre(client):
    response = client.post("/recommend/genre", json={"genre": "rock", "n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 5


def test_popularity(client):
    response = client.post("/recommend/popularity", json={"n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 5


def test_artist(client):
    response = client.post("/recommend/artist", json={"artist": "Ed Sheeran", "n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0


def test_search_songs(client):
    response = client.post("/recommend/search-songs", json={"query": "Ed Sheeran", "n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0


def test_n_is_bounded(client):
    response = client.post("/recommend/popularity", json={"n": 1000})
    assert response.status_code == 422


def test_discover(client):
    response = client.post("/recommend/discover", json={"song_name": "Blinding Lights", "n": 5})
    assert response.status_code == 200
    assert len(response.json()["results"]) == 5


def test_discover_not_found(client):
    response = client.post("/recommend/discover", json={"song_name": "not a real song xyz123"})
    assert response.status_code == 404
    assert "detail" in response.json()
