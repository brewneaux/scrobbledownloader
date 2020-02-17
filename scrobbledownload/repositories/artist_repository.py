from sqlalchemy.orm import Session

from scrobbledownload.models import Artist, ArtistGenre
from scrobbledownload.services import Spotify


class ArtistRepository(object):
    @classmethod
    def get_artist(cls, artist_name: str, session: Session, spotify_svc: Spotify) -> Artist:
        """
        Gets an Artist object from the database or creates one.
        Args:
            artist_name (str): - The artists name
            session (Session): A sqlalchemy session
            spotify_svc (spotify): The Spotify service

        Returns:
            Artist
        """
        search = Artist.get_by_name(artist_name, session)
        if search:
            return search
        return cls._create_artist(artist_name, spotify_svc)

    @classmethod
    def _create_artist(cls, artist_name: str, spotify_svc: Spotify) -> Artist:
        """
        Create a non-existent artist
        Args:
            artist_name (str): - The artists name
            session (Session): A sqlalchemy session
            spotify_svc (spotify): The Spotify service

        Returns:
            Artist
        """
        spotify_artist = spotify_svc.get_artist(artist_name)
        genres = [ArtistGenre(genre=x) for x in spotify_artist.genres]
        a = Artist(
            name=spotify_artist.name,
            popularity=spotify_artist.popularity,
            spotify_id=spotify_artist.id,
            genres=genres
        )
        return a
