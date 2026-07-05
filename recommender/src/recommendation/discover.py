"""
Discover recommender: nearest neighbors in the hybrid feature space (audio +
categorical + text signal, weighted and L2-normalized) with no genre gate -
the deliberate opposite of recommend_similar_songs, which stays inside one
genre. See notebooks/09_model_hybrid.ipynb: notebook 11's own model
comparison scores this space highest on diversity (0.30 vs 0.10 for the
genre-gated models) and ties cosine similarity for novelty (0.686), at the
cost of weaker genre precision (0.71 vs 1.0) - a fair trade for a "you might
also like something different" feature.
"""
import pandas as pd
from scipy.sparse import spmatrix
from sklearn.neighbors import NearestNeighbors

from src.recommendation.catalog import RESULT_COLUMNS, dedupe_by_track, find_track_index

POOL_MULTIPLIER = 5


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

    query_name = tracks.loc[query_index, "track_name"]
    query_artists = tracks.loc[query_index, "artists"]
    # Same duplicate guard as recommend_similar_songs: exclude every row
    # that's a copy of the seed (same title+artist under a different genre
    # split), not just the seed's own row index.
    is_seed_duplicate = (tracks["track_name"] == query_name) & (tracks["artists"] == query_artists)

    n_neighbors = min(top_n * POOL_MULTIPLIER + 1, hybrid_matrix.shape[0])
    _, neighbor_positions = hybrid_model.kneighbors(hybrid_matrix[query_index], n_neighbors=n_neighbors)

    candidate_positions = [pos for pos in neighbor_positions[0] if not is_seed_duplicate.iloc[pos]]
    ranked = tracks.iloc[candidate_positions][RESULT_COLUMNS]
    return dedupe_by_track(ranked, top_n).reset_index(drop=True)
