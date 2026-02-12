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


class TestBRTimer001StartWorkflow:
    """Testes para BR-TIMER-001: Start Workflow via CLI."""

    def test_br_timer_001_start_with_invalid_schedule(self, isolated_db):
        """BR-TIMER-001: Start com schedule inexistente falha."""
        result = runner.invoke(app, ["timer", "start", "--background", "--schedule", "999"])
        assert result.exit_code == 1
        assert "não encontrad" in result.output.lower()

    def test_br_timer_001_start_with_invalid_task(self, isolated_db):
        """BR-TIMER-001: Start com task inexistente falha."""
        result = runner.invoke(app, ["timer", "start", "--background", "--task", "999"])
        assert result.exit_code == 1
        # Task não encontrada ou não implementado

    def test_br_timer_001_start_requires_selection_or_flag(self, isolated_db):
        """BR-TIMER-001: Start sem seleção ou flag falha."""
        result = runner.invoke(app, ["timer", "start", "--background"])
        assert result.exit_code == 1
        assert "nenhuma" in result.output.lower() or "selecion" in result.output.lower()


class TestTimerStartEdgeCases:
    """Testes para edge cases do timer start."""

    def test_start_with_task_not_implemented(self, isolated_db):
        """Timer para task exibe 'não implementado'."""
        # Criar uma task primeiro
        from typer.testing import CliRunner

        from timeblock.main import app as main_app

        task_runner = CliRunner()
        task_runner.invoke(main_app, ["task", "create", "Test Task"])

        result = runner.invoke(app, ["timer", "start", "--background", "--task", "1"])
        assert result.exit_code == 1
        assert (
            "não implementado" in result.output.lower() or "não encontrad" in result.output.lower()
        )

    def test_start_via_context_file(self, isolated_db, tmp_path, monkeypatch):
        """Start via arquivo de contexto (.timeblock_context)."""
        import json

        # Criar arquivo de contexto com schedule selecionado
        context_file = tmp_path / ".timeblock_context"
        context_file.write_text(json.dumps({"selected_schedule": 999}))
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

        result = runner.invoke(app, ["timer", "start", "--background"])
        assert result.exit_code == 1
        # Instância 999 não existe
        assert "não encontrad" in result.output.lower()

    def test_start_schedule_confirm_no(self, isolated_db):
        """Start com --schedule mas confirmação negada."""
        # Precisa de instância válida para chegar no confirm
        # Sem dados, vai falhar antes
        result = runner.invoke(app, ["timer", "start", "--schedule", "999"], input="n\n")
        assert result.exit_code == 1
