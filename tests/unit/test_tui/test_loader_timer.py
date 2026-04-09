"""Tests for load_active_timer (DT-016).

Valida que load_active_timer retorna dict com elapsed formatado
como MM:SS ou HH:MM:SS e nome do hábito associado ao timer.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from timeblock.tui.screens.dashboard.loader import load_active_timer


def _make_timer(
    *,
    minutes: int = 5,
    seconds: int = 30,
    status: str = "running",
    paused: int = 0,
    habit_instance_id: int | None = 42,
) -> SimpleNamespace:
    """Cria objeto simulando TimeLog retornado por TimerService."""
    return SimpleNamespace(
        id=1,
        start_time=datetime.now() - timedelta(minutes=minutes, seconds=seconds),
        status=SimpleNamespace(value=status),
        paused_duration=paused,
        habit_instance_id=habit_instance_id,
    )


def _make_instance(title: str = "Academia") -> MagicMock:
    """Cria objeto simulando HabitInstance com Habit relationship."""
    inst = MagicMock()
    inst.habit.title = title
    return inst


class TestDT016LoadActiveTimer:
    """DT-016: load_active_timer retorna elapsed MM:SS e nome do hábito."""

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt016_returns_formatted_elapsed(self, mock_sa, mock_ts):
        """Elapsed é string no formato MM:SS, não int."""
        timer = _make_timer(minutes=5, seconds=30)
        instance = _make_instance("Academia")
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        elapsed = result["elapsed"]
        assert isinstance(elapsed, str)
        assert ":" in elapsed
        parts = elapsed.split(":")
        assert len(parts) == 2
        assert all(p.isdigit() for p in parts)

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt016_returns_habit_name(self, mock_sa, mock_ts):
        """Nome do hábito associado ao timer é retornado."""
        timer = _make_timer()
        instance = _make_instance("Academia")
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        assert result["name"] == "Academia"

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt016_returns_none_without_active_timer(self, mock_sa):
        """Sem timer ativo retorna None."""
        mock_sa.return_value = (None, None)
        result = load_active_timer()
        assert result is None

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_dt016_elapsed_seconds_also_present(self, mock_sa, mock_ts):
        """elapsed_seconds (int) é mantido para compatibilidade."""
        timer = _make_timer(minutes=2, seconds=15)
        instance = _make_instance()
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        assert isinstance(result["elapsed_seconds"], int)
        assert result["elapsed_seconds"] >= 0


class TestBugTimerHoursFormat:
    """Bug #5: TimerPanel não converte >60min para HH:MM:SS."""

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_bug_005_elapsed_over_60min_shows_hours(self, mock_sa, mock_ts):
        """Timer com 67min55s deve retornar '01:07:55', não '67:55'."""
        timer = _make_timer(minutes=67, seconds=55)
        instance = _make_instance("Estudo")
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        elapsed = result["elapsed"]
        assert ":" in elapsed
        parts = elapsed.split(":")
        assert len(parts) == 3, f"Esperava HH:MM:SS, obteve {elapsed}"
        hours, mins, secs = parts
        assert hours == "01"
        assert mins == "07"
        assert int(secs) >= 54  # margem de 1s pela execução

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_bug_005_elapsed_under_60min_keeps_mmss(self, mock_sa, mock_ts):
        """Timer com <60min mantém formato MM:SS."""
        timer = _make_timer(minutes=45, seconds=30)
        instance = _make_instance("Leitura")
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        elapsed = result["elapsed"]
        parts = elapsed.split(":")
        assert len(parts) == 2, f"Esperava MM:SS, obteve {elapsed}"

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_bug_005_elapsed_exactly_60min(self, mock_sa, mock_ts):
        """Timer com exatamente 60min retorna 01:00:00."""
        timer = _make_timer(minutes=60, seconds=0)
        instance = _make_instance("Exercício")
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        elapsed = result["elapsed"]
        parts = elapsed.split(":")
        assert len(parts) == 3, f"Esperava HH:MM:SS, obteve {elapsed}"
        assert parts[0] == "01"
        assert parts[1] == "00"

    @patch("timeblock.tui.screens.dashboard.loader.TimerService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_bug_005_elapsed_over_10_hours(self, mock_sa, mock_ts):
        """Timer com 10h30min retorna 10:30:XX."""
        timer = _make_timer(minutes=630, seconds=0)
        instance = _make_instance("Maratona")
        mock_ts.get_any_active_timer.return_value = timer

        def side_effect(fn):
            session = MagicMock()
            session.exec.return_value.first.return_value = instance
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = load_active_timer()

        assert result is not None
        elapsed = result["elapsed"]
        parts = elapsed.split(":")
        assert len(parts) == 3, f"Esperava HH:MM:SS, obteve {elapsed}"
        assert parts[0] == "10"
        assert parts[1] == "30"
