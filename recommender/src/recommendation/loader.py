"""
Loads the tracks catalog and the trained content-based model artifacts from
models/content_based/ once, so the API can reuse them across requests
instead of re-reading disk (or refitting anything) per call.

Artifacts come from five independent model notebooks, each producing one
file (or file pair) consumed here:
    notebooks/05_model_cosine.ipynb   -> cosine_feature_matrix.npy    (similar-song, playlist)
    notebooks/06_model_knn.ipynb      -> knn_config.json              (playlist - which distance metric to use)
    notebooks/07_model_weighted.ipynb -> weighted_feature_matrix.npy  (mood)
    notebooks/08_model_tfidf.ipynb    -> tfidf_matrix.npz + tfidf_vectorizer.joblib (genre)
    notebooks/09_model_hybrid.ipynb   -> content_based_knn_tfidf_weighted_model.joblib
                                          + tfidf_weighted_feature_matrix.npz (discover)
"""
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import load_npz, spmatrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

MODEL_DIR_NAME = "content_based"
TRACKS_FILENAME = "content_tracks_engineered.csv"
DEFAULT_KNN_METRIC = "cosine"


@dataclass
class RecommenderArtifacts:
    tracks: pd.DataFrame
    sound_matrix: np.ndarray
    mood_matrix: np.ndarray
    genre_descriptor_matrix: spmatrix
    genre_vectorizer: TfidfVectorizer
    knn_metric: str
    hybrid_model: NearestNeighbors
    hybrid_matrix: spmatrix


def load_artifacts(project_dir: Path) -> RecommenderArtifacts:
    processed_dir = project_dir / "data" / "processed"
    model_dir = project_dir / "models" / MODEL_DIR_NAME

    tracks_path = processed_dir / TRACKS_FILENAME
    if not tracks_path.exists():
        raise FileNotFoundError(
            f"{tracks_path} not found - run notebooks/01-04 to build the processed catalog."
        )

    tracks = pd.read_csv(tracks_path)

    sound_matrix = np.load(model_dir / "cosine_feature_matrix.npy")
    mood_matrix = np.load(model_dir / "weighted_feature_matrix.npy")
    genre_descriptor_matrix = load_npz(model_dir / "tfidf_matrix.npz")
    genre_vectorizer = joblib.load(model_dir / "tfidf_vectorizer.joblib")

    with open(model_dir / "knn_config.json", "r", encoding="utf-8") as file:
        knn_metric = json.load(file).get("metric", DEFAULT_KNN_METRIC)

    hybrid_model = joblib.load(model_dir / "content_based_knn_tfidf_weighted_model.joblib")
    hybrid_matrix = load_npz(model_dir / "tfidf_weighted_feature_matrix.npz")

    if (
        sound_matrix.shape[0] != len(tracks)
        or mood_matrix.shape[0] != len(tracks)
        or hybrid_matrix.shape[0] != len(tracks)
    ):
        raise RuntimeError(
            "Model artifacts are out of sync with content_tracks_engineered.csv - "
            "retrain via notebooks 04 through 09."
        )

    return RecommenderArtifacts(
        tracks=tracks,
        sound_matrix=sound_matrix,
        mood_matrix=mood_matrix,
        genre_descriptor_matrix=genre_descriptor_matrix,
        genre_vectorizer=genre_vectorizer,
        knn_metric=knn_metric,
        hybrid_model=hybrid_model,
        hybrid_matrix=hybrid_matrix,
    )
