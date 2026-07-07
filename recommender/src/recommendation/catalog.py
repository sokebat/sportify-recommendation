"""
Catalog lookups that don't need a trained model: substring search, popularity
ranking, artist filtering, and resolving a free-text song name to a row in the
tracks table. Used directly by the /popularity, /artist and /search-songs
endpoints, and as a helper for the model-backed recommenders.
"""
import re

import pandas as pd

RESULT_COLUMNS = ["track_id", "track_name", "artists", "album_name", "track_genre", "popularity"]

# Qualifiers external sources append to titles that this catalog usually
# doesn't: "(feat. X)" / "[Remastered]" groups and " - Radio Edit" suffixes.
_TITLE_QUALIFIERS = re.compile(r"\s*[(\[][^)\]]*[)\]]")

# Collaboration separators in external artist credits; the catalog's `artists`
# column joins collaborators with ";" and is matched by substring, so the
# first credited artist alone is the reliable key.
_ARTIST_SEPARATORS = re.compile(r"\s+feat\.?\s+|\s+featuring\s+|\s+ft\.?\s+|\s+&\s+|\s+x\s+|,|;", flags=re.IGNORECASE)


def normalize_title(title: str) -> str:
    """Strips featuring credits and version qualifiers so externally sourced
    titles can hit the catalog, e.g. 'Levitating (feat. DaBaby)' ->
    'Levitating', 'Blinding Lights - Radio Edit' -> 'Blinding Lights'."""
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
    """Bridges an externally sourced (track, artist) pair - e.g. a Spotify
    trending entry - to a catalog `content_index`. When `spotify_id` is given,
    tries an exact match against the catalog's own track_id first (the local
    dataset's track_ids are themselves real Spotify IDs, so this is a cheap,
    reliable hit whenever the track happens to be in the older static
    dataset); otherwise falls back to progressively looser normalizations of
    the title and artist. Deliberately never matches on title alone: an
    unrelated same-titled cover would silently become the model seed."""
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
