"""
Secrets that are loaded from a configuration file
"""
from os.path import exists

import yaml
from spotipy.oauth2 import SpotifyClientCredentials


class Secrets(object):
    _required_keys = [
        "lastfm_api_key",
        "lastfm_api_secret",
        "lastfm_username",
        "spotify_client_id",
        "spotify_client_secret",
        "scrobbles_per_page",
        "db_connection_string",
    ]

    _path: str = None
    _dict: dict = None
    lastfm_api_key: str
    lastfm_api_secret: str
    lastfm_username: str
    spotify_client_id: str
    spotify_client_secret: str
    scrobbles_per_page: int
    db_connection_string: str

    def __init__(self):
        """
        Secrets object - holds all the keys and settings that are necessary for interacting with the APIs
        """
        self._dict = self.load()
        self.validate()
        self.lastfm_api_key = self._dict["lastfm_api_key"]
        self.lastfm_api_secret = self._dict["lastfm_api_secret"]
        self.lastfm_username = self._dict["lastfm_username"]
        self.spotify_client_id = self._dict["spotify_client_id"]
        self.spotify_client_secret = self._dict["spotify_client_secret"]
        self.scrobbles_per_page = self._dict["scrobbles_per_page"]
        self.db_connection_string = self._dict["db_connection_string"]

    def load(self) -> dict:
        """
        Load the configuration file and return the necessary variables
        """
        with open(self._path) as fh:
            config_contents = fh.read()
        return yaml.load(config_contents, Loader=yaml.SafeLoader)

    def validate(self):
        """
        Validates that all the necessary keys exist in the configuration file.
        """
        missing_keys = set(self._required_keys) - set(self._dict.keys())
        if missing_keys:
            raise KeyError(f"Configuration file did not contain all necessary keys - missing {missing_keys}")

    @property
    def spotify_credentials(self) -> SpotifyClientCredentials:
        """
        Get the Spotify credentials object that is requried for interaction with the Spotify API
        Returns:
            SpotifyClientCredentials
        """
        return SpotifyClientCredentials(self.spotify_client_id, self.spotify_client_secret)

    @classmethod
    def set_filepath(cls, path: str):
        """
        Set the filepath to the configuration file.  This must be called properly before the class can be initialized.
        Args:
            path (str): a path to the configuration file
        """
        if not exists(path):
            raise FileNotFoundError(f"Configuration file was missing - it was not found at {path}")
        cls._path = path
