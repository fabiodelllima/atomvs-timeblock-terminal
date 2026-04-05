"""Testes do CRUD de hábitos via dashboard (BR-TUI-017).

Referências:
    - BR-TUI-017: Dashboard CRUD — Hábitos
    - ADR-019: Test Naming Convention
    - ADR-034: Dashboard-first CRUD
"""

import pytest
from textual.app import App, ComposeResult

from timeblock.tui.screens.dashboard.screen import DashboardScreen


class DashboardHabitsTestApp(App):
    """App de teste para CRUD de hábitos no dashboard."""

    def compose(self) -> ComposeResult:
        yield DashboardScreen(id="dashboard-view")


class TestBRTUI017CRUDHabits:
    """BR-TUI-017: Dashboard CRUD — Hábitos."""

    @pytest.mark.asyncio
    async def test_br_tui_017_n_on_habits_without_routine_opens_routine_form(self):
        """n no panel hábitos sem rotina ativa abre FormModal de rotina (DT-040)."""
        app = DashboardHabitsTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"
            dashboard._active_routine_id = None
            await pilot.press("n")
            await pilot.pause()
            assert len(app.screen_stack) == 2, "Deve abrir FormModal de criação de rotina"

    @pytest.mark.asyncio
    async def test_br_tui_017_n_on_habits_with_routine_opens_form(self):
        """n no panel hábitos com rotina ativa abre FormModal."""
        app = DashboardHabitsTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"
            dashboard._active_routine_id = 1
            await pilot.press("n")
            await pilot.pause()
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_017_form_has_four_fields(self):
        """FormModal de hábito tem 4 campos: título, horário, duração, recorrência."""
        app = DashboardHabitsTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"
            dashboard._active_routine_id = 1
            await pilot.press("n")
            await pilot.pause()
            modal = app.screen_stack[-1]
            inputs = modal.query("Input")
            selects = modal.query("Select")
            assert len(inputs) + len(selects) == 4

    @pytest.mark.asyncio
    async def test_br_tui_017_esc_closes_form(self):
        """Esc no FormModal de hábito fecha sem criar."""
        app = DashboardHabitsTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"
            dashboard._active_routine_id = 1
            await pilot.press("n")
            await pilot.pause()
            assert len(app.screen_stack) == 2
            await pilot.press("escape")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_017_e_without_selection_no_modal(self):
        """e no panel hábitos sem item selecionado não abre modal."""
        app = DashboardHabitsTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"
            await pilot.press("e")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_017_x_without_selection_no_modal(self):
        """x no panel hábitos sem item selecionado não abre modal."""
        app = DashboardHabitsTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"
            await pilot.press("x")
            await pilot.pause()
            assert len(app.screen_stack) == 1
