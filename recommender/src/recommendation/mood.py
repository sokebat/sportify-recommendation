"""
Mood recommender: ranks tracks within a mood_label bucket by how central they
are to that bucket's centroid, blended with popularity so obscure tracks
don't crowd out songs a listener is actually likely to recognize. See
notebooks/08_model_weighted.ipynb.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.recommendation.catalog import RESULT_COLUMNS, dedupe_by_track

POOL_MULTIPLIER = 5

# The frontend's four mood buttons map onto the valence/energy quadrants that
# mood_label was engineered from (notebooks/04_feature_engineering.ipynb):
# happy = positive & energetic, angry = negative & energetic,
# sad = negative & calm, calm = positive & calm.
MOOD_ALIASES = {
    "happy": "bright_energetic",
    "angry": "intense_dark",
    "sad": "calm_dark",
    "calm": "calm_positive",
}


def recommend_by_mood(
    tracks: pd.DataFrame,
    mood_matrix: np.ndarray,
    mood: str,
    top_n: int = 10,
    genre: str | None = None,
    similarity_weight: float = 0.5,
) -> pd.DataFrame:
    """Unrecognized moods fall back to matching `mood` directly against the
    raw mood_label buckets, so callers can also pass e.g. 'calm_positive'."""
    mood_label = MOOD_ALIASES.get(mood.lower(), mood.lower())

    mood_mask = tracks["mood_label"] == mood_label
    if genre:
        mood_mask &= tracks["track_genre"].str.contains(genre, case=False, na=False)

    candidate_indices = tracks.index[mood_mask].to_numpy()
    if len(candidate_indices) == 0:
        return tracks.iloc[0:0][RESULT_COLUMNS]

    centroid = mood_matrix[candidate_indices].mean(axis=0, keepdims=True)
    similarity = cosine_similarity(centroid, mood_matrix[candidate_indices])[0]
    popularity_norm = tracks.loc[candidate_indices, "popularity"].to_numpy() / 100

    combined_score = similarity_weight * similarity + (1 - similarity_weight) * popularity_norm
    ranked_order = combined_score.argsort()[::-1][: top_n * POOL_MULTIPLIER]
    ranked_indices = candidate_indices[ranked_order]

    ranked = tracks.loc[ranked_indices, RESULT_COLUMNS]
    return dedupe_by_track(ranked, top_n).reset_index(drop=True)
