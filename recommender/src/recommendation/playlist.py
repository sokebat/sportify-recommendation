"""
Playlist recommender: blends every seed track's audio profile into one
popularity-weighted centroid, then finds the nearest catalog tracks across
the union of the playlist's own genres. See notebooks/06_model_knn.ipynb -
reuses the same audio feature space as the similar-song model (05), and
notebooks/06's own metric sweep (cosine/euclidean/manhattan, scored by
genre-match-rate) picks the distance metric via `knn_metric`, so a re-run of
that notebook with a different winner takes effect here without a code change.
"""
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from src.recommendation.catalog import RESULT_COLUMNS, dedupe_by_track, find_track_index

POOL_MULTIPLIER = 5
DEFAULT_METRIC = "cosine"


def recommend_for_playlist(
    tracks: pd.DataFrame,
    sound_matrix: np.ndarray,
    song_names: list[str],
    top_n: int = 10,
    metric: str = DEFAULT_METRIC,
) -> pd.DataFrame:
    """Song names that don't match any catalog track are silently skipped -
    an empty result means none of them matched."""
    indices = [idx for idx in (find_track_index(tracks, name) for name in song_names) if idx is not None]
    if not indices:
        return tracks.iloc[0:0][RESULT_COLUMNS]

    weights = tracks.loc[indices, "popularity"].to_numpy() + 1  # avoid zero-weight tracks
    centroid = np.average(sound_matrix[indices], axis=0, weights=weights).reshape(1, -1)

    playlist_genres = set(tracks.loc[indices, "track_genre"])
    # Exclude every row that's a duplicate of a seed track (same title+artist
    # under a different genre split), not just the seed's own row index -
    # otherwise a seed can come back as its own "recommendation".
    all_pairs = pd.MultiIndex.from_arrays([tracks["track_name"], tracks["artists"]])
    seed_pairs = pd.MultiIndex.from_arrays([tracks.loc[indices, "track_name"], tracks.loc[indices, "artists"]])
    candidate_mask = tracks["track_genre"].isin(playlist_genres) & ~all_pairs.isin(seed_pairs)
    candidate_indices = tracks.index[candidate_mask].to_numpy()

    n_neighbors = min(top_n * POOL_MULTIPLIER, len(candidate_indices))
    if n_neighbors == 0:
        return tracks.iloc[0:0][RESULT_COLUMNS]

    knn = NearestNeighbors(n_neighbors=n_neighbors, metric=metric, n_jobs=-1)
    knn.fit(sound_matrix[candidate_indices])
    _, neighbor_positions = knn.kneighbors(centroid)

    ranked_indices = candidate_indices[neighbor_positions[0]]
    ranked = tracks.loc[ranked_indices, RESULT_COLUMNS]
    return dedupe_by_track(ranked, top_n).reset_index(drop=True)
