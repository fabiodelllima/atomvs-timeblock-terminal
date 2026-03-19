"""Tests para DT-054, DT-055, DT-049 — fixes críticos do loader.

DT-054: Timer pausado congela elapsed (não continua contando).
DT-055: load_instances detecta timer ativo e sobrescreve status.
DT-049: load_instances filtra por routine_id.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from timeblock.models.enums import TimerStatus
from timeblock.tui.screens.dashboard.loader import load_active_timer, load_instances

# =========================================================================
# Helpers
# =========================================================================


def _make_timer(
    *,
    minutes: int = 5,
    seconds: int = 30,
    status: TimerStatus = TimerStatus.RUNNING,
    paused: int = 0,
    pause_start: datetime | None = None,
    habit_instance_id: int | None = 42,
) -> SimpleNamespace:
    """Cria objeto simulando TimeLog com TimerStatus real."""
    return SimpleNamespace(
        id=1,
        start_time=datetime.now() - timedelta(minutes=minutes, seconds=seconds),
        status=status,
        paused_duration=paused,
        pause_start=pause_start,
        habit_instance_id=habit_instance_id,
    )


def _make_instance(
    *,
    inst_id: int = 42,
    title: str = "Academia",
    routine_id: int = 1,
    status_value: str = "pending",
) -> MagicMock:
    """Cria objeto simulando HabitInstance com Habit relationship."""
    inst = MagicMock()
    inst.id = inst_id
    inst.habit_id = inst_id
    inst.habit.title = title
    inst.habit.routine_id = routine_id
    inst.scheduled_start = MagicMock(hour=8, minute=0)
    inst.scheduled_end = MagicMock(hour=9, minute=0)
    inst.status = MagicMock(value=status_value)
    inst.done_substatus = None
    inst.not_done_substatus = None
    inst.actual_duration = None
    inst.date = datetime.now().date()
    return inst


# =========================================================================
# DT-054: Timer pause congela elapsed
# =========================================================================


class TestDT054TimerPauseFreezesElapsed:
    """DT-054: Elapsed não cresce enquanto timer está pausado."""

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt054_paused_timer_subtracts_current_pause(self, mock_sa, mock_ts):
        """Timer pausado há 2min com 5min prévios: elapsed ~3min, não ~5min."""
        pause_start = datetime.now() - timedelta(minutes=2)
        timer = _make_timer(
            minutes=5,
            seconds=0,
            status=TimerStatus.PAUSED,
            paused=0,
            pause_start=pause_start,
        )
        instance = MagicMock()
        instance.habit.title = "Academia"
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        # 5min total - 2min pausa corrente = ~3min (180s)
        assert result["elapsed_seconds"] < 200, (
            f"Elapsed {result['elapsed_seconds']}s deveria ser ~180s, "
            "não ~300s — pausa corrente não descontada"
        )
        assert result["elapsed_seconds"] >= 170, f"Elapsed {result['elapsed_seconds']}s muito baixo"

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt054_paused_with_prior_paused_duration(self, mock_sa, mock_ts):
        """Timer com 60s de pausa prévia + 30s de pausa corrente."""
        pause_start = datetime.now() - timedelta(seconds=30)
        timer = _make_timer(
            minutes=3,
            seconds=0,
            status=TimerStatus.PAUSED,
            paused=60,
            pause_start=pause_start,
        )
        instance = MagicMock()
        instance.habit.title = "Leitura"
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        # 180s total - 60s prévio - 30s corrente = ~90s
        assert result["elapsed_seconds"] < 100
        assert result["elapsed_seconds"] >= 80

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt054_running_timer_unchanged(self, mock_sa, mock_ts):
        """Timer running (não pausado) mantém cálculo original."""
        timer = _make_timer(
            minutes=2,
            seconds=0,
            status=TimerStatus.RUNNING,
            paused=0,
            pause_start=None,
        )
        instance = MagicMock()
        instance.habit.title = "Treino"
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        assert result["elapsed_seconds"] >= 115
        assert result["elapsed_seconds"] <= 125


# =========================================================================
# DT-055: load_instances detecta timer ativo
# =========================================================================


class TestDT055LoadInstancesTimerDetection:
    """DT-055: Instância com timer ativo recebe status 'running'/'paused'."""

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt055_running_timer_overrides_status(self, mock_sa, mock_his):
        """Instância com timer RUNNING aparece com status 'running'."""
        inst = _make_instance(inst_id=42)
        timer_log = MagicMock()
        timer_log.habit_instance_id = 42
        timer_log.status = TimerStatus.RUNNING

        his_instance = MagicMock()
        his_instance.list_instances.return_value = [inst]
        mock_his.return_value = his_instance

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = timer_log
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_instances()

        assert len(result) == 1
        assert result[0]["status"] == "running", (
            f"Status deveria ser 'running', não '{result[0]['status']}'"
        )

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt055_paused_timer_overrides_status(self, mock_sa, mock_his):
        """Instância com timer PAUSED aparece com status 'paused'."""
        inst = _make_instance(inst_id=42)
        timer_log = MagicMock()
        timer_log.habit_instance_id = 42
        timer_log.status = TimerStatus.PAUSED

        his_instance = MagicMock()
        his_instance.list_instances.return_value = [inst]
        mock_his.return_value = his_instance

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = timer_log
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_instances()

        assert len(result) == 1
        assert result[0]["status"] == "paused"

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt055_no_timer_keeps_original_status(self, mock_sa, mock_his):
        """Sem timer ativo, status permanece o original da instância."""
        inst = _make_instance(inst_id=42, status_value="done")

        his_instance = MagicMock()
        his_instance.list_instances.return_value = [inst]
        mock_his.return_value = his_instance

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = None
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_instances()

        assert len(result) == 1
        assert result[0]["status"] == "done"

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt055_timer_on_different_instance(self, mock_sa, mock_his):
        """Timer ativo em outra instância não afeta a corrente."""
        inst = _make_instance(inst_id=10)
        timer_log = MagicMock()
        timer_log.habit_instance_id = 99
        timer_log.status = TimerStatus.RUNNING

        his_instance = MagicMock()
        his_instance.list_instances.return_value = [inst]
        mock_his.return_value = his_instance

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = timer_log
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_instances()

        assert len(result) == 1
        assert result[0]["status"] == "pending"


# =========================================================================
# DT-049: load_instances filtra por routine_id
# =========================================================================


class TestDT049LoadInstancesRoutineFilter:
    """DT-049: load_instances filtra instâncias pela rotina ativa."""

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt049_filters_by_routine_id(self, mock_sa, mock_his):
        """Apenas instâncias da rotina fornecida são retornadas."""
        inst_a = _make_instance(inst_id=1, title="H_A", routine_id=10)
        inst_b = _make_instance(inst_id=2, title="H_B", routine_id=20)

        his_instance = MagicMock()
        his_instance.list_instances.return_value = [inst_a, inst_b]
        mock_his.return_value = his_instance

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = None
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_instances(routine_id=10)

        assert len(result) == 1
        assert result[0]["name"] == "H_A"

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt049_none_routine_returns_all(self, mock_sa, mock_his):
        """routine_id=None retorna todas as instâncias (backward compat)."""
        inst_a = _make_instance(inst_id=1, routine_id=10)
        inst_b = _make_instance(inst_id=2, routine_id=20)

        his_instance = MagicMock()
        his_instance.list_instances.return_value = [inst_a, inst_b]
        mock_his.return_value = his_instance

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = None
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_instances(routine_id=None)

        assert len(result) == 2

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt049_no_match_returns_empty(self, mock_sa, mock_his):
        """Rotina sem instâncias retorna lista vazia."""
        inst = _make_instance(inst_id=1, routine_id=10)

        his_instance = MagicMock()
        his_instance.list_instances.return_value = [inst]
        mock_his.return_value = his_instance

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = None
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_instances(routine_id=999)

        assert result == []
