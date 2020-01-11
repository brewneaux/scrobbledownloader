from dataclasses import dataclass
import json


def load_secrets():
    with open('/run/settings.json') as fh:
        secrets_json = json.load(fh)
        secrets = Secrets(
            lastfm_api_key=secrets_json['lastfm_api_key'],
            lastfm_api_secret=secrets_json['lastfm_api_secret'],
            lastfm_username=secrets_json['lastfm_username'],
            spotify_client_id=secrets_json['spotify_client_id'],
            spotify_client_secret=secrets_json['spotify_client_secret'],
            scrobbles_per_page=secrets_json['scrobbles_per_page']
        )
    return secrets

class Secrets(object):
    lastfm_api_key: str
    lastfm_api_secret: str
    lastfm_username: str
    spotify_client_id: str
    spotify_client_secret: str
    scrobbles_per_page: int

