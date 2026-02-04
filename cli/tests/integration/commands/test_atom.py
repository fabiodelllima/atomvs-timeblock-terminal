"""Testes de integração para comandos de atom (habit instances).

BRs validadas:
- BR-CLI-001: Validação de Flags Dependentes
- BR-HABITINSTANCE-006: Listagem de Instâncias
"""

from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner

from timeblock.commands.habit.atom import _validate_log_mode, atom_app

runner = CliRunner()


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco de dados isolado para testes."""
    db_path = tmp_path / "test_atom.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path


class TestBRCLI001ValidacaoFlags:
    """Testes para BR-CLI-001: Validação de Flags Dependentes."""

    def test_br_cli_001_start_requires_end(self):
        """BR-CLI-001: --start requer --end."""
        with pytest.raises(ValueError, match="--start requer --end"):
            _validate_log_mode(start="08:00", end=None, duration=None)

    def test_br_cli_001_end_requires_start(self):
        """BR-CLI-001: --end requer --start."""
        with pytest.raises(ValueError, match="--start requer --end"):
            _validate_log_mode(start=None, end="09:00", duration=None)

    def test_br_cli_001_interval_excludes_duration(self):
        """BR-CLI-001: --start/--end exclui --duration."""
        with pytest.raises(ValueError, match="não pode combinar"):
            _validate_log_mode(start="08:00", end="09:00", duration=60)

    def test_br_cli_001_requires_some_input(self):
        """BR-CLI-001: Requer algum input."""
        with pytest.raises(ValueError, match="forneça"):
            _validate_log_mode(start=None, end=None, duration=None)

    def test_br_cli_001_valid_interval_passes(self):
        """BR-CLI-001: Intervalo válido passa."""
        # Não deve lançar exceção
        _validate_log_mode(start="08:00", end="09:00", duration=None)

    def test_br_cli_001_valid_duration_passes(self):
        """BR-CLI-001: Duração válida passa."""
        # Não deve lançar exceção
        _validate_log_mode(start=None, end=None, duration=60)


class TestBRHabitInstance006Listagem:
    """Testes para BR-HABITINSTANCE-006: Listagem de Instâncias."""

    def test_br_habitinstance_006_list_empty_returns_message(self, isolated_db):
        """BR-HABITINSTANCE-006: Lista vazia retorna mensagem, não erro."""
        result = runner.invoke(atom_app, ["list"])
        assert result.exit_code == 0
        assert "nenhuma" in result.output.lower()

    def test_br_habitinstance_006_filter_by_today(self, isolated_db):
        """BR-HABITINSTANCE-006: Filtro --today funciona."""
        result = runner.invoke(atom_app, ["list", "--today"])
        assert result.exit_code == 0

    def test_br_habitinstance_006_filter_by_week(self, isolated_db):
        """BR-HABITINSTANCE-006: Filtro --week funciona."""
        result = runner.invoke(atom_app, ["list", "--week"])
        assert result.exit_code == 0

    def test_br_habitinstance_006_filters_mutually_exclusive(self, isolated_db):
        """BR-HABITINSTANCE-006: --today e --week são mutuamente exclusivos."""
        result = runner.invoke(atom_app, ["list", "--today", "--week"])
        assert result.exit_code == 1

    def test_br_habitinstance_006_status_filter_pending(self, isolated_db):
        """BR-HABITINSTANCE-006: Filtro --pending funciona."""
        result = runner.invoke(atom_app, ["list", "--pending"])
        assert result.exit_code == 0

    def test_br_habitinstance_006_status_filter_done(self, isolated_db):
        """BR-HABITINSTANCE-006: Filtro --done funciona."""
        result = runner.invoke(atom_app, ["list", "--done"])
        assert result.exit_code == 0

    def test_br_habitinstance_006_status_filters_exclusive(self, isolated_db):
        """BR-HABITINSTANCE-006: --pending e --done são mutuamente exclusivos."""
        result = runner.invoke(atom_app, ["list", "--pending", "--done"])
        assert result.exit_code == 1
