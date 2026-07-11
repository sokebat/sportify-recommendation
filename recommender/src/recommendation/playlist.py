"""
Playlist recommender: averages every seed track's audio profile (weighted
by popularity) into one centroid, then finds the nearest catalog tracks
across all the playlist's genres. Distance metric comes from `knn_metric`,
picked by notebooks/06.
"""
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from src.recommendation.catalog import (
    POOL_MULTIPLIER,
    RESULT_COLUMNS,
    finalize_results,
    find_track_index,
)

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
    # Skip every row that duplicates a seed track, not just the seed's own
    # row - otherwise a seed could get recommended as itself.
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
    return finalize_results(tracks, ranked_indices, top_n)
