"""Tests for TimeLog model.

BR validada: BR-TIMER-004 (Múltiplas Sessões)
"""

from datetime import datetime

from sqlmodel import Session

from timeblock.models.time_log import TimeLog


def test_time_log_creation(session: Session) -> None:
    """Test creating a time log. Validates BR-TIMER-004."""
    log = TimeLog(
        start_time=datetime(2025, 10, 16, 7, 0),
        end_time=datetime(2025, 10, 16, 8, 0),
        duration_seconds=3600,
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    assert log.id is not None
    assert log.duration_seconds == 3600


def test_time_log_with_notes(session: Session) -> None:
    """Test time log with notes. Validates BR-TIMER-004."""
    log = TimeLog(
        start_time=datetime(2025, 10, 16, 9, 0),
        notes="Productive session",
    )
    session.add(log)
    session.commit()

    assert log.notes == "Productive session"


def test_time_log_in_progress(session: Session) -> None:
    """Test time log without end time. Validates BR-TIMER-004."""
    log = TimeLog(start_time=datetime(2025, 10, 16, 10, 0))
    session.add(log)
    session.commit()

    assert log.end_time is None
    assert log.duration_seconds is None
