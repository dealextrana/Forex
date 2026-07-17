"""Datenbank-Verbindung und Session-Verwaltung.

Entwicklung/Tests: SQLite (Datei oder in-memory). Produktion: PostgreSQL
(SPEC §3) — nur die URL ändert sich, die Modelle sind kompatibel.
Migrationen: solange sich das Schema in der Aufbauphase (M1–M4) noch
bewegt, wird es per ``init_db`` erzeugt; mit der ersten produktiven
Installation (M5) wird Alembic eingeführt und eingefroren.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from bot.persistence.models import Base

DEFAULT_URL = "sqlite:///mechmodel.sqlite3"


def make_engine(url: str = DEFAULT_URL) -> Engine:
    """Erzeugt die Engine. ``future``-Style, pool_pre_ping für Robustheit."""
    return create_engine(url, pool_pre_ping=True)


def init_db(engine: Engine) -> None:
    """Legt alle Tabellen an (idempotent)."""
    Base.metadata.create_all(engine)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Transaktionaler Sessionblock: Commit bei Erfolg, Rollback bei Fehler.

    Wichtig für die Recovery-Garantie (SPEC §11): Zustandsübergänge werden
    atomar geschrieben — halbe Zustände existieren nie.
    """
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
