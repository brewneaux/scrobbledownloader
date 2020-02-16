from scrobbledownload.secrets import Secrets
from spotipy import Spotify as _Spotify
from typing import List
from dataclasses import dataclass
from spotipy.oauth2 import SpotifyClientCredentials
from scrobbledownload.models.spotify_models import SpotifyArtist, SpotifyAlbum, SpotifyTrack
import os
import yaml
from typing import Dict
import string


class SpotifyNotFoundExcecption(BaseException):
    pass


class Spotify(object):
    """
    todo rename to add Service
    """
    _creds: SpotifyClientCredentials
    _spotify_api: _Spotify
    _replacements: Dict[str, str]

    @classmethod
    def set_replacements(cls, path):
        """
        Set the replacements for weirdo edgecases.
        Args:
            path (str): a path to the configuration file
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Edge case replacements file was missing - it was not found at {path}")
        with open(path) as fh:
            cls._replacements = yaml.load(fh, Loader=yaml.SafeLoader)

    @classmethod
    def connect(cls, creds: SpotifyClientCredentials):
        """
        Set up the Spotify API connection
        Args:
            creds (SpotifyClientCredentials): the client creds for connecting to Spotify
        """
        cls._creds = creds
        cls._spotify_api = _Spotify(creds)

    @classmethod
    def get_artist(cls, artist_id) -> SpotifyArtist:
        """
        Get a spotify artist object using Spotipy.  Spotipy just returns a dict, so we turn it into an object here.
        Args:
            artist_id (str): The spotify ID for the artist

        Returns:
            SpotifyArtist
        """
        a = cls._spotify_api.artist(artist_id)
        return SpotifyArtist(
            name=a['name'],
            spotify_id=artist_id,
            genres=a['genres'],
            popularity=a.get('popularity')
        )

    @classmethod
    def get_album(cls, album_id) -> SpotifyAlbum:
        """
        Get a spotify album object using Spotipy.  Spotipy just returns a dict, so we turn it into an object here.
        Args:
            album_id (str): The spotify ID for the album

        Returns:
            SpotifyAlbum
        """
        a = cls._spotify_api.album(album_id)
        return SpotifyAlbum(
            name=a['name'],
            spotify_id=a['id'],
            release_date_str=a['release_date'],
            release_date_precision=a['release_date_precision'],
            genres=a['genres'],
            popularity=a['popularity']
        )

    @classmethod
    def handle_replacements(self, input_str: str) -> str:
        """
        If an edge-case replacement exists, return the replacement, else just the string
        Args:
            input_str (str):

        Returns:
            str
        """
        return self._replacements.get(input_str, input_str)

    @staticmethod
    def to_alphanum(s: str) -> str:
        """u
        Translate a string to alpha-numeric only
        Args:
            s (str): an input string to translate

        Returns:
            str
        """
        return s.translate(str.maketrans("", "", string.punctuation))

    @classmethod
    def _handle_spotify_track_response(cls, response) -> List[SpotifyTrack]:
        """
        Parse a Spotify track search response into SpotifyTracks
        Args:
            response (dict): The dict of results from spotify

        Returns:
            List(SpotifyTracks)
        """
        results = []
        for track in response['tracks']['items']:
            # name: str
            # spotify_id: str
            # duration_ms: int
            # popularity: int
            # album_id: str
            # artist_id: str

            results.append(SpotifyTrack(
                name=track['name'],
                spotify_id=track['id'],
                duration_ms=track['duration_ms'],
                popularity=track['popularity'],
                album_id=track['album']['id'],
                artist_id=track['artists'][0]
            ))
        return results

    @classmethod
    def _make_track_query(cls, track_name, track_artist):
        """
        Makes a query to the Spotify API
        Args:
            track_name (str):
            track_artist (str):

        Returns:
            SpotifyTrack
        """
        search_string = f"{track_name} artist:{track_artist}"
        response = cls._spotify_api.search(q=search_string, type="track")
        return cls._handle_spotify_track_response(response)

    @classmethod
    def get_track(cls, track_name: str, track_artist: str) -> SpotifyTrack:
        """
        Use Spotipy search to find a track from the Spotify API.

        This method has a little bit of extra magic that has to happen, due to some differences between the LastFM and
        Spotify track/artist/ablum names, punctuation, etc.

        Args:
            track_name (str): Name of the track
            track_artist (str): Name of the artist

        Returns:
            SpotifyTrack
        """
        track_artist = cls.handle_replacements(cls.to_alphanum(track_artist))
        track_name_words = [cls.handle_replacements(cls.to_alphanum(word)) for word in reversed(track_name.split())]

        results = cls._make_track_query(' '.join(reversed(track_name_words)), track_artist)

        while track_name_words and not len(results):
            track_name_words.pop()
            search_string_track_name = " ".join(list(reversed(track_name_words)))
            results = cls._make_track_query(search_string_track_name, track_artist)

        if not results:
            raise SpotifyNotFoundExcecption(f"Unable to find {track_name} by {track_artist}")
        return results[0]
