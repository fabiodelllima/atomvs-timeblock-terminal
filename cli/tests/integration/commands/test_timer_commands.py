"""Testes de integração para timer/commands.py.

BRs validadas:
- BR-TIMER-001: Single Active Timer
"""

from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner

from timeblock.main import app

runner = CliRunner()


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco de dados isolado para testes."""
    db_path = tmp_path / "test_timer.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path


class TestBRTimer001SingleActive:
    """Testes para BR-TIMER-001: Single Active Timer."""

    def test_br_timer_001_no_active_timer_pause_fails(self, isolated_db):
        """BR-TIMER-001: Pause sem timer ativo falha."""
        result = runner.invoke(app, ["timer", "pause"])
        assert result.exit_code == 1
        assert "nenhum timer ativo" in result.output.lower()

    def test_br_timer_001_no_active_timer_stop_fails(self, isolated_db):
        """BR-TIMER-001: Stop sem timer ativo falha."""
        result = runner.invoke(app, ["timer", "stop"])
        assert result.exit_code == 1
        assert "nenhum timer ativo" in result.output.lower()

    def test_br_timer_001_no_active_timer_resume_fails(self, isolated_db):
        """BR-TIMER-001: Resume sem timer ativo falha."""
        result = runner.invoke(app, ["timer", "resume"])
        assert result.exit_code == 1
        assert "nenhum timer ativo" in result.output.lower()

    def test_br_timer_001_status_shows_no_timer(self, isolated_db):
        """BR-TIMER-001: Status sem timer mostra mensagem."""
        result = runner.invoke(app, ["timer", "status"])
        assert result.exit_code == 0
        assert "nenhum timer ativo" in result.output.lower()

    def test_br_timer_001_cancel_without_active_fails(self, isolated_db):
        """BR-TIMER-001: Cancel sem timer ativo falha."""
        result = runner.invoke(app, ["timer", "cancel"])
        assert result.exit_code == 1
        assert "nenhum timer ativo" in result.output.lower()
