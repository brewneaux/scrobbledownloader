from scrobbledownload.secrets import Secrets
from spotipy import Spotify as _Spotify
from typing import List
from dataclasses import dataclass

class SpotifyNotFoundExcecption(BaseException):
    pass



class Spotify(object):
    def __init__(self, secrets: Secrets):
        self.sp = _Spotify(secrets.spotify_credentials)

    def get_artist(self, artist_name):
        """
        Get artist information from the Spotify API
        Args:
            artist_name (str): The artist name to search for

        Returns:
            unk
        """
        results = self.sp.search(q=f'artist: {artist_name}', type='artist')
        artist_response = results.get('artists', {}).get('items')
        if not artist_response:
            raise SpotifyNotFoundExcecption(f"Artist {artist_name} not found")
        return SpotifyArtist(
            id=artist_response[0]['id'],
            name=artist_response[0]['name'],
            genres=artist_response[0]['genres'],
            popularity=artist_response[0]['popularity']
        )