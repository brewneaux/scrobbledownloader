import hashlib
import requests
import os
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
from typing import List
from scrobbledownload.models import (
    Track,
    TrackTag,
    Artist,
    ArtistGenre,
    ArtistTag,
    Album,
    AlbumGenre,
)
from dateutil.parser import parse
import logging
import string

logger = logging.getLogger(__name__)

def to_alphanum(input):
    return input.translate(str.maketrans('', '', string.punctuation))

edge_cases = {
    'The AllAmerican Rejects': 'The All American Rejects',
    'blink182': 'blink-182',
    '3OH3': '3OH!3',
    'The Kodan Armada': 'Kodan Armada',
    'Pg99': 'Pageninetynine',
    'Combatwoundedveteran': 'Combat wounded veteran',
    'The Pack AD': 'The pack a.d.',
    'Angel Dut': "Angel Du$t"
}

def fix_weird_edgecase(input):
    return edge_cases.get(input, input)


def parse_date(date, precision):
    dt = parse(date).date()
    if precision == "year":
        return dt.replace(month=1, day=1)
    if precision == "month":
        return dt.replace(day=1)
    if precision == "day":
        return dt


class TrackNotFoundError(Exception):
    pass


class TrackMetadata(object):
    def __init__(
        self, track_name, track_artist, track_album, mbid, session, spotify_credentials
    ):
        self.session = session
        self.ccm = spotify_credentials
        self.sp = Spotify(client_credentials_manager=self.ccm)
        self.track_name = fix_weird_edgecase(to_alphanum(track_name))
        self.track_artist = fix_weird_edgecase(to_alphanum(track_artist))
        self.track_album = fix_weird_edgecase(to_alphanum(track_album))
        self.mbid = mbid

    @property
    def hash(self):
        return hashlib.sha1(f'{self.track_name} - {self.track_artist} on {self.track_album}'.encode()).hexdigest()

    def get_track_result_from_spotify(self):
        search_string = f"{self.track_name} artist:{self.track_artist}"

        logger.debug(f'Quering spotify api for {search_string}')
        tracks = self.sp.search(q=search_string, type="track")
        track_name_words = list(reversed(self.track_name.split()))

        results_count = len(tracks["tracks"]["items"])
        logger.debug(f'loop stuff: {track_name_words}, {results_count}')


        while track_name_words and not len(tracks["tracks"]["items"]):
            track_name_words.pop()
            search_string_track_name = ' '.join(list(reversed(track_name_words)))
            search_string = f"{search_string_track_name} artist:{self.track_artist}"
            logger.debug(f'Quering spotify api for {search_string}')
            tracks = self.sp.search(q=search_string, type="track")

        try:
            track_json = tracks["tracks"]["items"][0]
        except:
            logger.debug(f'Cant find {self.track_artist} - {self.track_name}')
            raise TrackNotFoundError(f'Cant find {self.track_artist} - {self.track_name}')
        return track_json

    def get_or_create_track(self):
        logger.info(f'Creating TrackMetadata object for name: {self.track_name} by {self.track_artist} on {self.track_album}')
        result = self.session.query(Track).filter_by(mbid=self.mbid).first()
        if result:
            return result

        track_json = self.get_track_result_from_spotify()

        artist = self.get_or_create_artist(track_json["artists"][0]["id"])
        album = self.get_or_create_album(track_json["album"]["id"])
        track = Track(
            name=self.track_name,
            spotify_id=track_json['id'],
            mbid=self.mbid or self.hash,
            artist=artist,
            album=album
        )
        return track

    def get_or_create_artist(self, artist_id):
        result = self.session.query(Artist).filter_by(spotify_id=artist_id).first()
        if result:
            logger.debug(f'Retrieved Artist object for {self.track_artist}')
            return result

        logger.debug(f'Building Artist object for {self.track_artist}')

        artist = self.sp.artist(artist_id)
        genres = [ArtistGenre(genre=x) for x in artist["genres"]]
        a = Artist(
            name=artist["name"],
            popularity=artist["popularity"],
            spotify_id=artist["id"],
            genres=genres,
        )
        return a

    def get_or_create_album(self, album_id):
        result = self.session.query(Album).filter_by(spotify_id=album_id).first()
        if result:
            logger.debug(f'Retrieved existing Album object for {self.track_album}')
            return result

        logger.debug(f'Building Album object for {self.track_album}')

        album = self.sp.album(album_id)
        genres = [AlbumGenre(genre=x) for x in album["genres"]]
        a = Album(
            name=album["name"],
            popularity=album["popularity"],
            spotify_id=album["id"],
            genres=genres,
            release_date=parse_date(
                album["release_date"], album["release_date_precision"]
            ),
        )
        return a

    