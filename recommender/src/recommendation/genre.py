"""
Genre recommender: TF-IDF over a genre/mood/tempo text descriptor per
track, filtered to the query's genre so a track only shows up for a genre
it's actually tagged with. See notebooks/09_model_tfidf.ipynb.
"""
import pandas as pd
from scipy.sparse import spmatrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.recommendation.catalog import RESULT_COLUMNS, finalize_results, top_candidate_indices


def recommend_by_genre(
    tracks: pd.DataFrame,
    descriptor_matrix: spmatrix,
    vectorizer: TfidfVectorizer,
    genre: str,
    top_n: int = 10,
    relevance_weight: float = 0.7,
) -> pd.DataFrame:
    """Empty result means no catalog genre contains `genre` as a substring."""
    genre = genre.strip().lower()
    if not genre:
        return tracks.iloc[0:0][RESULT_COLUMNS]

    primary_term = genre.split()[0]
    genre_mask = tracks["track_genre"].str.contains(primary_term, case=False, na=False)
    if not genre_mask.any():
        return tracks.iloc[0:0][RESULT_COLUMNS]

    candidate_indices = tracks.index[genre_mask].to_numpy()
    query_vector = vectorizer.transform([genre])
    similarity = cosine_similarity(query_vector, descriptor_matrix[candidate_indices])[0]
    popularity_norm = tracks.loc[candidate_indices, "popularity"].to_numpy() / 100

    combined_score = relevance_weight * similarity + (1 - relevance_weight) * popularity_norm
    ranked_indices = top_candidate_indices(candidate_indices, combined_score, top_n)
    return finalize_results(tracks, ranked_indices, top_n)
