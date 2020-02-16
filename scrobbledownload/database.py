from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, Session
from scrobbledownload.models import create_all

_engine: Engine
_sessionmaker: sessionmaker


def get_session() -> Session:
    """
    Get a fresh-and-so-clean SQLAlchemy Session
    Returns:
        Session
    """
    return _sessionmaker()


def create_sessionmaker(db_string):
    global engine, _sessionmaker
    engine = create_engine(db_string)
    _sessionmaker = sessionmaker(bind=engine)


def create_sql_session(db_string: str):
    """
    Creates a sql session
    Args:
        db_string (str): a SQLAlchemy connection string.

    Returns:
        Session
    """
    create_sessionmaker(db_string)
    create_all(engine)
    return _sessionmaker()
