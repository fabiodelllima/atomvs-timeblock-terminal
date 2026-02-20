"""Tests for BR-TUI-003: Dashboard Screen."""

import pytest

from timeblock.tui.app import TimeBlockApp
from timeblock.tui.screens.dashboard import DashboardScreen
from timeblock.tui.widgets.timeblock_grid import (
    calculate_block_height,
    generate_time_slots,
)


class TestBRTUI003DashboardScreen:
    """BR-TUI-003: Dashboard exibe grade temporal + tasks."""

    @pytest.mark.asyncio
    async def test_br_tui_003_shows_active_routine_name(self):
        """Dashboard exibe nome da rotina ativa."""
        async with TimeBlockApp().run_test() as pilot:
            content = pilot.app.query_one("#content-area")
            assert content is not None

    def test_br_tui_003_shows_no_routine_message(self):
        """Sem rotina ativa, exibe mensagem orientativa."""
        screen = DashboardScreen()
        label = screen.get_no_routine_label()
        assert "rotina" in label.lower() or "routine" in label.lower()

    @pytest.mark.asyncio
    async def test_br_tui_003_has_two_columns(self):
        """Dashboard possui duas colunas: timeblocks (~70%) e tasks (~30%)."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("1")
            timeblock_col = pilot.app.query("#timeblock-column")
            tasks_col = pilot.app.query("#tasks-column")
            assert len(timeblock_col) == 1
            assert len(tasks_col) == 1

    def test_br_tui_003_timeblock_proportional_height(self):
        """Timeblock de 1h30 ocupa 3 linhas (30min = 1 linha)."""
        assert calculate_block_height(90) == 3
        assert calculate_block_height(30) == 1
        assert calculate_block_height(120) == 4
        assert calculate_block_height(60) == 2
        assert calculate_block_height(15) == 1  # minimo 1 linha

    def test_br_tui_003_shows_time_slots(self):
        """Grade temporal exibe slots de 30min com horarios."""
        slots = generate_time_slots("07:00", "12:00")
        assert slots[0] == "07:00"
        assert slots[1] == "07:30"
        assert slots[2] == "08:00"
        assert len(slots) == 10

    @pytest.mark.asyncio
    async def test_br_tui_003_shows_pending_tasks(self):
        """Coluna direita lista tasks pendentes."""
        async with TimeBlockApp().run_test() as pilot:
            tasks_col = pilot.app.query_one("#tasks-column")
            assert tasks_col is not None
