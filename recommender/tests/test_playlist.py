from src.recommendation.playlist import recommend_for_playlist


class TestRecommendForPlaylist:
    def test_returns_requested_number_of_results(self, tracks, sound_matrix):
        songs = tracks["track_name"].head(3).tolist()
        recs = recommend_for_playlist(tracks, sound_matrix, songs, top_n=10)
        assert len(recs) == 10

    def test_never_recommends_a_seed_track_back(self, tracks, sound_matrix):
        songs = tracks["track_name"].head(3).tolist()
        recs = recommend_for_playlist(tracks, sound_matrix, songs, top_n=10)
        assert not any(name in songs for name in recs["track_name"])

    def test_no_duplicate_tracks_in_results(self, tracks, sound_matrix):
        songs = tracks["track_name"].head(3).tolist()
        recs = recommend_for_playlist(tracks, sound_matrix, songs, top_n=10)
        assert not recs.duplicated(subset=["track_name", "artists"]).any()

    def test_unknown_songs_are_skipped_not_errored(self, tracks, sound_matrix):
        recs = recommend_for_playlist(tracks, sound_matrix, ["not a real song xyz123"], top_n=5)
        assert recs.empty

    def test_mixed_known_and_unknown_songs_still_works(self, tracks, sound_matrix):
        known = tracks["track_name"].iloc[0]
        recs = recommend_for_playlist(tracks, sound_matrix, [known, "not a real song xyz123"], top_n=5)
        assert len(recs) == 5

    def test_uses_the_metric_from_notebook_06s_config(self, tracks, sound_matrix, knn_metric):
        # notebooks/06_model_knn.ipynb picks "cosine" via a genre-match-rate
        # sweep and saves it to knn_config.json - this should be the metric
        # actually driving the KNN call, not a separate hardcoded literal.
        assert knn_metric == "cosine"
        songs = tracks["track_name"].head(3).tolist()
        recs = recommend_for_playlist(tracks, sound_matrix, songs, top_n=10, metric=knn_metric)
        assert len(recs) == 10
