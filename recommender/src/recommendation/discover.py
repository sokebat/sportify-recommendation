"""
Discover recommender: finds nearest neighbors in the hybrid feature space
(audio + categorical + text), with no genre filter. Genre precision is
worse than recommend_similar_songs but results are more varied.
"""
import pandas as pd
from scipy.sparse import spmatrix
from sklearn.neighbors import NearestNeighbors

from src.recommendation.catalog import (
    POOL_MULTIPLIER,
    RESULT_COLUMNS,
    dedupe_by_track,
    find_track_index,
    seed_duplicate_mask,
)


def recommend_discover(
    tracks: pd.DataFrame,
    hybrid_model: NearestNeighbors,
    hybrid_matrix: spmatrix,
    track_name: str,
    artist: str | None = None,
    top_n: int = 10,
) -> pd.DataFrame | None:
    """Returns `None` if `track_name`/`artist` doesn't match any catalog track."""
    query_index = find_track_index(tracks, track_name, artist)
    if query_index is None:
        return None

    # Same duplicate guard as recommend_similar_songs - skip every row
    # that copies the seed, not just the seed's own row.
    is_seed_duplicate = seed_duplicate_mask(tracks, query_index)

    n_neighbors = min(top_n * POOL_MULTIPLIER + 1, hybrid_matrix.shape[0])
    _, neighbor_positions = hybrid_model.kneighbors(hybrid_matrix[query_index], n_neighbors=n_neighbors)

    candidate_positions = [pos for pos in neighbor_positions[0] if not is_seed_duplicate.iloc[pos]]
    ranked = tracks.iloc[candidate_positions][RESULT_COLUMNS]
    return dedupe_by_track(ranked, top_n).reset_index(drop=True)
