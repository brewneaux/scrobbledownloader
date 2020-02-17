from unittest import TestCase
from unittest.mock import MagicMock, patch
from scrobbledownload.services.album import Album
from scrobbledownload.models import Album as AlbumModel
from scrobbledownload.models import create_all
from scrobbledownload.models.spotify_models import SpotifyAlbum
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class TestAlbum(TestCase):
    @patch('scrobbledownload.services.album.get_session')
    def test_get_album_exists(self, mock_get_session):
        session = MagicMock()
        mock_get_session.return_value = session
        expected = AlbumModel(
            name='test album',
            spotify_id='test id',
            release_date=date(2019, 1, 1),
            popularity=19)

        # Mock the return of the SQLAlchemy query for unit tests.
        session.query.return_value.filter_by.return_value.first.return_value = expected
        actual = Album.get_album('test_id')
        assert actual == expected

    @patch.object(Album, '_create')
    @patch('scrobbledownload.services.album.get_session')
    def test_get_album_doesnt_exist(self, mock_get_session, mock_create):
        session = MagicMock()
        mock_get_session.return_value = session
        session.query.return_value.filter_by.return_value.first.return_value = False

        actual = Album.get_album('test_id')
        mock_create.assert_called()

    @patch('scrobbledownload.services.album.Spotify')
    def test_create(self, mock_spotify):
        session = MagicMock()
        mock_spotify.get_album.return_value = SpotifyAlbum(
            name='test album',
            spotify_id='testid',
            release_date_str='2019-02-05',
            release_date_precision='day',
            genres=['genre1', 'genre2'],
            popularity=99
        )

        Album._create(session, 'test_id')
        mock_spotify.get_album.assert_called_with('test_id')
        added_model = session.add.call_args[0][0]
        assert added_model.name == 'test album'
        session.commit.assert_called()

    @patch('scrobbledownload.services.album.Spotify')
    def test_create_with_backend(self, mock_spotify):
        mock_spotify.get_album.return_value = SpotifyAlbum(
            name='test album',
            spotify_id='testid',
            release_date_str='2019-02-05',
            release_date_precision='day',
            genres=['genre1', 'genre2'],
            popularity=99
        )

        engine = create_engine('sqlite://')
        create_all(engine)
        s = Session(bind=engine)
        Album._create(s, 'test_id')

        cxn = engine.raw_connection()
        curs = cxn.cursor()
        results = curs.execute("select * from albums").fetchall()
        assert results == (1, 'test album', 'testid', '2019-02-05', 99)