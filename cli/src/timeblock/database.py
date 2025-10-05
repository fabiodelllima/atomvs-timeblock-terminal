"""Database connection and operations."""

from pathlib import Path
from typing import Optional

from sqlmodel import Session, SQLModel, create_engine, select

from .models import ChangeLog, Event, PauseLog, TimeLog

# Database path
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "timeblock.db"

# SQLite connection string
DATABASE_URL = f"sqlite:///{DB_PATH}"


def get_engine():
    """Create and return SQLite engine.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    # Create data directory if it doesn't exist
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Create engine with echo=False for production
    engine = create_engine(DATABASE_URL, echo=False)
    return engine


def create_db_and_tables():
    """Create database and all tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session.

    Yields:
        Session: SQLModel session instance.
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session


# Event CRUD operations
def create_event(session: Session, event: Event) -> Event:
    """Create a new event.

    Args:
        session: Database session.
        event: Event instance to create.

    Returns:
        Event: Created event with ID.
    """
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def get_event(session: Session, event_id: int) -> Optional[Event]:
    """Get event by ID.

    Args:
        session: Database session.
        event_id: Event ID.

    Returns:
        Event or None: Event instance if found.
    """
    return session.get(Event, event_id)


def get_events(session: Session, limit: int = 100) -> list[Event]:
    """Get all events.

    Args:
        session: Database session.
        limit: Maximum number of events to return.

    Returns:
        list[Event]: List of events.
    """
    statement = select(Event).limit(limit)
    return list(session.exec(statement))


def update_event(session: Session, event: Event) -> Event:
    """Update an existing event.

    Args:
        session: Database session.
        event: Event instance with updated data.

    Returns:
        Event: Updated event.
    """
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def delete_event(session: Session, event_id: int) -> bool:
    """Delete event by ID.

    Args:
        session: Database session.
        event_id: Event ID to delete.

    Returns:
        bool: True if deleted, False if not found.
    """
    event = session.get(Event, event_id)
    if event:
        session.delete(event)
        session.commit()
        return True
    return False


# TimeLog CRUD operations
def create_timelog(session: Session, timelog: TimeLog) -> TimeLog:
    """Create a new time log.

    Args:
        session: Database session.
        timelog: TimeLog instance to create.

    Returns:
        TimeLog: Created time log with ID.
    """
    session.add(timelog)
    session.commit()
    session.refresh(timelog)
    return timelog


def get_timelog(session: Session, timelog_id: int) -> Optional[TimeLog]:
    """Get time log by ID.

    Args:
        session: Database session.
        timelog_id: TimeLog ID.

    Returns:
        TimeLog or None: TimeLog instance if found.
    """
    return session.get(TimeLog, timelog_id)


def get_timelogs_by_event(session: Session, event_id: int) -> list[TimeLog]:
    """Get all time logs for a specific event.

    Args:
        session: Database session.
        event_id: Event ID.

    Returns:
        list[TimeLog]: List of time logs.
    """
    statement = select(TimeLog).where(TimeLog.event_id == event_id)
    return list(session.exec(statement))


# PauseLog CRUD operations
def create_pauselog(session: Session, pauselog: PauseLog) -> PauseLog:
    """Create a new pause log.

    Args:
        session: Database session.
        pauselog: PauseLog instance to create.

    Returns:
        PauseLog: Created pause log with ID.
    """
    session.add(pauselog)
    session.commit()
    session.refresh(pauselog)
    return pauselog


def get_pauselogs_by_timelog(session: Session, timelog_id: int) -> list[PauseLog]:
    """Get all pause logs for a specific time log.

    Args:
        session: Database session.
        timelog_id: TimeLog ID.

    Returns:
        list[PauseLog]: List of pause logs.
    """
    statement = select(PauseLog).where(PauseLog.timelog_id == timelog_id)
    return list(session.exec(statement))


# ChangeLog CRUD operations
def create_changelog(session: Session, changelog: ChangeLog) -> ChangeLog:
    """Create a new change log entry.

    Args:
        session: Database session.
        changelog: ChangeLog instance to create.

    Returns:
        ChangeLog: Created change log with ID.
    """
    session.add(changelog)
    session.commit()
    session.refresh(changelog)
    return changelog


def get_changelogs_by_event(session: Session, event_id: int) -> list[ChangeLog]:
    """Get all change logs for a specific event.

    Args:
        session: Database session.
        event_id: Event ID.

    Returns:
        list[ChangeLog]: List of change logs ordered by time (newest first).
    """
    statement = (
        select(ChangeLog)
        .where(ChangeLog.event_id == event_id)
        .order_by(ChangeLog.changed_at.desc())  # type: ignore
    )
    return list(session.exec(statement))
