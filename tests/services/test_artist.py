from unittest import TestCase
from unittest.mock import MagicMock, patch
from scrobbledownload.services.artist import Artist
from scrobbledownload.models import Artist as ArtistModel
from scrobbledownload.models import create_all
from scrobbledownload.models.spotify_models import SpotifyArtist
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class TestArtist(TestCase):
    @patch('scrobbledownload.services.artist.get_session')
    def test_get_artist_exists(self, mock_get_session):
        session = MagicMock()
        mock_get_session.return_value = session
        expected = ArtistModel(
            name='test artist',
            spotify_id='test id',
            popularity=19)

        # Mock the return of the SQLAlchemy query for unit tests.
        session.query.return_value.filter_by.return_value.first.return_value = expected
        actual = Artist.get_artist('test_id')
        assert actual == expected

    @patch.object(Artist, '_create')
    @patch('scrobbledownload.services.artist.get_session')
    def test_get_artist_doesnt_exist(self, mock_get_session, mock_create):
        session = MagicMock()
        mock_get_session.return_value = session
        session.query.return_value.filter_by.return_value.first.return_value = False

        actual = Artist.get_artist('test_id')
        mock_create.assert_called()

    @patch('scrobbledownload.services.artist.Spotify')
    def test_create(self, mock_spotify):
        session = MagicMock()
        mock_spotify.get_artist.return_value = SpotifyArtist(
            name='test artist',
            spotify_id='testid',
            genres=['genre1', 'genre2'],
            popularity=99
        )

        Artist._create(session, 'test_id')
        mock_spotify.get_artist.assert_called_with('test_id')
        added_model = session.add.call_args[0][0]
        assert added_model.name == 'test artist'
        session.commit.assert_called()

    @patch('scrobbledownload.services.artist.Spotify')
    def test_create_with_backend(self, mock_spotify):
        mock_spotify.get_artist.return_value = SpotifyArtist(
            name='test artist',
            spotify_id='testid',
            genres=['genre1', 'genre2'],
            popularity=99
        )

        engine = create_engine('sqlite://')
        create_all(engine)
        s = Session(bind=engine)
        Artist._create(s, 'test_id')

        cxn = engine.raw_connection()
        curs = cxn.cursor()
        results = curs.execute("select * from artists").fetchall()
        assert results[0] == (1, 'test artist', 99, 'testid')