from unittest import TestCase
from scrobbledownload.secrets import Secrets
from unittest.mock import patch, mock_open, MagicMock


class TestSecrets(TestCase):
    @patch('scrobbledownload.secrets.exists')
    def test_set_path(self, mock_exists):
        Secrets._path = None
        assert Secrets._path is None

        mock_exists.return_value = True
        Secrets.set_filepath('test_path')
        assert Secrets._path == 'test_path'

        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError) as ctx:
            Secrets.set_filepath('nothing')
        assert "Configuration file was missing - it was not found at nothing" in str(ctx.exception)

    @patch('builtins.open')
    def test_init(self, m_open):
        fake_config = '''{
            "lastfm_api_key": "lastfm_api_key",
            "lastfm_api_secret": "lastfm_api_secret",
            "lastfm_username": "lastfm_username",
            "spotify_client_id": "spotify_client_id",
            "spotify_client_secret": "spotify_client_secret",
            "scrobbles_per_page": 10,
            "db_connection_string": "db_connection_string"
        }'''
        mock_open(m_open, read_data=fake_config)
        Secrets._path = 'test_path'
        s = Secrets()

        assert s._dict is not None
        assert s.spotify_client_secret == 'spotify_client_secret'

    @patch.object(Secrets, "__init__", lambda x: None)
    def test_validate(self):
        s = Secrets()
        s._dict = {
            "not a key": "value"
        }
        with self.assertRaises(KeyError) as ctx:
            s.validate()
        assert 'Configuration file did not contain all necessary keys' in str(ctx.exception)

    @patch('builtins.open')
    @patch.object(Secrets, "__init__", lambda x: None)
    def test_load(self, m_open):
        expected = {"thing": "stuff"}
        json_data = '{"thing": "stuff"}'
        mock_open(m_open, read_data=json_data)
        s = Secrets()
        actual = s.load()
        assert actual == expected

        yaml_data = '''thing: stuff
        '''
        mock_open(m_open, read_data=yaml_data)
        actual = s.load()
        assert actual == expected

    @patch('scrobbledownload.secrets.SpotifyClientCredentials')
    @patch.object(Secrets, "__init__", lambda x: None)
    def test_spotify_credentials_property(self, mock_creds):
        s = Secrets()
        client_id = 'test_client_id'
        client_secret = 'test_secret'
        s.spotify_client_id = client_id
        s.spotify_client_secret = client_secret

        res = s.spotify_credentials
        mock_creds.assert_called_with(client_id, client_secret)