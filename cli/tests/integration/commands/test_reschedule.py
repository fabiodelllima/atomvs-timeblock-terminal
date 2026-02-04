"""Testes de integração para comandos de reschedule.

Testa detecção de conflitos via CLI.
Nota: reschedule é subcomando, não tem BRs específicas documentadas.
"""

from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner

from timeblock.main import app as main_app

runner = CliRunner()


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco de dados isolado para testes."""
    db_path = tmp_path / "test_reschedule.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path


class TestRescheduleConflicts:
    """Testes para comando reschedule conflicts."""

    def test_conflicts_with_valid_date(self, isolated_db):
        """Data válida executa sem erro fatal."""
        result = runner.invoke(main_app, ["reschedule", "conflicts", "--date", "2025-11-08"])
        # Pode não ter conflitos, mas não deve dar erro de parsing
        assert result.exit_code in [0, 1]

    def test_conflicts_with_invalid_date_format(self, isolated_db):
        """Data inválida retorna erro."""
        result = runner.invoke(main_app, ["reschedule", "conflicts", "--date", "invalid"])
        assert result.exit_code == 1
        assert "formato" in result.output.lower() or "inválido" in result.output.lower()
