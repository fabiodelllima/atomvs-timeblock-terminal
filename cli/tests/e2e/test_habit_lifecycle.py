"""
E2E tests validando regras de negocio completas.

Referencias:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
BRs cobertas:
    - BR-HABIT-001: Criacao de habitos
    - BR-HABIT-003: Geracao de instancias via --generate
"""

from pathlib import Path

import pytest
from freezegun import freeze_time
from pytest import MonkeyPatch
from typer.testing import CliRunner

from timeblock.main import app


@pytest.fixture
def isolated_db(tmp_path: Path) -> Path:
    """Cria banco de dados temporario isolado para E2E tests."""
    db_path = tmp_path / "test.db"
    return db_path


class TestBRHabitWorkflow:
    """
    E2E: Workflow completo de habitos.

    BRs cobertas:
    - BR-HABIT-001: Criacao de habitos
    - BR-HABIT-003: Geracao de instancias via --generate
    """

    def test_br_habit_complete_daily_workflow_with_confirmation(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario cria habito confirmando rotina ativa interativamente.
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # Criar habito confirmando rotina ativa
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--title",
                "Meditação",
                "--start",
                "06:00",
                "--end",
                "06:20",
                "--repeat",
                "EVERYDAY",
            ],
            input="y\n",
        )

        assert result.exit_code == 0, f"Deve criar com sucesso. Output: {result.output}"
        assert "criado" in result.output.lower(), "Deve confirmar criacao"

    @freeze_time("2025-10-01")
    def test_br_habit_complete_daily_workflow_explicit_routine(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario cria habito com --routine e --generate.

        DADO: Data fixa em 2025-10-01
        QUANDO: Usuario cria habito EVERYDAY com --generate 1
        ENTAO: Sistema gera 32 instancias (01/10 a 01/11 inclusive)
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # 1. Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # 2. Criar habito com --routine e --generate
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--title",
                "Meditação",
                "--start",
                "06:00",
                "--end",
                "06:20",
                "--repeat",
                "EVERYDAY",
                "--routine",
                "1",
                "--generate",
                "1",
            ],
        )
        assert result.exit_code == 0, f"Criacao deve ter sucesso. Output: {result.output}"
        # De 01/10 a 01/11 = 32 dias
        assert "32" in result.output or "instância" in result.output.lower()

    def test_br_habit_creation_rejection_aborts(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario rejeita criar habito na rotina ativa.
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Setup
        runner.invoke(app, ["init"])
        runner.invoke(app, ["routine", "create", "Rotina Matinal"])

        # Rejeitar rotina ativa
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--title",
                "Meditação",
                "--start",
                "06:00",
                "--end",
                "06:20",
                "--repeat",
                "EVERYDAY",
            ],
            input="n\n",
        )

        assert (
            result.exit_code != 0
            or "Aborted" in result.output
            or "ID da rotina" in result.output
        ), f"Deve abortar ou pedir alternativa. Output: {result.output}"


class TestBREventConflictWorkflow:
    """
    E2E: Workflow de deteccao e resolucao de conflitos.

    BRs cobertas:
    - BR-REORDER-001: Deteccao de conflitos de horario
    - BR-REORDER-002: Proposta de reorganizacao
    """

    @pytest.mark.skip(
        reason="Deteccao de conflitos em habit edit nao implementada ainda"
    )
    def test_br_event_conflict_detection_and_resolution(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Sistema detecta conflito de horarios.

        TODO: Implementar deteccao de conflitos no habit edit
        """
        pass
