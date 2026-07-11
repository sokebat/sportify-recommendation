"""
Similar-song recommender: cosine similarity over tracks in the same genre,
using the audio feature space from notebooks/06_model_cosine.ipynb.
Filtering by genre first matters - without it, cosine similarity can match
tracks that are numerically close but don't actually sound related.
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.recommendation.catalog import (
    finalize_results,
    find_track_index,
    seed_duplicate_mask,
    top_candidate_indices,
)


def recommend_similar_songs(
    tracks: pd.DataFrame,
    sound_matrix: np.ndarray,
    track_name: str,
    artist: str | None = None,
    top_n: int = 10,
) -> pd.DataFrame | None:
    """Returns `None` if `track_name`/`artist` doesn't match any catalog track."""
    query_index = find_track_index(tracks, track_name, artist)
    if query_index is None:
        return None

    query_genre = tracks.loc[query_index, "track_genre"]
    # Skip every row that's a duplicate of the seed, not just its own row -
    # otherwise a copy of the seed could show up as its own "similar" match.
    candidate_mask = (tracks["track_genre"] == query_genre) & ~seed_duplicate_mask(tracks, query_index)
    candidate_indices = tracks.index[candidate_mask].to_numpy()

    similarity = cosine_similarity(sound_matrix[[query_index]], sound_matrix[candidate_indices])[0]
    ranked_indices = top_candidate_indices(candidate_indices, similarity, top_n)
    return finalize_results(tracks, ranked_indices, top_n)
