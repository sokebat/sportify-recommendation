from src.recommendation.mood import MOOD_ALIASES, recommend_by_mood


class TestRecommendByMood:
    def test_all_frontend_moods_return_results(self, tracks, mood_matrix):
        for mood in MOOD_ALIASES:
            recs = recommend_by_mood(tracks, mood_matrix, mood, top_n=10)
            assert len(recs) == 10, f"mood={mood!r} returned {len(recs)} results"

    def test_results_are_in_the_aliased_mood_bucket(self, tracks, mood_matrix):
        recs = recommend_by_mood(tracks, mood_matrix, "happy", top_n=10)
        # join on track_id (unique per row) rather than track_name, which
        # this dataset repeats across unrelated genre/mood splits
        matched = tracks.set_index("track_id").loc[recs["track_id"]]
        assert all(matched["mood_label"] == "bright_energetic")

    def test_no_duplicate_tracks_in_results(self, tracks, mood_matrix):
        recs = recommend_by_mood(tracks, mood_matrix, "sad", top_n=10)
        assert not recs.duplicated(subset=["track_name", "artists"]).any()

    def test_unknown_mood_returns_empty(self, tracks, mood_matrix):
        recs = recommend_by_mood(tracks, mood_matrix, "this-is-not-a-real-mood", top_n=10)
        assert recs.empty

    def test_genre_filter_narrows_candidate_pool(self, tracks, mood_matrix):
        recs = recommend_by_mood(tracks, mood_matrix, "happy", top_n=10, genre="pop")
        assert len(recs) > 0
        assert all("pop" in genre.lower() for genre in recs["track_genre"])
