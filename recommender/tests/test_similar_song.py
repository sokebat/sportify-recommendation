from src.recommendation.similar_song import recommend_similar_songs


class TestRecommendSimilarSongs:
    def test_returns_requested_number_of_results(self, tracks, sound_matrix, seed_song):
        track_name, artist = seed_song
        recs = recommend_similar_songs(tracks, sound_matrix, track_name, artist, top_n=10)
        assert recs is not None
        assert len(recs) == 10

    def test_never_recommends_a_duplicate_of_the_seed(self, tracks, sound_matrix, seed_song):
        track_name, artist = seed_song
        recs = recommend_similar_songs(tracks, sound_matrix, track_name, artist, top_n=10)
        same_track = recs[(recs["track_name"] == track_name) & (recs["artists"] == artist)]
        assert same_track.empty

    def test_never_recommends_a_duplicate_of_a_widely_duplicated_seed(self, tracks, sound_matrix):
        # "Blinding Lights" by The Weeknd appears multiple times across genre
        # splits in this dataset - a real case that would otherwise let the
        # seed rank as its own "similar" match.
        recs = recommend_similar_songs(tracks, sound_matrix, "Blinding Lights", "The Weeknd", top_n=10)
        assert recs is not None
        same_track = recs[(recs["track_name"] == "Blinding Lights") & (recs["artists"] == "The Weeknd")]
        assert same_track.empty

    def test_results_stay_within_seed_genre(self, tracks, sound_matrix, seed_song):
        track_name, artist = seed_song
        seed_genre = tracks[(tracks["track_name"] == track_name) & (tracks["artists"] == artist)].iloc[0]["track_genre"]
        recs = recommend_similar_songs(tracks, sound_matrix, track_name, artist, top_n=10)
        assert all(recs["track_genre"] == seed_genre)

    def test_no_duplicate_tracks_in_results(self, tracks, sound_matrix, seed_song):
        track_name, artist = seed_song
        recs = recommend_similar_songs(tracks, sound_matrix, track_name, artist, top_n=10)
        assert not recs.duplicated(subset=["track_name", "artists"]).any()

    def test_unknown_track_returns_none(self, tracks, sound_matrix):
        assert recommend_similar_songs(tracks, sound_matrix, "this track definitely does not exist xyz123") is None
