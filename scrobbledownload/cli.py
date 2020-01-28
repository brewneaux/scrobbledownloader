import click
from scrobbledownload import initialize_logger, create_sql_session
from scrobbledownload.download import download_tracks, test_downloading
from scrobbledownload.secrets import load_secrets, set_secrets_path
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
@click.pass_context
def cli(ctx, debug, secrets_path):
    """
    Entrypoint for the application
    Args:
        debug:
        secrets_path:
    """
    log_level = logging.DEBUG if debug else logging.INFO
    initialize_logger(log_level)
    logging.getLogger(__name__).info(f"Loading secrets from {secrets_path}")
    ctx.obj = load_secrets(secrets_path)


@cli.command()
@click.pass_obj
def download(secrets):
    """
    Download new scrobbles.
    """
    session = create_sql_session(secrets.db_connection_string)
    download_tracks(session, secrets)


@cli.command()
@click.pass_obj
def download_test(secrets):
    """

    """
    session = create_sql_session(secrets.db_connection_string)
    test_downloading(session, secrets)
