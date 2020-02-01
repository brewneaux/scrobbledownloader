"""
All classes responsible for scrobble information

TODO reorganize this class
"""
import requests
from dataclasses import dataclass
from datetime import datetime
from dateutil.parser import parse
from typing import List
from scrobbledownload.secrets import Secrets


@dataclass
class ScrobbleTrack(object):
    """
    A single Scrobble Track
    """
    track_name: str
    track_mbid: str
    listen_dt: datetime
    artist: str
    artist_mbid: str
    album: str
    album_mbid: str


@dataclass
class Scrobbles(object):
    """
    A collection of scrobble responses
    """

    page: int
    perPage: int
    totalPages: int
    tracks: List[ScrobbleTrack]


class ScrobbleDownloader(object):
    """
    Downloads scrobbles from lastfm.

    todo prob rename this to be something closer to LastfmApi or something
    """

    def __init__(self, secrets: Secrets):
        """Get scrobbles
        
        Args:
            secrets (scrobbledownload.secrets.Secrets): the secrets class
        """
        self.secrets = secrets

    def get(self, page: int = 1) -> Scrobbles:
        """Get scrobbles by page
        
        Args:
            page (int, optional): what page we're gettin. Defaults to 1.
        
        Returns:
            Scrobbles: the scrobbles
        """
        url = (
            f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&"
            f"user={self.secrets.lastfm_username}&api_key={self.secrets.lastfm_api_key}"
            f"&format=json&limit={self.secrets.scrobbles_per_page}&page={page}"
        )
        req = requests.get(url)
        req.raise_for_status()
        scrobble_json = req.json()
        tracks = ScrobbleDownloader._get_tracks(scrobble_json["recenttracks"]["track"])
        return Scrobbles(
            page=scrobble_json["recenttracks"]["@attr"]["page"],
            perPage=scrobble_json["recenttracks"]["@attr"]["perPage"],
            totalPages=scrobble_json["recenttracks"]["@attr"]["totalPages"],
            tracks=tracks,
        )

    @staticmethod
    def _get_tracks(tracks_json) -> List[ScrobbleTrack]:
        """
        Parses the JSON-decoded object for track objects.
        Args:
            tracks_json (list): a decoded JSON list of objects

        Returns:
            list(ScrobbleTrack)
        """
        tracks = []
        for t in tracks_json:
            tracks.append(
                ScrobbleTrack(
                    track_name=t["name"],
                    track_mbid=t["mbid"],
                    date=parse(t["date"]["#text"]),
                    artist=t["artist"]["#text"],
                    artist_mbid=t["artist"]["mbid"],
                    album=t["album"]["#text"],
                    album_mbid=t["album"]["mbid"],
                )
            )
        return tracks
