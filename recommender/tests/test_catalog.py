from src.recommendation.catalog import (
    dedupe_by_track,
    find_track_index,
    popular_songs,
    search_songs,
    songs_by_artist,
)


class TestFindTrackIndex:
    def test_finds_known_track(self, tracks, seed_song):
        track_name, artist = seed_song
        index = find_track_index(tracks, track_name, artist)
        assert index is not None
        assert tracks.loc[index, "track_name"] == track_name

    def test_unknown_track_returns_none(self, tracks):
        assert find_track_index(tracks, "this track definitely does not exist xyz123") is None

    def test_artist_filter_narrows_match(self, tracks, seed_song):
        track_name, artist = seed_song
        assert find_track_index(tracks, track_name, artist="zzz_no_such_artist_zzz") is None

    def test_picks_the_most_popular_match_when_title_is_ambiguous(self, tracks):
        # "Blinding Lights" exists both as The Weeknd's hit and as an
        # unrelated, far less popular cover in this dataset - without an
        # artist filter, the popular version should win, not just whichever
        # row happens to come first in the CSV.
        index = find_track_index(tracks, "Blinding Lights")
        assert index is not None
        assert tracks.loc[index, "artists"] == "The Weeknd"


class TestSearchSongs:
    def test_matches_by_track_name_substring(self, tracks):
        results = search_songs(tracks, "Blinding Lights", limit=5)
        assert len(results) > 0
        assert all("blinding lights" in name.lower() for name in results["track_name"])

    def test_matches_by_artist_substring(self, tracks):
        results = search_songs(tracks, "Ed Sheeran", limit=5)
        assert len(results) > 0
        assert all("ed sheeran" in artists.lower() for artists in results["artists"])

    def test_blank_query_returns_empty(self, tracks):
        assert search_songs(tracks, "   ", limit=5).empty

    def test_respects_limit(self, tracks):
        assert len(search_songs(tracks, "a", limit=3)) <= 3


class TestPopularSongs:
    def test_sorted_descending_by_popularity(self, tracks):
        results = popular_songs(tracks, limit=10)
        popularity = results["popularity"].to_numpy()
        assert all(popularity[i] >= popularity[i + 1] for i in range(len(popularity) - 1))

    def test_genre_filter_restricts_results(self, tracks):
        results = popular_songs(tracks, genre="jazz", limit=10)
        assert all("jazz" in genre.lower() for genre in results["track_genre"])

    def test_no_duplicate_tracks(self, tracks):
        results = popular_songs(tracks, limit=20)
        assert not results.duplicated(subset=["track_name", "artists"]).any()


class TestSongsByArtist:
    def test_matches_artist_substring(self, tracks, seed_song):
        _, artist = seed_song
        results = songs_by_artist(tracks, artist, limit=10)
        assert len(results) > 0
        assert all(artist.lower() in artists.lower() for artists in results["artists"])


class TestDedupeByTrack:
    def test_collapses_same_track_name_and_artist(self, tracks):
        duplicated = tracks.iloc[[0, 0, 1]]
        result = dedupe_by_track(duplicated, limit=10)
        assert len(result) == 2

    def test_respects_limit_after_dedup(self, tracks):
        result = dedupe_by_track(tracks.head(20), limit=5)
        assert len(result) == 5
