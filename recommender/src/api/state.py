"""
Holds the tracks catalog and model artifacts loaded once at app startup, so
every request just reuses them instead of re-reading disk each time.
"""
from pathlib import Path

from src.recommendation.loader import load_artifacts

PROJECT_DIR = Path(__file__).resolve().parents[2]


class AppState:
    def __init__(self):
        self.tracks = None
        self.sound_matrix = None
        self.mood_matrix = None
        self.genre_matrix = None
        self.genre_vectorizer = None
        self.knn_metric = None
        self.hybrid_model = None
        self.hybrid_matrix = None
        self.loaded = False

    def load(self):
        artifacts = load_artifacts(PROJECT_DIR)
        self.tracks = artifacts.tracks
        self.sound_matrix = artifacts.sound_matrix
        self.mood_matrix = artifacts.mood_matrix
        self.genre_matrix = artifacts.genre_descriptor_matrix
        self.genre_vectorizer = artifacts.genre_vectorizer
        self.knn_metric = artifacts.knn_metric
        self.hybrid_model = artifacts.hybrid_model
        self.hybrid_matrix = artifacts.hybrid_matrix
        self.loaded = True
        print(f"Loaded {len(self.tracks):,} tracks, {self.tracks['track_genre'].nunique()} genres")


# single shared instance, imported by router.py and main.py
state = AppState()
