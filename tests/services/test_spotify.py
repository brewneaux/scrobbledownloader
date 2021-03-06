from unittest import TestCase
from unittest.mock import MagicMock, patch, mock_open, call
from scrobbledownload.services.spotify import Spotify, SpotifyNotFoundExcecption
from scrobbledownload.models.spotify_models import SpotifyArtist, SpotifyAlbum, SpotifyTrack

from collections import namedtuple

Case = namedtuple('Case', ['input', 'expected'])

class TestSpotify(TestCase):
    @patch('scrobbledownload.services.spotify.os')
    @patch('builtins.open')
    def test_set_replacements(self, m_open, mock_os):
        Spotify._replacements = None
        mock_os.path.exists.return_value = True
        test_replacements = '''{"test": "replacements"}'''
        expected = {
            'test': 'replacements'
        }
        mock_open(m_open, read_data=test_replacements)
        Spotify.set_replacements('testpath')
        m_open.assert_called_with('testpath')
        assert Spotify._replacements == expected
        mock_os.path.exists.assert_called()

        mock_os.path.exists.return_value = False
        with self.assertRaises(FileNotFoundError) as ctx:
            Spotify.set_replacements('nothing')
        assert 'nothing' in str(ctx.exception)
        Spotify._replacements = None

    @patch('scrobbledownload.services.spotify._Spotify')
    def test_connect(self, mock__spotify):
        creds = MagicMock()
        spotify_api = mock__spotify()
        Spotify.connect(creds)
        assert Spotify._creds == creds
        assert Spotify._spotify_api == spotify_api
        Spotify._creds = None
        Spotify._spotify_api = None

    def test_get_artist(self):
        _spotify_api_mock = MagicMock()
        artist_id = '1234'
        _spotify_api_mock.artist.return_value = {
            'name': 'name',
            'artist_id': artist_id,
            'genres': [
                'genre1',
                'genre2'
            ],
            'popularity': 12
        }
        Spotify._spotify_api = _spotify_api_mock
        actual = Spotify.get_artist(artist_id)
        expected = SpotifyArtist(
            name='name',
            spotify_id=artist_id,
            genres=[
                'genre1',
                'genre2'
            ],
            popularity=12
        )
        assert actual == expected
        _spotify_api_mock.artist.assert_called_with(artist_id)
        Spotify._spotify_api = None


    def test_get_album(self):
        _spotify_api_mock = MagicMock()
        album_id = '1234'
        _spotify_api_mock.album.return_value = {
            'name': 'name',
            'id': album_id,
            'release_date': "2019-10",
            'release_date_precision': 'month',
            'genres': [
                'genre1',
                'genre2'
            ],
            'popularity': 12
        }
        Spotify._spotify_api = _spotify_api_mock
        actual = Spotify.get_album(album_id)
        expected = SpotifyAlbum(
            name='name',
            spotify_id=album_id,
            release_date_precision='month',
            release_date_str='2019-10',
            genres=[
                'genre1',
                'genre2'
            ],
            popularity=12
        )
        assert actual == expected
        _spotify_api_mock.album.assert_called_with(album_id)
        Spotify._spotify_api = None

    def test_handle_replacements(self):
        test_replacements = {
            'in': 'out',
            'thing': 'stuff'
        }
        Spotify._replacements = test_replacements

        test_cases = [
            Case('in', 'out'),
            Case('nothing', 'nothing')
        ]
        for case in test_cases:
            with self.subTest(input=case.input, expected=case.expected):
                assert case.expected == Spotify.handle_replacements(case.input)

    def test_to_alphanum(self):
        test_cases = [
            Case('aaa', 'aaa'),
            Case('a1a2a', 'a1a2a'),
            Case('a.a!a', 'aaa'),
        ]
        for case in test_cases:
            with self.subTest(input=case.input, expected=case.expected):
                assert case.expected == Spotify.to_alphanum(case.input)

    def test__handle_spotify_track_response(self):
        test_response = {
            'tracks': {
                'items': [
                    {
                        'name': 'testname',
                        'id': 'testid',
                        'duration_ms': 12345,
                        'popularity': 12,
                        'album': {
                            'id': "test_album_id"
                        },
                        'artists': [
                            {
                                'name': "testartist",
                                'id': 'test_artist_id'
                            }
                        ]
                    }
                ]
            }
        }
        expected = [SpotifyTrack(
            name='testname',
            spotify_id='testid',
            duration_ms=12345,
            popularity=12,
            album_id='test_album_id',
            artist_id='test_artist_id'
        )]
        assert expected == Spotify._handle_spotify_track_response(test_response)

    @patch.object(Spotify, '_handle_spotify_track_response')
    def test__make_track_query(self, mock_respones_handler):
        _spotify_api_mock = MagicMock()
        Spotify._spotify_api = _spotify_api_mock
        expected_search_string = 'test_name artist:test_artist'
        Spotify._make_track_query('test_name', 'test_artist')
        _spotify_api_mock.search.assert_called_with(q=expected_search_string, type='track')
        mock_respones_handler.assert_called()
        Spotify._spotify_api = None

    @patch.object(Spotify, '_make_track_query')
    def test_get_track(self, mock_make_track_query):
        mock_make_track_query.return_value = []
        Spotify._replacements = {}

        with self.assertRaises(SpotifyNotFoundExcecption) as ctx:
            Spotify.get_track('this is a long track name', 'test artist')
        expected_calls = [
            call('this is a long track name', 'test artist'),
            call('is a long track name', 'test artist'),
            call('a long track name', 'test artist'),
            call('long track name', 'test artist'),
            call('track name', 'test artist'),
            call('name', 'test artist'),
        ]
        mock_make_track_query.assert_has_calls(expected_calls)
        assert call('', 'test artist') not in mock_make_track_query.mock_calls

        mock_make_track_query.return_value = ['thing']
        assert Spotify.get_track('name', 'artist') == 'thing'