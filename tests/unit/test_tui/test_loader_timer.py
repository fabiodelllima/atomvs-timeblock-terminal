"""Tests for load_active_timer (DT-016).

Valida que load_active_timer retorna dict com elapsed formatado
como MM:SS e nome do hábito associado ao timer.
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
