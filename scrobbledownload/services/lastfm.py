import requests
from typing import List
from scrobbledownload.models.scrobbles import ScrobbleTrack, Scrobbles
from dateutil.parser import parse
import logging


class LastFM(object):
    """
    Interactions with the Last.fm API, where we download a users listened tracks.
    """

    def __init__(self, username: str, api_key: str):
        """
        Initialize with the username, since this interacts only with a specific users information, and the API key
        for the API.
        Args:
            username:
            api_key:
        """
        self._username = username
        self._api_key = api_key

    def download_scrobbles(self, page: int, scrobbles_per_page: int = 1000) -> Scrobbles:
        """
        Download a list of scrobbles - that is, individual listens to a specific track as defined by Last.fm. This uses
        the LastFM user.getrecenttracks api method as documented here: https://www.last.fm/api/show/user.getRecentTracks

        Returned is a Scrobbles object, which represents some metadata about this response, as well as a list of the
        tracks themselves.
        Args:
            page (int): What page of scrobbles to gather.  The Last.fm API works from most recent backwards, so as you
                loop through pages, you move backwards in time
            scrobbles_per_page (int): how many scrobbles, per page, we are going to retrieve.  According to the
                docs, you are allowed a maximum of 200 tracks per request, but 1000 definitely works.

        Returns:
            Scrobbles
        """
        url = (
            f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&"
            f"user={self._username}&api_key={self._api_key}"
            f"&format=json&limit={scrobbles_per_page}&page={page}"
        )
        req = requests.get(url)
        req.raise_for_status()
        scrobble_json = req.json()
        scrobbles = LastFM._handle_lastfm_response(scrobble_json)
        logging.getLogger(__name__).info(f"Retrieved {len(scrobbles.tracks)} from LastFM API on page {page} of {scrobbles.totalPages}")
        return scrobbles

    @staticmethod
    def _handle_lastfm_response(resp: dict) -> Scrobbles:
        """
        Parse the response dict from user.getRecentTracks into an object
        Args:
            resp (dict): the JSON-decoded response from user.getRecentTracks

        Returns:
            Scrobbles
        """
        recent_tracks_attr = resp['recenttracks']['@attr']
        tracks = LastFM._get_tracks(resp['recenttracks']['track'])
        return Scrobbles(
            page=recent_tracks_attr["page"],
            perPage=recent_tracks_attr["perPage"],
            totalPages=recent_tracks_attr["totalPages"],
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
            if t.get('@attr', {}).get('nowplaying'):
                continue
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
