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



def initialize_logger(log_level=logging.INFO):
    logger = logging.getLogger('scrobbledownload')
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)

def create_sql_session(db_string):
    engine = create_engine(db_string)

    session = sessionmaker(bind=engine)()

    create_all(engine)
    return session

