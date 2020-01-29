"""
All of the SQLAlchemy models to represent the data we are saving.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ArtistTag(Base):
    """
    Represents the various tags that are attached to an Artist.
    """

    __tablename__ = "artist_tags"

    id = Column(Integer(), primary_key=True)
    artist_id = Column(Integer(), ForeignKey("artists.id"), nullable=False)
    tag = Column(String(1000))
    artist = relationship("Artist")


class ArtistGenre(Base):
    __tablename__ = "artist_genres"

    id = Column(Integer(), primary_key=True)
    artist_id = Column(Integer(), ForeignKey("artists.id"), nullable=False)
    genre = Column(String(1000))


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer(), primary_key=True)
    name = Column(String(1000))
    popularity = Column(Integer())
    spotify_id = Column(String(100), index=True)

    tags = relationship("ArtistTag")
    genres = relationship("ArtistGenre")


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


def create_all(engine):
    """
    Creats all of the models.

    Args:
        engine (Engine): A built SQLAlchemy engine
    """
    Base.metadata.create_all(engine)
