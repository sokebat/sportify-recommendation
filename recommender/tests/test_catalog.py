import pandas as pd

from src.recommendation.catalog import (
    dedupe_by_track,
    find_track_index,
    normalize_artist,
    normalize_title,
    popular_songs,
    resolve_external_track,
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


class TestNormalizeTitle:
    def test_strips_featuring_credit(self):
        assert normalize_title("Levitating (feat. DaBaby)") == "Levitating"

    def test_strips_dash_suffix(self):
        assert normalize_title("Blinding Lights - Radio Edit") == "Blinding Lights"

    def test_strips_bracketed_qualifier(self):
        assert normalize_title("Africa [Remastered 2019]") == "Africa"

    def test_plain_title_unchanged(self):
        assert normalize_title("Yellow") == "Yellow"


class TestNormalizeArtist:
    def test_strips_featuring(self):
        assert normalize_artist("Dua Lipa feat. DaBaby") == "Dua Lipa"

    def test_strips_ampersand_collaborator(self):
        assert normalize_artist("Tiesto & Ava Max") == "Tiesto"

    def test_strips_comma_collaborator(self):
        assert normalize_artist("Doja Cat, SZA") == "Doja Cat"

    def test_plain_artist_unchanged(self):
        assert normalize_artist("The Weeknd") == "The Weeknd"


class TestResolveExternalTrack:
    # Synthetic catalog rather than the real artifacts: the bridge is exercised
    # with externally styled names, which the real dataset can't guarantee.
    @staticmethod
    def _tracks() -> pd.DataFrame:
        tracks = pd.DataFrame(
            {
                "track_id": ["sp-levitating", "sp-blinding-lights", "sp-cover"],
                "track_name": ["Levitating", "Blinding Lights", "Blinding Lights"],
                "artists": ["Dua Lipa;DaBaby", "The Weeknd", "Kidz Chartz"],
                "popularity": [88, 95, 10],
            }
        )
        tracks["content_index"] = tracks.index
        return tracks

    def test_exact_match(self):
        assert resolve_external_track(self._tracks(), "Blinding Lights", "The Weeknd") == 1

    def test_normalized_title_match(self):
        assert resolve_external_track(self._tracks(), "Levitating (feat. DaBaby)", "Dua Lipa") == 0

    def test_normalized_artist_match(self):
        assert resolve_external_track(self._tracks(), "Blinding Lights", "The Weeknd & Someone Else") == 1

    def test_never_matches_on_title_alone(self):
        # A same-titled track by an unrelated artist must not become the seed.
        assert resolve_external_track(self._tracks(), "Blinding Lights", "Totally Unrelated") is None

    def test_spotify_id_matches_even_with_wrong_name(self):
        # The catalog's own track_id values are real Spotify IDs, so an exact
        # ID match should win regardless of how the name/artist are spelled.
        index = resolve_external_track(
            self._tracks(), "Completely Wrong Title", "Nobody", spotify_id="sp-blinding-lights",
        )
        assert index == 1

    def test_spotify_id_miss_falls_back_to_name_matching(self):
        index = resolve_external_track(
            self._tracks(), "Blinding Lights", "The Weeknd", spotify_id="sp-not-in-catalog",
        )
        assert index == 1

    def test_no_spotify_id_behaves_as_before(self):
        assert resolve_external_track(self._tracks(), "Blinding Lights", "The Weeknd", spotify_id=None) == 1
