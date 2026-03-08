"""Testes do CRUD de rotinas via dashboard (BR-TUI-016).

Referências:
    - BR-TUI-016: Dashboard CRUD — Rotinas
    - ADR-019: Test Naming Convention
    - ADR-034: Dashboard-first CRUD
"""

import pytest
from textual.app import App, ComposeResult

from timeblock.tui.screens.dashboard.screen import DashboardScreen


class DashboardCRUDTestApp(App):
    """App de teste para CRUD no dashboard."""

    def compose(self) -> ComposeResult:
        yield DashboardScreen(id="dashboard-view")


class TestBRTUI016CRUDRoutines:
    """BR-TUI-016: Dashboard CRUD — Rotinas."""

    @pytest.mark.asyncio
    async def test_br_tui_016_n_on_dashboard_opens_routine_form(self):
        """n sem panel focado abre FormModal de rotina."""
        app = DashboardCRUDTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_016_no_routine_shows_hint(self):
        """Sem rotina ativa, get_no_routine_label retorna hint com n."""
        label = DashboardScreen.get_no_routine_label()
        assert "n" in label

    @pytest.mark.asyncio
    async def test_br_tui_016_e_without_routine_does_nothing(self):
        """e sem rotina ativa não abre modal."""
        app = DashboardCRUDTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("e")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_016_x_without_routine_does_nothing(self):
        """x sem rotina ativa não abre modal."""
        app = DashboardCRUDTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_016_form_modal_has_name_field(self):
        """FormModal de rotina tem campo nome."""
        app = DashboardCRUDTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            modal = app.screen_stack[-1]
            inputs = modal.query("Input")
            assert len(inputs) == 1

    @pytest.mark.asyncio
    async def test_br_tui_016_esc_closes_form_modal(self):
        """Esc no FormModal fecha sem criar rotina."""
        app = DashboardCRUDTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            assert len(app.screen_stack) == 2
            await pilot.press("escape")
            await pilot.pause()
            assert len(app.screen_stack) == 1
