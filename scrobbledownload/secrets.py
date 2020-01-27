from dataclasses import dataclass
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os

spotify_creds = None

secrets_path = None


def set_secrets_path(path):
    global secrets_path
    secrets_path = path


def load_secrets():
    if not os.path.exists(secrets_path):
        raise FileNotFoundError(f"Configuration file was missing - it was not found at {secrets_path}")
    with open(secrets_path) as fh:
        secrets_json = json.load(fh)
        secrets = Secrets(
            lastfm_api_key=secrets_json['lastfm_api_key'],
            lastfm_api_secret=secrets_json['lastfm_api_secret'],
            lastfm_username=secrets_json['lastfm_username'],
            spotify_client_id=secrets_json['spotify_client_id'],
            spotify_client_secret=secrets_json['spotify_client_secret'],
            scrobbles_per_page=secrets_json['scrobbles_per_page'],
            db_connection_string=secrets_json['db_connection_string']
        )
    return secrets


def get_spotify_creds(secrets):
    global spotify_creds
    spotify_creds = SpotifyClientCredentials(secrets.spotify_client_id, secrets.spotify_client_secret)


@dataclass
class Secrets(object):
    lastfm_api_key: str
    lastfm_api_secret: str
    lastfm_username: str
    spotify_client_id: str
    spotify_client_secret: str
    scrobbles_per_page: int
    db_connection_string: str
