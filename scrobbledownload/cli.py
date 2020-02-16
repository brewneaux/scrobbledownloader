"""
THe comand line interface for the scrobble downloader.
"""
import click
from scrobbledownload import initialize_logger
from scrobbledownload.database import create_sql_session
from scrobbledownload.download import download_tracks, test_downloading
from scrobbledownload.secrets import Secrets
from scrobbledownload.services.track import Track
from scrobbledownload.services.spotify import Spotify
from scrobbledownload.services.genius import Genius
import logging


@click.group()
@click.option("--debug", default=False)
@click.option(
    "--secrets-path",
    type=click.Path(exists=True, dir_okay=False),
    envvar="SECRETS_PATH",
    required=True,
    default="/run/secrets.json",
)
def cli(debug, secrets_path):
    """
    Entrypoint for the application
    Args:
        ctx (click.context):
        debug:
        secrets_path:
    """
    log_level = logging.DEBUG if debug else logging.INFO
    initialize_logger(log_level)
    logging.getLogger(__name__).info(f"Loading secrets from {secrets_path}")
    Secrets.set_filepath(secrets_path)



@cli.command()
def download_test():
    """
    shoundt exist
    todo remove me
    """
    secrets = Secrets()
    session = create_sql_session(secrets.db_connection_string)
    test_downloading(session, secrets)


@cli.command()
@cli.option(
    "--replacements-file",
    type=click.Path(exists=True, dir_okay=False),
    envvar='REPLACEMENTS_FILE',
    required=True,
    default='/run/replacements.json'
)
def download(replacements_file):
    """
    Download new scrobbles.
    """
    secrets = Secrets()
    session = create_sql_session(secrets.db_connection_string)
    spotify = Spotify.connect(secrets.spotify_credentials)
    spotify.set_replacements(replacements_file)

    download_tracks(session, secrets)

