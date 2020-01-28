import hashlib
import logging
import string
from sqlalchemy.orm import Session
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Optional, List
from dateutil.parser import parse
from spotipy import Spotify
from datetime import date

from scrobbledownload.models import (
    Track,
    Artist,
    ArtistGenre,
    Album,
    AlbumGenre,
)

logger = logging.getLogger(__name__)


def to_alphanum(s: str) -> str:
    """u
    Translate a string to alpha-numeric only
    Args:
        s (str): an input string to translate

    Returns:
        str
    """
    return s.translate(str.maketrans("", "", string.punctuation))


# TODO move edge cases to config?
edge_cases = {
    "The AllAmerican Rejects": "The All American Rejects",
    "blink182": "blink-182",
    "3OH3": "3OH!3",
    "The Kodan Armada": "Kodan Armada",
    "Pg99": "Pageninetynine",
    "Combatwoundedveteran": "Combat wounded veteran",
    "The Pack AD": "The pack a.d.",
    "Angel Dut": "Angel Du$t",
}


def fix_weird_edgecase(artist: str) -> str:
    """
    Looks up Artist edgecases, and returns the 'fixed' version.  LastFM sometimes has Arists listed differently than Spotify.
    Args:
        artist (str):

    Returns:
        str
    """
    return edge_cases.get(artist, artist)


def parse_date(date: str, precision: str) -> date:
    """
    Parse a date string from lastfm into a datetime object.
    Args:
        date (str): The input string
        precision (str): The precision identifier given by the API

    Returns:
        date
    """
    dt = parse(date).date()
    if precision == "year":
        return dt.replace(month=1, day=1)
    if precision == "month":
        return dt.replace(day=1)
    if precision == "day":
        return dt


class TrackNotFoundError(Exception):
    pass


class TrackMetadata(object):
    def __init__(self, track_name: str, track_artist: str, track_album: str, mbid: Optional[str], session: Session, spotify_credentials: SpotifyClientCredentials):
        """
        Get or create all of a tracks objects to be stored in the database
        Args:
            track_name (str): The name of the track
            track_artist (str): The artist
            track_album (str): The album
            mbid (str): The mbid - MusicBrainz ID - a UUID that is unique to this track
            session (Session): SQLAlchemy Session
            spotify_credentials (SpotifyClientCredentials): Credentials for the Spotify API
        """
        self.session = session
        self.ccm = spotify_credentials
        self.sp = Spotify(client_credentials_manager=self.ccm)
        self.track_name = fix_weird_edgecase(to_alphanum(track_name))
        self.track_artist = fix_weird_edgecase(to_alphanum(track_artist))
        self.track_album = fix_weird_edgecase(to_alphanum(track_album))
        self.mbid = mbid

    @property
    def hash(self) -> str:
        """
        Generate our own internal hash for this track - used if there is no mbid asssciated to this track
        Returns:
            str
        """
        return hashlib.sha1(
            f"{self.track_name} - {self.track_artist} on {self.track_album}".encode()
        ).hexdigest()

    def get_track_result_from_spotify(self) -> dict:
        """
        Retrieves a track from the spotify API.  This does a little bit of cleverness in removing words from the track name if it can't find a match.

        When I first implemented this, I was finding that some spelling differences made it difficult to find the exact track.
        I did some testing and found that it would usually find the right thing if you started chopping off words.  It
        didnt seem to every find the _wrong_ thing, so I went with it.

        Returns:
            dict
        """
        search_string = f"{self.track_name} artist:{self.track_artist}"

        logger.debug(f"Quering spotify api for {search_string}")
        tracks = self.sp.search(q=search_string, type="track")
        track_name_words = list(reversed(self.track_name.split()))

        results_count = len(tracks["tracks"]["items"])
        logger.debug(f"loop stuff: {track_name_words}, {results_count}")

        while track_name_words and not len(tracks["tracks"]["items"]):
            track_name_words.pop()
            search_string_track_name = " ".join(list(reversed(track_name_words)))
            search_string = f"{search_string_track_name} artist:{self.track_artist}"
            logger.debug(f"Quering spotify api for {search_string}")
            tracks = self.sp.search(q=search_string, type="track")

        try:
            track_json = tracks["tracks"]["items"][0]
        except Exception:
            logger.debug(f"Cant find {self.track_artist} - {self.track_name}")
            raise TrackNotFoundError(f"Cant find {self.track_artist} - {self.track_name}")
        return track_json

    def get_or_create_track(self) -> Track:
        """
        Gets or creates a track object from the database
        Returns:
            Track
        """
        logger.info(
            f"Creating TrackMetadata object for name: {self.track_name} by {self.track_artist} on {self.track_album}"
        )
        result = self.session.query(Track).filter_by(mbid=self.mbid).first()
        if result:
            return result

        track_json = self.get_track_result_from_spotify()

        artist = self.get_or_create_artist(track_json["artists"][0]["id"])
        album = self.get_or_create_album(track_json["album"]["id"])
        track = Track(
            name=self.track_name,
            spotify_id=track_json["id"],
            mbid=self.mbid or self.hash,
            artist=artist,
            album=album,
        )
        return track

    def get_or_create_artist(self, artist_id: str) -> Artist:
        """
        Get or create an Artist object
        Args:
            artist_id (str):  The Spotify Artist ID

        Returns:

        """
        result = self.session.query(Artist).filter_by(spotify_id=artist_id).first()
        if result:
            logger.debug(f"Retrieved Artist object for {self.track_artist}")
            return result

        logger.debug(f"Building Artist object for {self.track_artist}")

        artist = self.sp.artist(artist_id)
        genres = [ArtistGenre(genre=x) for x in artist["genres"]]
        a = Artist(
            name=artist["name"], popularity=artist["popularity"], spotify_id=artist["id"], genres=genres,
        )
        return a

    def get_or_create_album(self, album_id: str) -> Album:
        """
        Get or create an Album object
        Args:
            album_id (str): The Spotify album ID

        Returns:
            Album
        """
        result = self.session.query(Album).filter_by(spotify_id=album_id).first()
        if result:
            logger.debug(f"Retrieved existing Album object for {self.track_album}")
            return result

        logger.debug(f"Building Album object for {self.track_album}")

        album = self.sp.album(album_id)
        genres = [AlbumGenre(genre=x) for x in album["genres"]]
        a = Album(
            name=album["name"],
            popularity=album["popularity"],
            spotify_id=album["id"],
            genres=genres,
            release_date=parse_date(album["release_date"], album["release_date_precision"]),
        )
        return a
