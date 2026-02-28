"""Integration tests para comando demo.

Testa criação e remoção de dados demonstrativos,
incluindo rotinas, hábitos e tarefas.

Referências:
    - BR-TUI-003-R28: Dados de demonstração para showcase
    - ADR-019: Test Naming Convention
    - ADR-026: Test Database Isolation Strategy
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from timeblock.main import app

runner = CliRunner()


@pytest.fixture
def demo_db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco isolado com tabelas criadas para testes demo.

    Args:
        tmp_path: Diretório temporário do pytest.
        monkeypatch: Fixture para modificar environment.

    Returns:
        Path do banco de dados temporário.
    """
    db_path = tmp_path / "test_demo.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    return db_path


class TestBRTUI003R28DemoCreate:
    """Integration: Comando demo create (BR-TUI-003-R28)."""

    def test_br_tui_003_r28_creates_three_routines(self, demo_db_path: Path) -> None:
        """demo create cria exatamente 3 rotinas demo."""
        result = runner.invoke(app, ["demo", "create"])
        assert result.exit_code == 0
        assert "Semanal Mock" in result.output
        assert "Fim de Semana Mock" in result.output
        assert "Férias Mock" in result.output

    def test_br_tui_003_r28_creates_habits_per_routine(self, demo_db_path: Path) -> None:
        """demo create cria hábitos corretos por rotina (8 + 6 + 5)."""
        result = runner.invoke(app, ["demo", "create"])
        assert result.exit_code == 0
        assert "8 hábitos criados" in result.output
        assert "6 hábitos criados" in result.output
        assert "5 hábitos criados" in result.output

    def test_br_tui_003_r28_creates_eight_tasks(self, demo_db_path: Path) -> None:
        """demo create cria 8 tarefas com datas relativas."""
        result = runner.invoke(app, ["demo", "create"])
        assert result.exit_code == 0
        assert "8 tarefas criadas" in result.output

    def test_br_tui_003_r28_activates_first_routine_by_default(self, demo_db_path: Path) -> None:
        """demo create ativa a primeira rotina por padrão."""
        result = runner.invoke(app, ["demo", "create"])
        assert result.exit_code == 0
        assert "Rotina ativa:" in result.output
        assert "Semanal Mock" in result.output

    def test_br_tui_003_r28_no_activate_flag(self, demo_db_path: Path) -> None:
        """demo create --no-activate não ativa nenhuma rotina."""
        result = runner.invoke(app, ["demo", "create", "--no-activate"])
        assert result.exit_code == 0
        assert "Rotina ativa:" not in result.output

    def test_br_tui_003_r28_success_message(self, demo_db_path: Path) -> None:
        """demo create exibe mensagem de sucesso ao final."""
        result = runner.invoke(app, ["demo", "create"])
        assert result.exit_code == 0
        assert "Demo criado com sucesso" in result.output

    def test_br_tui_003_r28_routines_visible_after_create(self, demo_db_path: Path) -> None:
        """Rotinas criadas por demo são listáveis via routine list."""
        runner.invoke(app, ["demo", "create"])
        result = runner.invoke(app, ["routine", "list"])
        assert result.exit_code == 0
        assert "Semanal Mock" in result.output


class TestBRTUI003R28DemoClear:
    """Integration: Comando demo clear (BR-TUI-003-R28)."""

    def test_br_tui_003_r28_clear_removes_demo_routines(self, demo_db_path: Path) -> None:
        """demo clear remove rotinas demo e seus hábitos."""
        runner.invoke(app, ["demo", "create"])
        result = runner.invoke(app, ["demo", "clear"])
        assert result.exit_code == 0
        assert "3 rotinas demo removidas" in result.output

    def test_br_tui_003_r28_clear_success_message(self, demo_db_path: Path) -> None:
        """demo clear exibe mensagem de limpeza concluída."""
        runner.invoke(app, ["demo", "create"])
        result = runner.invoke(app, ["demo", "clear"])
        assert result.exit_code == 0
        assert "Limpeza concluída" in result.output

    def test_br_tui_003_r28_clear_on_empty_db(self, demo_db_path: Path) -> None:
        """demo clear em banco vazio remove 0 rotinas sem erro."""
        result = runner.invoke(app, ["demo", "clear"])
        assert result.exit_code == 0
        assert "0 rotinas demo removidas" in result.output

    def test_br_tui_003_r28_routines_gone_after_clear(self, demo_db_path: Path) -> None:
        """Após demo clear, routine list não mostra rotinas demo."""
        runner.invoke(app, ["demo", "create"])
        runner.invoke(app, ["demo", "clear"])
        result = runner.invoke(app, ["routine", "list"])
        assert "Semanal Mock" not in result.output

    def test_br_tui_003_r28_clear_respects_fk_constraints(self, demo_db_path: Path) -> None:
        """demo clear deleta hábitos antes das rotinas (FK RESTRICT)."""
        runner.invoke(app, ["demo", "create"])
        result = runner.invoke(app, ["demo", "clear"])
        assert result.exit_code == 0
        assert "com hábitos" in result.output

    def test_br_tui_003_r28_create_after_clear_works(self, demo_db_path: Path) -> None:
        """demo create funciona normalmente após um clear anterior."""
        runner.invoke(app, ["demo", "create"])
        runner.invoke(app, ["demo", "clear"])
        result = runner.invoke(app, ["demo", "create"])
        assert result.exit_code == 0
        assert "Demo criado com sucesso" in result.output
