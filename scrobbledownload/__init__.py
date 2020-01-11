import requests
import os
import json
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from scrobbledownload.secrets import Secrets, load_secrets    
from scrobbledownload.models import Listen, UnfoundTracks
from scrobbledownload.models.scrobbles import ScrobbleDownloader
from scrobbledownload.models.track import TrackMetadata
from spotipy.oauth2 import SpotifyClientCredentials
from scrobbledownload.models import create_all
from datetime import datetime
import logging
import sys


logger = logging.getLogger('scrobbledownload')
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
handler.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
logger.addHandler(handler)

secrets = load_secrets()

db_string = "postgres://postgres:postgres@172.17.0.1/lastfm"
engine = create_engine(db_string)

session = sessionmaker(bind=engine)()

create_all(engine)

spotify_creds = SpotifyClientCredentials(secrets.spotify_client_id, secrets.spotify_client_secret)

def download():
    last_listen_downloaded = session.query(func.max(Listen.dt)).scalar()
    if last_listen_downloaded is None:
        last_listen_downloaded = datetime(1970, 1, 1)

    logger.info(f"Downloading scrobbles from now back to {last_listen_downloaded}")
    sd = ScrobbleDownloader(secrets)

    page = 1
    keep_going = True
    while keep_going:
        scrobbles = sd.get(page)
        logger.info(f'\n\nGot {len(scrobbles.tracks)} scrobbles\nPage {page} of {scrobbles.totalPages}')
        
        for t in scrobbles.tracks:
            if t.date < last_listen_downloaded:
                logger.info("Caught up, breaking")
                keep_going = False
                break
            try:
                track = TrackMetadata(
                    track_name=t.track_name, 
                    track_artist=t.artist, 
                    track_album=t.album, 
                    mbid=t.track_mbid,
                    session=session,
                    spotify_credentials=spotify_creds
                    ).get_or_create_track()
                session.add(track)
                listen = Listen(dt=t.date, track=track)
                session.add(listen)
            except Exception as e:
                logger.exception('Unable to find track!')
                t = UnfoundTracks(
                    track_name=t.track_name,
                    track_mbid=t.track_mbid,
                    dt=t.date,
                    artist=t.artist,
                    artist_mbid=t.artist_mbid,
                    album=t.album,
                    album_mbid=t.album_mbid
                )
                session.add(t)
        session.commit()
        if page == scrobbles.totalPages or len(scrobbles.tracks) == 0:
            break
        page += 1

        