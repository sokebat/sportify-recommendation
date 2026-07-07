"""
Shared test fixtures. Loads the real trained artifacts (not mocks) since
they're already precomputed on disk (data/processed + models/content_based) -
loading them is a couple of seconds, and `session` scope means it only
happens once for the whole test run.
"""
from pathlib import Path

import pytest

from src.recommendation.loader import load_artifacts

PROJECT_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def artifacts():
    try:
        return load_artifacts(PROJECT_DIR)
    except FileNotFoundError as error:
        # Fresh checkout without the generated artifacts: skip (with the
        # build instructions) rather than error the whole suite - the
        # artifact-free tests (Spotify client, external API, normalizers)
        # still run.
        pytest.skip(str(error))


@pytest.fixture(scope="session")
def tracks(artifacts):
    return artifacts.tracks


@pytest.fixture(scope="session")
def sound_matrix(artifacts):
    return artifacts.sound_matrix


@pytest.fixture(scope="session")
def mood_matrix(artifacts):
    return artifacts.mood_matrix


@pytest.fixture(scope="session")
def genre_matrix(artifacts):
    return artifacts.genre_descriptor_matrix


@pytest.fixture(scope="session")
def genre_vectorizer(artifacts):
    return artifacts.genre_vectorizer


@pytest.fixture(scope="session")
def knn_metric(artifacts):
    return artifacts.knn_metric


@pytest.fixture(scope="session")
def hybrid_model(artifacts):
    return artifacts.hybrid_model


@pytest.fixture(scope="session")
def hybrid_matrix(artifacts):
    return artifacts.hybrid_matrix


@pytest.fixture(scope="session")
def seed_song(tracks):
    """A song guaranteed to exist in the catalog, for tests needing a real seed."""
    row = tracks.iloc[0]
    return row["track_name"], row["artists"].split(";")[0]
