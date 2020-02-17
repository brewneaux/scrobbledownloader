"""
Downloads and processes tracks

TODO make this a downloader object
"""
import logging
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from scrobbledownload.models import Listen, UnfoundTracks
from scrobbledownload.models.scrobbles import ScrobbleDownloader, ScrobbleTrack
from scrobbledownload.secrets import spotify_creds, Secrets
from scrobbledownload.services.track import TrackMetadata

logger = logging.getLogger(__name__)


def process_track(track: ScrobbleTrack, session: Session):
    """
    Processes a single track, adding it to the database
    Args:
        track (ScrobbleTrack): a single track object
        session (Session): The sqlalchemy session
    """
    track_metadata = TrackMetadata(
        track_name=track.track_name,
        track_artist=track.artist,
        track_album=track.album,
        mbid=track.track_mbid,
        session=session,
        spotify_credentials=spotify_creds,
    ).get_or_create_track()
    session.add(track_metadata)
    listen = Listen(dt=track.listen_dt, track=track_metadata)
    session.add(listen)


def save_unfound_track(track: ScrobbleTrack, session: Session):
    """
    If a Track can't be gathered from the requisite sources, we just shove it in a secondary table for later processing.
    Args:
        track (ScrobbleTrack): a single track object
        session (Session): The sqlalchemy session
    """
    t = UnfoundTracks(
        track_name=track.track_name,
        track_mbid=track.track_mbid,
        dt=track.listen_dt,
        artist=track.artist,
        artist_mbid=track.artist_mbid,
        album=track.album,
        album_mbid=track.album_mbid,
    )
    session.add(t)


def get_last_downloaded_listen(session: Session) -> datetime:
    """
    Queries the database for the last scrobble's datetime, so we can catch up after that
    Args:
        session (Session): The sqlalchemy session

    Returns:
        datetime
    """
    last_listen_downloaded = session.query(func.max(Listen.dt)).scalar()
    if last_listen_downloaded is None:
        last_listen_downloaded = datetime(1970, 1, 1)
    return last_listen_downloaded


def download_tracks(session: Session, secrets: Secrets):
    """
    Downloads and processes tracks.  It does so a page at a time, breaking if has caught up or run out of data.
    Args:
        session (Session): The SQLAlchemy Session
        secrets (Secrets): The secrets model
    """
    last_listen_downloaded = get_last_downloaded_listen(session)

    logger.info(f"Downloading scrobbles from now back to {last_listen_downloaded}")
    sd = ScrobbleDownloader(secrets)

    page = 1
    keep_going = True
    while keep_going:
        scrobbles = sd.get(page)
        logger.info(f"\n\nGot {len(scrobbles.tracks)} scrobbles\nPage {page} of {scrobbles.totalPages}")

        for t in scrobbles.tracks:
            if t.listen_dt < last_listen_downloaded:
                logger.info("Caught up, breaking")
                keep_going = False
                break
            try:
                process_track(t, session)
            except Exception as e:
                logger.exception("Unable to find track!", exc_info=e)
                save_unfound_track(t, session)

        session.commit()

        if page == scrobbles.totalPages or len(scrobbles.tracks) == 0:
            break
        page += 1


def test_downloading(session, secrets):
    """
    I'm not real
    Args:
        session:
        secrets:

    Returns:

    """
    last_listen_downloaded = get_last_downloaded_listen(session)

    logger.info(f"Downloading scrobbles from now back to {last_listen_downloaded}")
    sd = ScrobbleDownloader(secrets)

    scrobbles = sd.get(1)
    print(scrobbles)
