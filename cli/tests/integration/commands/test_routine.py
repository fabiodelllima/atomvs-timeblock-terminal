"""Testes de integração para comandos de routine.

BRs validadas:
- BR-ROUTINE-001: Single Active Constraint
- BR-ROUTINE-004: Activation Cascade
- BR-ROUTINE-005: Validação de Nome
"""

from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner

from timeblock.commands.routine import app

runner = CliRunner()


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco de dados isolado para testes."""
    db_path = tmp_path / "test_routine.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path


class TestBRRoutine001SingleActive:
    """Testes para BR-ROUTINE-001: Single Active Constraint."""

    def test_br_routine_001_only_one_active(self, isolated_db):
        """BR-ROUTINE-001: Apenas uma rotina pode estar ativa."""
        runner.invoke(app, ["create", "Manhã"], input="y\n")
        runner.invoke(app, ["create", "Noite"], input="y\n")

        result = runner.invoke(app, ["list", "--all"])
        active_count = result.output.count("[ATIVA]")
        assert active_count <= 1


class TestBRRoutine004ActivationCascade:
    """Testes para BR-ROUTINE-004: Activation Cascade."""

    def test_br_routine_004_activate_deactivates_others(self, isolated_db):
        """BR-ROUTINE-004: Ativar uma rotina desativa outras."""
        runner.invoke(app, ["create", "Manhã"], input="y\n")
        runner.invoke(app, ["create", "Noite"], input="n\n")

        runner.invoke(app, ["activate", "2"])

        result = runner.invoke(app, ["list", "--all"])
        # Só pode ter uma ativa
        assert result.output.count("[ATIVA]") == 1
        # Noite deve estar ativa agora
        lines = result.output.split("\n")
        for line in lines:
            if "Noite" in line:
                assert "[ATIVA]" in line or "ATIVA" in line.upper()


class TestBRRoutine005ValidacaoNome:
    """Testes para BR-ROUTINE-005: Validação de Nome."""

    def test_br_routine_005_create_requires_name(self, isolated_db):
        """BR-ROUTINE-005: Rotina requer nome."""
        result = runner.invoke(app, ["create", "Rotina Matinal"], input="n\n")
        assert result.exit_code == 0
        assert "Rotina Matinal" in result.output

    def test_br_routine_005_list_shows_names(self, isolated_db):
        """BR-ROUTINE-005: Lista exibe nomes das rotinas."""
        runner.invoke(app, ["create", "Trabalho"], input="n\n")
        runner.invoke(app, ["create", "Lazer"], input="n\n")

        result = runner.invoke(app, ["list", "--all"])
        assert "Trabalho" in result.output
        assert "Lazer" in result.output

    def test_br_routine_005_delete_by_id(self, isolated_db):
        """BR-ROUTINE-005: Delete usa ID, não nome."""
        runner.invoke(app, ["create", "Teste"], input="n\n")

        result = runner.invoke(app, ["delete", "1", "--force"])
        assert result.exit_code == 0
        assert "deletada" in result.output.lower()

    def test_br_routine_005_nonexistent_returns_error(self, isolated_db):
        """BR-ROUTINE-005: ID inexistente retorna erro."""
        result = runner.invoke(app, ["activate", "999"])
        assert result.exit_code == 1
        assert "não encontrada" in result.output.lower()
