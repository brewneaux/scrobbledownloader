from unittest import TestCase
from unittest.mock import MagicMock, patch
from scrobbledownload.services.spotify import Spotify


class TestSpotify:
    def test_set_replacements(self):
        Spotify._replacements = None