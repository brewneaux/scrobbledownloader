from scrobbledownload.database import get_session
from scrobbledownload.models import Artist as ArtistModel, ArtistGenre
from .spotify import Spotify


class Artist(object):
    """
    todo rename to add Service, docstrings
    """

    @classmethod
    def _create(cls, session, spotify_artist_id) -> ArtistModel:
        spotify_artist = Spotify.get_artist(spotify_artist_id)
        genres = [ArtistGenre(genre=x) for x in spotify_artist.genres]
        a = ArtistModel(
            name=spotify_artist.name,
            popularity=spotify_artist.popularity,
            spotify_id=spotify_artist.spotify_id,
            genres=genres,
        )
        session.add(a)
        session.commit()
        return a

    @classmethod
    def get_artist(cls, spotify_artist_id: str) -> ArtistModel:
        session = get_session()
        existing = session.query(ArtistModel).filter_by(spotify_id=spotify_artist_id).first()
        if existing:
            return existing
        else:
            return cls._create(session, spotify_artist_id)
