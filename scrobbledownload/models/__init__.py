"""
All of the SQLAlchemy models to represent the data we are saving.
"""
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class ArtistGenre(Base):
    __tablename__ = "artist_genres"

    id = Column(Integer(), primary_key=True)
    artist_id = Column(Integer(), ForeignKey("artists.id"), nullable=False)
    genre = Column(String(1000))


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer(), primary_key=True)
    name = Column(String(1000), index=True)
    popularity = Column(Integer())
    spotify_id = Column(String(100), index=True)

    genres = relationship("ArtistGenre")

    @classmethod
    def get_by_name(cls, name: str, session: Session):
        """
        Get the artist object by the name of the artist
        Args:
            name (str): The name of the artist
            session (Session): The SQLAlchemy ORM session

        Returns:
            Artist
        """
        result = session.query(cls).filter_by(name=name).first()
        return result


class AlbumGenre(Base):
    __tablename__ = "album_genres"

    id = Column(Integer(), primary_key=True)
    album_id = Column(Integer(), ForeignKey("albums.id"), nullable=False)
    genre = Column(String(1000))


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer(), primary_key=True)
    name = Column(String(1000))
    spotify_id = Column(String(100), index=True)
    release_date = Column(Date())
    popularity = Column(Integer())
    genres = relationship("AlbumGenre")


class TrackTag(Base):
    __tablename__ = "track_tags"

    id = Column(Integer(), primary_key=True)
    track_id = Column(Integer(), ForeignKey("tracks.id"), nullable=False)
    tag = Column(String(1000))
    track = relationship("Track")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer(), primary_key=True)
    name = Column(String(1000))
    spotify_id = Column(String(100))
    mbid = Column(String(100), index=True)
    generated_id = Column(String(100), index=True)
    artist_id = Column(Integer(), ForeignKey("artists.id"))
    album_id = Column(Integer(), ForeignKey("albums.id"))
    artist = relationship("Artist", foreign_keys=[artist_id])
    album = relationship("Album", foreign_keys=[album_id])
    tags = relationship("TrackTag")


class Listen(Base):
    __tablename__ = "listens"

    id = Column(Integer(), primary_key=True)
    dt = Column(DateTime())
    track_id = Column(Integer(), ForeignKey("tracks.id"))
    track = relationship("Track")

    @classmethod
    def get_last_listen(cls, session: Session) -> datetime:
        """
        Get the max listen date from the database to use as a loop starting point.
        Args:
            session (Session): The SQLAlchemy ORM session

        Returns:
            datetime
        """
        last_listen_downloaded = session.query(func.max(cls.dt)).scalar()
        if last_listen_downloaded is None:
            last_listen_downloaded = datetime(1970, 1, 1)
        return last_listen_downloaded


class UnfoundTracks(Base):
    __tablename__ = "unfoundtracks"

    id = Column(Integer(), primary_key=True)
    track_name = Column(String(1000))
    track_mbid = Column(String(1000))
    dt = Column(DateTime())
    artist = Column(String(1000))
    artist_mbid = Column(String(1000))
    album = Column(String(1000))
    album_mbid = Column(String(1000))


def create_all(engine: Engine):
    """
    Creats all of the models.

    Args:
        engine (Engine): A built SQLAlchemy engine
    """
    Base.metadata.create_all(engine)
