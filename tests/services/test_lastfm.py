from unittest import TestCase
from unittest.mock import patch, MagicMock
from scrobbledownload.services import LastFM
from scrobbledownload.models.scrobbles import Scrobbles, ScrobbleTrack
import datetime

# This is a sample scrobble downloaded from
# http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=rj&api_key=YOUR KEY&format=json&limit=1
# I've removed the images section so its way shorter
sample_scrobble_response = {
    "recenttracks": {
        "@attr": {
            "page": "1",
            "total": "132403",
            "user": "RJ",
            "perPage": "1",
            "totalPages": "132403"
        },
        "track": [
            {
                "artist": {
                    "mbid": "",
                    "#text": "Fleetwood Mac"
                },
                "album": {
                    "mbid": "02ac7ce7-4f21-4010-8210-e682085c58ab",
                    "#text": "Rumours"
                },
                "streamable": "0",
                "date": {
                    "uts": "1581873452",
                    "#text": "16 Feb 2020, 17:17"
                },
                "url": "https:\/\/www.last.fm\/music\/Fleetwood+Mac\/_\/Go+Your+Own+Way+-+2004+Remaster",
                "name": "Go Your Own Way - 2004 Remaster",
                "mbid": ""
            }
        ]
    }
}

class TestLastFm(TestCase):
    def test_init(self):
        l = LastFM('test_user', 'test_key')
        assert l._username == 'test_user'
        assert l._api_key == 'test_key'

    @patch.object(LastFM, '_handle_lastfm_response')
    @patch('scrobbledownload.services.lastfm.requests')
    def test_download_scrobbles(self, mock_requests, mock_handle):
        response = MagicMock()
        mock_requests.get.return_value = response
        response.json.return_value = [{'test': 'thing'}]
        track = ScrobbleTrack(
            track_name='test track',
            track_mbid='test mbid',
            listen_dt=datetime.datetime(2019, 2, 3, 4, 5, 6),
            artist='test artist',
            artist_mbid='artist mbd',
            album='test album',
            album_mbid='album mbid'
        )
        scrobbles = Scrobbles(
            page=1,
            perPage=10,
            totalPages=11,
            tracks=[track]
        )
        mock_handle.return_value = scrobbles

        l = LastFM('test_user', 'test_key')
        actual = l.download_scrobbles(1, 10)
        assert actual == scrobbles

    @patch.object(LastFM, '_get_tracks')
    def test_handle_lastfm_response(self, mock_get_tracks):
        track = ScrobbleTrack(
            track_name='test track',
            track_mbid='test mbid',
            listen_dt=datetime.datetime(2019, 2, 3, 4, 5, 6),
            artist='test artist',
            artist_mbid='artist mbd',
            album='test album',
            album_mbid='album mbid'
        )
        mock_get_tracks.return_value = [track]
        actual = LastFM._handle_lastfm_response(sample_scrobble_response)
        expected = Scrobbles(
            page=1,
            perPage=1,
            totalPages=132403,
            tracks=[track]
        )
        assert actual == expected

    def test_get_tracks(self):
        tracks = sample_scrobble_response['recenttracks']['track']

        expected = ScrobbleTrack(
            track_name='Go Your Own Way - 2004 Remaster',
            track_mbid='',
            listen_dt=datetime.datetime(2020, 2, 16, 17, 17, 32),
            artist='Fleetwood Mac',
            artist_mbid='',
            album='Rumours',
            album_mbid='02ac7ce7-4f21-4010-8210-e682085c58ab'
        )
        actual = LastFM._get_tracks(tracks)
        assert actual == [expected]

        tracks[0]['@attr'] = {'nowplaying': True}
        actual = LastFM._get_tracks(tracks)
        assert actual == []