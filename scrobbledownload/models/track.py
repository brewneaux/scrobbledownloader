from scrobbledownload.models import (
    Track,
    Artist,
    ArtistGenre,
    Album,
    AlbumGenre,
)
from scrobbledownload.services.spotify import Spotify
from scrobbledownload.services.genius import Genius
from sqlalchemy.orm import Session
from scrobbledownload.models.scrobbles import Scrobbles, ScrobbleTrack
import hashlib


class TrackFactory(object):
    _spotify_svc: Spotify = None
    _genius_svc: Genius = None


class Track(object):
    _session: Session
    _scrobble: ScrobbleTrack
    _spotify_service: Spotify
    _genius_service: Genius

    def __init__(self, scrobble: ScrobbleTrack, session: Session, spotify_service, genius_service: Genius):
        """
        todo: actual docs

        This model should:
            -a handle edgecases for track/album/artist name from something?
            - get the track information from the Spotify API
            - save itself


        todo:
            - if the track exists in the database, return it
            - if the track doesnt exist in the database
                - lookup the track from Spotify, get the SpotifyTrack
                -

        Args:
            spotify_service:
            genius_service:
        """
        self._session = session
        self._scrobble_track = scrobble
        self._spotify_service = spotify_service
        self._genius_service = genius_service

    @property
    def listen_datetime(self):
        return self._scrobble_track.listen_dt

    @property
    def hash(self) -> str:
        """
        A hash specific for this track - mbid is pretty unreliable, and I don't want to hit the Spotify and Genius APIs
        any more than I have to.
        Returns:
            str
        """
        return hashlib.sha1(
            f"{self._scrobble_track.track_name} - {self._scrobble_track.artist} on {self._scrobble_track.album}".encode()
        ).hexdigest()

