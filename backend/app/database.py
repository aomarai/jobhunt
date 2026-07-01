from contextlib import contextmanager
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(str(settings.database_url))
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Returns a database connection session.
    """
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()