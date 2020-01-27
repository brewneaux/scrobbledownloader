import click
from scrobbledownload import initialize_logger, create_sql_session
from scrobbledownload.download import download_tracks, test_downloading
from scrobbledownload.secrets import load_secrets, set_secrets_path
import logging



@click.group()
@click.option('--debug', default=False)
@click.option('--secrets-path', type=click.Path(exists=True, dir_okay=False), envvar='SECRETS_PATH', required=True, default='/run/secrets.json')
def cli(debug, secrets_path):
    log_level = logging.DEBUG if debug else logging.INFO
    initialize_logger(log_level)
    logging.getLogger(__name__).info(f"Loading secrets from {secrets_path}")
    set_secrets_path(secrets_path)


@cli.command()
def download():
    secrets = load_secrets()
    session = create_sql_session(secrets.db_connection_string)
    download_tracks(session, secrets)


@cli.command()
def download_test():
    secrets = load_secrets()
    session = create_sql_session(secrets.db_connection_string)
    test_downloading(session, secrets)

