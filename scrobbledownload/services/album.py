from scrobbledownload.models import Album as AlbumModel, AlbumGenre
from .spotify import Spotify
from scrobbledownload.database import get_session


class Album(object):
    """
    todo rename to add Service, docstrings
    """
    @classmethod
    def _create(cls, session, spotify_album_id) -> AlbumModel:
        spotify_album = Spotify.get_album(spotify_album_id)
        genres = [AlbumGenre(genre=x) for x in spotify_album.genres]
        a = AlbumModel(
            name=spotify_album.name,
            popularity=spotify_album.popularity,
            spotify_id=spotify_album.spotify_id,
            genres=genres
        )
        session.add(a)
        session.commit()
        return a

    @classmethod
    def get_album(cls, spotify_album_id: str) -> AlbumModel:
        session = get_session()
        existing = session.query(AlbumModel).filter_by(spotify_id=spotify_album_id).first()
        if existing:
            return existing
        else:
            return cls._create(session, spotify_album_id)
