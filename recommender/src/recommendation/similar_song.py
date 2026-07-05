"""
Similar-song recommender: cosine similarity over a genre-matched candidate
pool, in the "how it sounds" audio feature space fit in
notebooks/06_model_cosine.ipynb. Genre-filtering the candidate pool before
ranking is what keeps results musically relevant - unfiltered cosine
similarity over raw audio features tends to surface tracks that are
numerically close but genre-unrelated (e.g. two quiet instrumental tracks
from completely different genres).
"""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.recommendation.catalog import RESULT_COLUMNS, dedupe_by_track, find_track_index

# How much further than top_n to rank before deduping - this dataset repeats
# the same track across genre splits, so the raw top-N is often mostly
# duplicates of one song; a wider pool leaves enough distinct tracks after dedup.
POOL_MULTIPLIER = 5


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
    query_name = tracks.loc[query_index, "track_name"]
    query_artists = tracks.loc[query_index, "artists"]
    # Exclude every row that's a duplicate of the seed (same title+artist
    # under a different genre/album split), not just its own row index -
    # otherwise a near-identical copy of the seed can rank as its own "similar" match.
    is_seed_duplicate = (tracks["track_name"] == query_name) & (tracks["artists"] == query_artists)
    candidate_mask = (tracks["track_genre"] == query_genre) & ~is_seed_duplicate
    candidate_indices = tracks.index[candidate_mask].to_numpy()

    similarity = cosine_similarity(sound_matrix[[query_index]], sound_matrix[candidate_indices])[0]
    ranked_order = similarity.argsort()[::-1][: top_n * POOL_MULTIPLIER]
    ranked_indices = candidate_indices[ranked_order]

    ranked = tracks.loc[ranked_indices, RESULT_COLUMNS]
    return dedupe_by_track(ranked, top_n).reset_index(drop=True)
