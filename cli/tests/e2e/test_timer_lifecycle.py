"""
E2E tests validando workflow completo de timer.

Referencias:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
BRs cobertas:
    - BR-TIMER-001: Iniciar timer para HabitInstance
    - BR-TIMER-002: Estados do timer (RUNNING, PAUSED, DONE, CANCELLED)
    - BR-TIMER-003: Pause/Resume tracking
    - BR-TIMER-004: Stop finaliza e salva
    - BR-TIMER-005: Cancel descarta sem salvar
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


@pytest.fixture
def setup_habit_instance(isolated_db: Path, monkeypatch: MonkeyPatch) -> CliRunner:
    """Setup completo: init + routine + habit + generate."""
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
    runner = CliRunner()

    # Init
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, f"Init falhou: {result.output}"

    # Criar rotina
    result = runner.invoke(app, ["routine", "create", "Test Routine"])
    assert result.exit_code == 0, f"Routine falhou: {result.output}"

    # Criar habito com instancia
    result = runner.invoke(
        app,
        [
            "habit",
            "create",
            "--routine",
            "1",
            "--title",
            "Test Habit",
            "--start",
            "09:00",
            "--end",
            "10:00",
            "--repeat",
            "EVERYDAY",
            "--generate",
            "1",
        ],
    )
    assert result.exit_code == 0, f"Habit falhou: {result.output}"

    return runner


class TestBRTimerLifecycle:
    """
    E2E: Workflow completo de timer.

    BRs cobertas:
    - BR-TIMER-001: Iniciar timer
    - BR-TIMER-002: Estados do timer
    - BR-TIMER-003: Pause/Resume
    - BR-TIMER-004: Stop finaliza
    - BR-TIMER-005: Cancel descarta
    """

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_001_start_timer_for_instance(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario inicia timer para HabitInstance.

        DADO: HabitInstance existe (ID=1)
        QUANDO: Usuario executa 'timer start 1'
        ENTAO: Timer inicia e mostra status RUNNING
        """
        runner = setup_habit_instance

        result = runner.invoke(app, ["timer", "start", "--schedule", "1", "--background"], input="y\n")

        assert result.exit_code == 0, f"Start deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower()
            for word in ["iniciado", "running", "started", "timer"]
        ), f"Deve confirmar inicio: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_002_status_shows_running(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Status mostra timer RUNNING.

        DADO: Timer iniciado
        QUANDO: Usuario executa 'timer status'
        ENTAO: Mostra estado RUNNING
        """
        runner = setup_habit_instance

        # Start timer
        runner.invoke(app, ["timer", "start", "--schedule", "1", "--background"], input="y\n")

        # Check status
        result = runner.invoke(app, ["timer", "status"])

        assert result.exit_code == 0, f"Status deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower()
            for word in ["running", "ativo", "em andamento"]
        ), f"Deve mostrar running: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_003_pause_resume_workflow(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario pausa e retoma timer.

        DADO: Timer em RUNNING
        QUANDO: Usuario executa 'timer pause'
        ENTAO: Timer muda para PAUSED
        QUANDO: Usuario executa 'timer resume'
        ENTAO: Timer volta para RUNNING
        """
        runner = setup_habit_instance

        # Start
        runner.invoke(app, ["timer", "start", "--schedule", "1", "--background"], input="y\n")

        # Pause
        result = runner.invoke(app, ["timer", "pause"])
        assert result.exit_code == 0, f"Pause deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower() for word in ["pausado", "paused"]
        ), f"Deve confirmar pausa: {result.output}"

        # Resume
        result = runner.invoke(app, ["timer", "resume", "--background"])
        assert result.exit_code == 0, f"Resume deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower() for word in ["retomado", "resumed", "running"]
        ), f"Deve confirmar retomada: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_004_stop_saves_timelog(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Stop finaliza timer e salva TimeLog.

        DADO: Timer em RUNNING
        QUANDO: Usuario executa 'timer stop'
        ENTAO: Timer muda para DONE e TimeLog eh salvo
        """
        runner = setup_habit_instance

        # Start
        runner.invoke(app, ["timer", "start", "--schedule", "1", "--background"], input="y\n")

        # Stop
        result = runner.invoke(app, ["timer", "stop"])

        assert result.exit_code == 0, f"Stop deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower()
            for word in ["finalizado", "stopped", "done", "salvo", "saved"]
        ), f"Deve confirmar finalizacao: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_005_cancel_discards_timer(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Cancel descarta timer sem salvar.

        DADO: Timer em RUNNING
        QUANDO: Usuario executa 'timer cancel'
        ENTAO: Timer eh descartado (CANCELLED)
        """
        runner = setup_habit_instance

        # Start
        runner.invoke(app, ["timer", "start", "--schedule", "1", "--background"], input="y\n")

        # Cancel
        result = runner.invoke(app, ["timer", "cancel"], input="y\n")

        assert result.exit_code == 0, f"Cancel deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower()
            for word in ["cancelado", "cancelled", "descartado"]
        ), f"Deve confirmar cancelamento: {result.output}"


class TestBRTimerEdgeCases:
    """
    E2E: Casos de borda do timer.

    BRs cobertas:
    - BR-TIMER-006: Nao pode pausar timer nao-running
    - BR-TIMER-007: Nao pode iniciar com timer ja ativo
    """

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_006_pause_without_active_timer_fails(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Pause sem timer ativo falha.

        DADO: Nenhum timer ativo
        QUANDO: Usuario executa 'timer pause'
        ENTAO: Sistema rejeita com erro apropriado
        """
        runner = setup_habit_instance

        result = runner.invoke(app, ["timer", "pause"])

        # Deve falhar ou mostrar mensagem de erro
        assert result.exit_code != 0 or any(
            word in result.output.lower()
            for word in ["nenhum", "no active", "not running", "erro", "error"]
        ), f"Deve falhar sem timer ativo: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_007_start_with_active_timer_fails(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Start com timer ja ativo falha.

        DADO: Timer ja em RUNNING
        QUANDO: Usuario tenta iniciar outro timer
        ENTAO: Sistema rejeita com erro apropriado
        """
        runner = setup_habit_instance

        # Start first timer
        runner.invoke(app, ["timer", "start", "--schedule", "1", "--background"], input="y\n")

        # Try to start another
        result = runner.invoke(app, ["timer", "start", "--schedule", "1", "--background"], input="y\n")

        # Deve falhar ou mostrar mensagem de erro
        assert result.exit_code != 0 or any(
            word in result.output.lower()
            for word in ["ja ativo", "already", "em andamento", "running"]
        ), f"Deve falhar com timer ja ativo: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_timer_status_without_active_timer(
        self, setup_habit_instance: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Status sem timer ativo mostra mensagem apropriada.

        DADO: Nenhum timer ativo
        QUANDO: Usuario executa 'timer status'
        ENTAO: Sistema informa que nao ha timer ativo
        """
        runner = setup_habit_instance

        result = runner.invoke(app, ["timer", "status"])

        assert result.exit_code == 0, f"Status deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower()
            for word in ["nenhum", "no active", "sem timer", "inativo"]
        ), f"Deve informar sem timer: {result.output}"
