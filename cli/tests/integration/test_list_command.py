"""Testes de caracterização do comando list.

Capturam comportamento MÍNIMO necessário antes da refatoração.
"""

import pytest
from typer.testing import CliRunner
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture(scope="function")
def isolated_db(tmp_path, monkeypatch):
    """Banco temporário isolado."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_file))
    
    # Criar tabelas
    from timeblock.database import create_db_and_tables
    create_db_and_tables()
    
    return db_file


@pytest.fixture
def add_sample_events(isolated_db):
    """Adiciona 3 eventos de teste."""
    from timeblock.database import get_engine
    from timeblock.models import Event, EventStatus
    from sqlmodel import Session
    
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
    COMPORTAMENTO MÍNIMO: comando list não crasha.
    """
    from timeblock.main import app
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    
    # Não deve crashar
    assert result.exit_code == 0


def test_list_shows_created_events(add_sample_events):
    """
    COMPORTAMENTO MÍNIMO: mostra eventos criados.
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
    COMPORTAMENTO MÍNIMO: banco vazio não crasha.
    """
    from timeblock.main import app
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    
    assert result.exit_code == 0
