from dataclasses import dataclass
from datetime import date
from typing import List

from dateutil.parser import parse


@dataclass
class SpotifyArtist(object):
    """
    Representation of an artist from the Spotify API
    """

    name: str
    spotify_id: str
    genres: List[str]
    popularity: int


@dataclass
class SpotifyAlbum(object):
    """
    Representation of an album from the Spotify API
    """

    name: str
    spotify_id: str
    release_date_str: str
    release_date_precision: str
    genres: List[str]
    popularity: int

    @property
    def release_date(self) -> date:
        dt = parse(self.release_date_str).date()
        if self.release_date_precision == "year":
            return dt.replace(month=1, day=1)
        if self.release_date_precision == "month":
            return dt.replace(day=1)
        if self.release_date_precision == "day":
            return dt


@dataclass
class SpotifyTrack(object):
    """
    Representation of a track from the Spotify API
    """

    name: str
    spotify_id: str
    duration_ms: int
    popularity: int
    album_id: str
    artist_id: str
