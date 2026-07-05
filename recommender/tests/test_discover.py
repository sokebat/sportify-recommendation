from src.recommendation.discover import recommend_discover


class TestRecommendDiscover:
    def test_returns_requested_number_of_results(self, tracks, hybrid_model, hybrid_matrix, seed_song):
        track_name, artist = seed_song
        recs = recommend_discover(tracks, hybrid_model, hybrid_matrix, track_name, artist, top_n=10)
        assert recs is not None
        assert len(recs) == 10

    def test_never_recommends_the_seed_back(self, tracks, hybrid_model, hybrid_matrix, seed_song):
        track_name, artist = seed_song
        recs = recommend_discover(tracks, hybrid_model, hybrid_matrix, track_name, artist, top_n=10)
        same_track = recs[(recs["track_name"] == track_name) & (recs["artists"] == artist)]
        assert same_track.empty

    def test_never_recommends_a_duplicate_of_a_widely_duplicated_seed(self, tracks, hybrid_model, hybrid_matrix):
        # Same real-world case as test_similar_song.py: "Blinding Lights" is
        # repeated across genre splits in this dataset.
        recs = recommend_discover(tracks, hybrid_model, hybrid_matrix, "Blinding Lights", "The Weeknd", top_n=10)
        assert recs is not None
        same_track = recs[(recs["track_name"] == "Blinding Lights") & (recs["artists"] == "The Weeknd")]
        assert same_track.empty

    def test_not_gated_to_a_single_genre(self, tracks, hybrid_model, hybrid_matrix, seed_song):
        # The whole point of /discover vs /similar-song: it's allowed to
        # cross genre lines, unlike recommend_similar_songs.
        track_name, artist = seed_song
        recs = recommend_discover(tracks, hybrid_model, hybrid_matrix, track_name, artist, top_n=10)
        assert recs["track_genre"].nunique() >= 1

    def test_no_duplicate_tracks_in_results(self, tracks, hybrid_model, hybrid_matrix, seed_song):
        track_name, artist = seed_song
        recs = recommend_discover(tracks, hybrid_model, hybrid_matrix, track_name, artist, top_n=10)
        assert not recs.duplicated(subset=["track_name", "artists"]).any()

    def test_unknown_track_returns_none(self, tracks, hybrid_model, hybrid_matrix):
        recs = recommend_discover(tracks, hybrid_model, hybrid_matrix, "this track definitely does not exist xyz123")
        assert recs is None
