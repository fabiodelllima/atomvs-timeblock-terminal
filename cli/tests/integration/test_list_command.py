"""Characterization tests for list command.

Capture MINIMAL necessary behavior before refactoring.
"""

import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture(scope="function")
def isolated_db(tmp_path, monkeypatch):
    """Isolated temporary database."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_file))
    # Create tables
    from timeblock.database import create_db_and_tables

    create_db_and_tables()
    return db_file


@pytest.fixture
def add_sample_events(isolated_db):
    """Add 3 test events."""
    from sqlmodel import Session
    from timeblock.database import get_engine
    from timeblock.models import Event, EventStatus

    now = datetime.now(timezone.utc)
    events = [
        Event(
            title="Morning Standup",
            scheduled_start=now + timedelta(days=1, hours=9),
            scheduled_end=now + timedelta(days=1, hours=9, minutes=30),
            status=EventStatus.PLANNED,
        ),
        Event(
            title="Code Review",
            scheduled_start=now + timedelta(days=2, hours=14),
            scheduled_end=now + timedelta(days=2, hours=15),
            status=EventStatus.PLANNED,
        ),
        Event(
            title="Gym",
            scheduled_start=now + timedelta(days=3, hours=18),
            scheduled_end=now + timedelta(days=3, hours=19),
            status=EventStatus.PLANNED,
        ),
    ]
    engine = get_engine()
    with Session(engine) as session:
        for event in events:
            session.add(event)
        session.commit()


def test_list_command_works(add_sample_events):
    """
    MINIMAL BEHAVIOR: list command doesn't crash.
    """
    from timeblock.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    # Should not crash
    assert result.exit_code == 0


def test_list_shows_created_events(add_sample_events):
    """
    MINIMAL BEHAVIOR: shows created events.
    """
    from timeblock.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Morning Standup" in result.output
    assert "Code Review" in result.output
    assert "Gym" in result.output


def test_list_empty_db_works(isolated_db):
    """
    MINIMAL BEHAVIOR: empty database doesn't crash.
    """
    from timeblock.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
