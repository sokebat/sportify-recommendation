from src.recommendation.genre import recommend_by_genre


class TestRecommendByGenre:
    def test_returns_requested_number_of_results(self, tracks, genre_matrix, genre_vectorizer):
        recs = recommend_by_genre(tracks, genre_matrix, genre_vectorizer, "rock", top_n=10)
        assert len(recs) == 10

    def test_results_are_hard_gated_to_the_genre(self, tracks, genre_matrix, genre_vectorizer):
        recs = recommend_by_genre(tracks, genre_matrix, genre_vectorizer, "k-pop", top_n=10)
        assert all("k-pop" in genre.lower() for genre in recs["track_genre"])

    def test_no_duplicate_tracks_in_results(self, tracks, genre_matrix, genre_vectorizer):
        recs = recommend_by_genre(tracks, genre_matrix, genre_vectorizer, "pop", top_n=10)
        assert not recs.duplicated(subset=["track_name", "artists"]).any()

    def test_unknown_genre_returns_empty(self, tracks, genre_matrix, genre_vectorizer):
        recs = recommend_by_genre(tracks, genre_matrix, genre_vectorizer, "not-a-real-genre-xyz", top_n=10)
        assert recs.empty

    def test_blank_genre_returns_empty(self, tracks, genre_matrix, genre_vectorizer):
        recs = recommend_by_genre(tracks, genre_matrix, genre_vectorizer, "  ", top_n=10)
        assert recs.empty
