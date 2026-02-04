"""Testes unitários para habit/display.py.

Valida funções de formatação e exibição de instâncias de hábito.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from timeblock.commands.habit.display import (
    _resolve_date_range,
    _resolve_status_filter,
    display_instances,
    display_log_result,
    handle_log_error,
)
from timeblock.models.enums import Status


class TestResolveDateRange:
    """Testes para _resolve_date_range."""

    def test_today_returns_same_date(self):
        """--today retorna data atual para início e fim."""
        start, end = _resolve_date_range(today=True, week=False, habit_id=None)
        assert start == date.today()
        assert end == date.today()

    def test_week_returns_7_days(self):
        """--week retorna período de 7 dias."""
        start, end = _resolve_date_range(today=False, week=True, habit_id=None)
        assert start == date.today()
        assert end == date.today() + timedelta(days=6)

    def test_no_habit_id_defaults_to_week(self):
        """Sem habit_id, default é semana."""
        start, end = _resolve_date_range(today=False, week=False, habit_id=None)
        assert start == date.today()
        assert end == date.today() + timedelta(days=6)

    def test_with_habit_id_returns_none(self):
        """Com habit_id específico, retorna None (todas as datas)."""
        start, end = _resolve_date_range(today=False, week=False, habit_id=1)
        assert start is None
        assert end is None

    def test_today_and_week_raises_error(self):
        """--today e --week são mutuamente exclusivos."""
        with pytest.raises(ValueError, match="mutuamente exclusivos"):
            _resolve_date_range(today=True, week=True, habit_id=None)


class TestResolveStatusFilter:
    """Testes para _resolve_status_filter."""

    def test_pending_returns_pending_status(self):
        """--pending retorna Status.PENDING."""
        result = _resolve_status_filter(pending=True, done=False, all_status=False, habit_id=None)
        assert result == Status.PENDING

    def test_done_returns_done_status(self):
        """--done retorna Status.DONE."""
        result = _resolve_status_filter(pending=False, done=True, all_status=False, habit_id=None)
        assert result == Status.DONE

    def test_all_status_returns_none(self):
        """--all retorna None (sem filtro)."""
        result = _resolve_status_filter(pending=False, done=False, all_status=True, habit_id=None)
        assert result is None

    def test_no_flags_no_habit_defaults_to_pending(self):
        """Sem flags e sem habit_id, default é PENDING."""
        result = _resolve_status_filter(pending=False, done=False, all_status=False, habit_id=None)
        assert result == Status.PENDING

    def test_with_habit_id_returns_none(self):
        """Com habit_id, retorna None (todas)."""
        result = _resolve_status_filter(pending=False, done=False, all_status=False, habit_id=1)
        assert result is None

    def test_pending_and_done_raises_error(self):
        """--pending e --done são mutuamente exclusivos."""
        with pytest.raises(ValueError, match="mutuamente exclusivos"):
            _resolve_status_filter(pending=True, done=True, all_status=False, habit_id=None)


class TestDisplayInstances:
    """Testes para display_instances."""

    @patch("timeblock.commands.habit.display.console")
    def test_empty_list_prints_message(self, mock_console):
        """Lista vazia exibe mensagem apropriada."""
        display_instances([], today=False, week=False, habit_id=None, status_filter=None)
        mock_console.print.assert_called_once()
        assert "Nenhuma instância" in str(mock_console.print.call_args)

    @patch("timeblock.commands.habit.display.console")
    def test_empty_list_with_habit_id(self, mock_console):
        """Lista vazia com habit_id menciona o ID."""
        display_instances([], today=False, week=False, habit_id=42, status_filter=None)
        mock_console.print.assert_called_once()
        assert "42" in str(mock_console.print.call_args)

    @patch("timeblock.commands.habit.display.console")
    def test_displays_instances_grouped_by_date(self, mock_console):
        """Instâncias são agrupadas por data."""
        from datetime import time

        mock_habit = MagicMock()
        mock_habit.title = "Meditação"

        mock_instance = MagicMock()
        mock_instance.date = date.today()
        mock_instance.scheduled_start = time(8, 0)
        mock_instance.scheduled_end = time(8, 30)
        mock_instance.status = Status.PENDING
        mock_instance.habit = mock_habit
        mock_instance.id = 1

        display_instances(
            [mock_instance],
            today=True,
            week=False,
            habit_id=None,
            status_filter=Status.PENDING,
        )

        # Verifica que houve múltiplas chamadas (header + instância)
        assert mock_console.print.call_count >= 2


class TestDisplayLogResult:
    """Testes para display_log_result."""

    @patch("timeblock.commands.habit.display.console")
    def test_displays_duration(self, mock_console):
        """Exibe duração formatada."""
        mock_timelog = MagicMock()
        mock_timelog.duration_seconds = 3665  # 1h 1min 5s

        display_log_result(mock_timelog, instance=None)

        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("01h01min" in call for call in calls)

    @patch("timeblock.commands.habit.display.console")
    def test_displays_completion_percentage(self, mock_console):
        """Exibe percentual de conclusão quando há instância."""
        mock_timelog = MagicMock()
        mock_timelog.duration_seconds = 1800

        mock_instance = MagicMock()
        mock_instance.completion_percentage = 75
        mock_instance.done_substatus = None

        display_log_result(mock_timelog, mock_instance)

        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("75%" in call for call in calls)


class TestHandleLogError:
    """Testes para handle_log_error."""

    @patch("timeblock.commands.habit.display.console")
    def test_not_found_error(self, mock_console):
        """Erro 'not found' exibe mensagem específica."""
        error = ValueError("Instance not found")
        handle_log_error(error, instance_id=99)

        calls = str(mock_console.print.call_args)
        assert "99" in calls
        assert "não encontrada" in calls

    @patch("timeblock.commands.habit.display.console")
    def test_start_before_end_error(self, mock_console):
        """Erro de ordem de horário exibe mensagem."""
        error = ValueError("start must be before end")
        handle_log_error(error, instance_id=1)

        calls = str(mock_console.print.call_args)
        assert "anterior" in calls

    @patch("timeblock.commands.habit.display.console")
    def test_duration_positive_error(self, mock_console):
        """Erro de duração exibe mensagem."""
        error = ValueError("duration must be positive")
        handle_log_error(error, instance_id=1)

        calls = str(mock_console.print.call_args)
        assert "maior que zero" in calls

    @patch("timeblock.commands.habit.display.console")
    def test_generic_error(self, mock_console):
        """Erro genérico exibe mensagem original."""
        error = ValueError("Algo inesperado")
        handle_log_error(error, instance_id=1)

        calls = str(mock_console.print.call_args)
        assert "Algo inesperado" in calls
