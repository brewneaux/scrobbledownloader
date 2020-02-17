import logging
from typing import List

from sqlalchemy.orm import Session

from scrobbledownload.models import Listen
from scrobbledownload.models.scrobbles import ScrobbleTrack
from scrobbledownload.secrets import Secrets
from scrobbledownload.services import LastFM, Genius, Spotify
from scrobbledownload.services.track import Track


class ListenRepository(object):
    def __init__(self, username: str, session: Session, secrets: Secrets):
        self._username = username
        self._session = session
        self._scrobbles_per_page = secrets.scrobbles_per_page
        self._lastfm_service = LastFM(username, secrets.lastfm_api_key)
        self._genius_service = Genius()
        self._spotify_servie = Spotify()

    def retrieve_and_store_tracks(self) -> List[Track]:
        """
        Retrieve track objects using the LastFM service to download bare scrobbles, and then populate a list of Track
        objects.  Handles looping over the scrobbles to retrieve what is necessary, page over page, until we run out
        of data, or we are caught up to the last listen contained in the database.

        Returns:
            list(Track)
        """
        last_downloaded = Listen.get_last_listen(self._session)
        logging.getLogger(__name__).info(f"Downloading scrobbles from now back to {last_downloaded}")
        #
        # page = 1

        while True:
            scrobbles = self._lastfm_service.download_scrobbles(1, self._scrobbles_per_page)
            tracks = self._get_track_objects(scrobbles.tracks)
            for t in tracks:
                if t.listen_datetime < last_downloaded:
                    break
        pass

    def _get_track_objects(self, scrobbles: List[ScrobbleTrack]) -> List[Track]:
        """
        Process a list of ScrobbleTracks, getting track objects for them
        Args:
            scrobbles (list(ScrobbleTrack)): A list of ScrobbleTrack objects

        Returns:
            list(Track)
        """
        tracks = []
        for scrobble in scrobbles:
            tracks.append(Track(scrobble, self._spotify_servie, self._genius_service))
        return tracks
