"""
Catalog lookups that don't need a trained model: search, popularity
ranking, artist filtering, and matching a free-text song name to a row.
Used by /popularity, /artist, /search-songs, and by the other recommenders.
"""
import re

import pandas as pd

RESULT_COLUMNS = ["track_id", "track_name", "artists", "album_name", "track_genre", "popularity"]

# How many extra results to rank before deduping. Tracks repeat across
# genre splits, so a plain top-N is often mostly the same song.
POOL_MULTIPLIER = 5

# Strips things like "(feat. X)", "[Remastered]", or " - Radio Edit"
# that external sources add but our catalog usually doesn't have.
_TITLE_QUALIFIERS = re.compile(r"\s*[(\[][^)\]]*[)\]]")

# Splits multi-artist credits like "feat.", "&", "x", ",". Our catalog
# only reliably matches on the first artist.
_ARTIST_SEPARATORS = re.compile(r"\s+feat\.?\s+|\s+featuring\s+|\s+ft\.?\s+|\s+&\s+|\s+x\s+|,|;", flags=re.IGNORECASE)


def normalize_title(title: str) -> str:
    """Strips featuring credits and version tags so external titles can
    match the catalog, e.g. 'Levitating (feat. DaBaby)' -> 'Levitating'."""
    cleaned = _TITLE_QUALIFIERS.sub("", title)
    cleaned = cleaned.split(" - ")[0]
    return cleaned.strip()


def normalize_artist(artist: str) -> str:
    """First credited artist from an external credit string, e.g.
    'Dua Lipa feat. DaBaby' -> 'Dua Lipa', 'Silk Sonic, Bruno Mars' -> 'Silk Sonic'."""
    return _ARTIST_SEPARATORS.split(artist)[0].strip()


def resolve_external_track(
    tracks: pd.DataFrame, track_name: str, artist: str, spotify_id: str | None = None,
) -> int | None:
    """Matches an external (track, artist) pair to a catalog `content_index`.
    Tries an exact spotify_id match first, then looser title/artist matches.
    Never matches on title alone - a cover with the same name could get
    picked as the seed by mistake."""
    if spotify_id:
        matches = tracks[tracks["track_id"] == spotify_id]
        if not matches.empty:
            return int(matches.iloc[0]["content_index"])

    titles = [track_name]
    if normalize_title(track_name) not in titles:
        titles.append(normalize_title(track_name))
    artists = [artist]
    if normalize_artist(artist) not in artists:
        artists.append(normalize_artist(artist))

    for candidate_artist in artists:
        for candidate_title in titles:
            index = find_track_index(tracks, candidate_title, candidate_artist)
            if index is not None:
                return index
    return None


def dedupe_by_track(ranked: pd.DataFrame, limit: int) -> pd.DataFrame:
    """Drops duplicate rows for the same title/artist, keeping the
    best-ranked one. `ranked` must already be sorted best-first."""
    return ranked.drop_duplicates(subset=["track_name", "artists"]).head(limit)


def finalize_results(tracks: pd.DataFrame, ranked_indices, top_n: int) -> pd.DataFrame:
    """Last step for the ranked recommenders: picks the result columns,
    dedupes, and resets the index."""
    ranked = tracks.loc[ranked_indices, RESULT_COLUMNS]
    return dedupe_by_track(ranked, top_n).reset_index(drop=True)


def top_candidate_indices(candidate_indices, scores, top_n: int):
    """Sorts candidates by score, best first, and keeps the top
    `top_n * POOL_MULTIPLIER`."""
    ranked_order = scores.argsort()[::-1][: top_n * POOL_MULTIPLIER]
    return candidate_indices[ranked_order]


def seed_duplicate_mask(tracks: pd.DataFrame, query_index: int) -> pd.Series:
    """Marks rows that are duplicates of the seed track (same title +
    artist, different genre split), so the seed can't get recommended as
    itself."""
    query_name = tracks.loc[query_index, "track_name"]
    query_artists = tracks.loc[query_index, "artists"]
    return (tracks["track_name"] == query_name) & (tracks["artists"] == query_artists)


def find_track_index(tracks: pd.DataFrame, track_name: str, artist: str | None = None) -> int | None:
    """Finds the most popular row matching `track_name` (case-insensitive),
    optionally narrowed by `artist`. Picks the most popular match instead of
    just the first row, since titles repeat across unrelated covers."""
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
