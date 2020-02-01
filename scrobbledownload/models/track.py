from scrobbledownload.services.spotify import Spotify
from scrobbledownload.services.genius import Genius
from sqlalchemy.orm import Session
from scrobbledownload.models.scrobbles import Scrobbles, ScrobbleTrack

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




