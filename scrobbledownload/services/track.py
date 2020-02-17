import hashlib

from sqlalchemy.orm import Session

from scrobbledownload import models
from scrobbledownload.models.scrobbles import ScrobbleTrack
from scrobbledownload.services import Artist, Album
from scrobbledownload.services.genius import Genius
from scrobbledownload.services.spotify import Spotify


class TrackFactory(object):
    _spotify_svc: Spotify = None
    _genius_svc: Genius = None


class Track(object):
    """
    todo rename to add Service
    """
    _session: Session
    _scrobble: ScrobbleTrack
    _artist: models.Artist
    _album: models.Album
    _track: models.Track

    @classmethod
    def get_track(cls, session: Session, track_name: str, track_artist: str, track_album: str) -> models.Track:
        """
        Create a Track object, which either loads from the database and returns a model.Track, or builds itself out of
        API calls.

        I think, technically, name/album/artist is not enough to totally get unique by track, but i have a feeling
        LastFM doesn't really do much better than that, and the occurance of mis-matches is probably going to be
        insanely low.

        Args:
            session (sqlalchemy.orm.Session):
            track_name (str): The name of the track
            track_artist (str): The Track artist
            track_album (str): The track album

        Returns:
            models.Track
        """
        _t = cls(session, track_name, track_artist, track_album)
        return _t.get_model_object()

    def __init__(self, session: Session, track_name: str, track_artist: str, track_album: str, mbid: str):
        """
        Create a Track object, which either loads from the database and returns a model.Track, or builds itself out of
        API calls.

        I think, technically, name/album/artist is not enough to totally get unique by track, but i have a feeling
        LastFM doesn't really do much better than that, and the occurance of mis-matches is probably going to be
        insanely low.

        Args:
            session (Session):
            track_name (str): The name of the track
            track_artist (str): The Track artist
            track_album (str): The track album
        """
        self._session = session
        self._track_name = track_name
        self._track_artist = track_artist
        self._track_album = track_album
        self._mbid = mbid

    def _build_from_scratch(self) -> models.Track:
        """
        Build a track out of the resutls of Spotify, etc

        todo genius

        Returns:
            models.Track
        """
        spotify_track = Spotify.get_track(track_name=self._track_name, track_artist=self._track_artist)
        artist = Artist.get_artist(spotify_track.artist_id)
        album = Album.get_album(spotify_track.album_id)

        track = models.Track(
            name=spotify_track.name,
            spotify_id=spotify_track.spotify_id,
            mbid=self._mbid,
            generated_id=self.hash,
            artist=artist,
            album=album
        )
        self._session.add(track)
        self._session.commit()
        return track

    def get_model_object(self) -> models.Track:
        """
        Get the Track model object, creating it if it doesn't exist
        Returns:
            models.Track
        """
        existing = self._session.query(models.Track).filter_by(generated_id=self.hash).first()
        if existing:
            return existing
        return self._build_from_scratch()

    @property
    def hash(self) -> str:
        """
        A hash specific for this track - mbid is pretty unreliable, and I don't want to hit the Spotify and Genius APIs
        any more than I have to.
        Returns:
            str
        """
        return hashlib.sha1(
            f"{self._track_name} - {self._track_artist} on {self._track_album}".encode()
        ).hexdigest()
