"""
Some initialization functinos for the application
"""
import logging
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scrobbledownload.models import Listen, UnfoundTracks
from scrobbledownload.models import create_all
from scrobbledownload.models.scrobbles import ScrobbleDownloader
from scrobbledownload.models.track import TrackMetadata
from scrobbledownload.secrets import Secrets, load_secrets


def initialize_logger(log_level: str=logging.INFO):
    """
    Initialize the logger for the application. We sendeverything through stderr since this is designed for Docker.
    Args:
        log_level (str): The log level to initialize with
    """
    logger = logging.getLogger("scrobbledownload")
    logger.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)


def create_sql_session(db_string: str):
    """
    Creates a sql session
    Args:
        db_string (str): a SQLAlchemy connection string.

    Returns:
        Session
    """
    engine = create_engine(db_string)

    session = sessionmaker(bind=engine)()

    create_all(engine)
    return session
