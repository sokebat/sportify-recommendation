"""
Mood recommender: ranks tracks in a mood_label bucket by how close they
are to that bucket's centroid, blended with popularity so obscure tracks
don't crowd out songs people actually know. See notebooks/08_model_weighted.ipynb.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.recommendation.catalog import RESULT_COLUMNS, finalize_results, top_candidate_indices

# Maps to the valence/energy quadrants mood_label was built from:
# happy = positive+energetic, angry = negative+energetic,
# sad = negative+calm, calm = positive+calm.
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
    ranked_indices = top_candidate_indices(candidate_indices, combined_score, top_n)
    return finalize_results(tracks, ranked_indices, top_n)
