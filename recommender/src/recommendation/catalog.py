"""
Catalog lookups that don't need a trained model: substring search, popularity
ranking, artist filtering, and resolving a free-text song name to a row in the
tracks table. Used directly by the /popularity, /artist and /search-songs
endpoints, and as a helper for the model-backed recommenders.
"""
import pandas as pd

RESULT_COLUMNS = ["track_id", "track_name", "artists", "album_name", "track_genre", "popularity"]


def dedupe_by_track(ranked: pd.DataFrame, limit: int) -> pd.DataFrame:
    """Collapses duplicate catalog rows for the same title/artist - this
    dataset repeats popular tracks across multiple genre splits, so an
    unfiltered top-N can otherwise show the same song several times. Assumes
    `ranked` is already sorted best-first; keeps each track's best-ranked row."""
    return ranked.drop_duplicates(subset=["track_name", "artists"]).head(limit)


def find_track_index(tracks: pd.DataFrame, track_name: str, artist: str | None = None) -> int | None:
    """Most popular catalog row matching `track_name` (case-insensitive),
    optionally narrowed to artists containing `artist`. Mirrors how a
    listener would type a title into the search box, not an exact-key
    lookup - and picking the most popular match (rather than just whichever
    row the CSV happens to list first) matters because this dataset repeats
    common titles across many unrelated cover versions/genre splits, e.g.
    "Blinding Lights" also exists as a kids'-compilation cover."""
    matches = tracks[tracks["track_name"].str.lower() == track_name.lower()]
    if artist:
        matches = matches[matches["artists"].str.lower().str.contains(artist.lower(), na=False)]
    if matches.empty:
        return None
    return int(matches.sort_values("popularity", ascending=False).iloc[0]["content_index"])


def search_songs(tracks: pd.DataFrame, query: str, limit: int = 10) -> pd.DataFrame:
    """Case-insensitive substring search over track name and artist."""
    if not query.strip():
        return tracks.iloc[0:0][RESULT_COLUMNS]

    q = query.lower()
    mask = (
        tracks["track_name"].str.lower().str.contains(q, na=False)
        | tracks["artists"].str.lower().str.contains(q, na=False)
    )
    ranked = tracks[mask][RESULT_COLUMNS].sort_values("popularity", ascending=False)
    return dedupe_by_track(ranked, limit).reset_index(drop=True)


def popular_songs(tracks: pd.DataFrame, genre: str | None = None, limit: int = 10) -> pd.DataFrame:
    """Most popular tracks in the catalog, optionally restricted to a genre."""
    candidates = tracks
    if genre:
        candidates = candidates[candidates["track_genre"].str.contains(genre, case=False, na=False)]
    ranked = candidates[RESULT_COLUMNS].sort_values("popularity", ascending=False)
    return dedupe_by_track(ranked, limit).reset_index(drop=True)


def songs_by_artist(tracks: pd.DataFrame, artist: str, limit: int = 10) -> pd.DataFrame:
    """Most popular tracks by an artist (substring match - `artists` can hold
    multiple collaborators joined by `;`)."""
    matches = tracks[tracks["artists"].str.lower().str.contains(artist.lower(), na=False)]
    ranked = matches[RESULT_COLUMNS].sort_values("popularity", ascending=False)
    return dedupe_by_track(ranked, limit).reset_index(drop=True)
