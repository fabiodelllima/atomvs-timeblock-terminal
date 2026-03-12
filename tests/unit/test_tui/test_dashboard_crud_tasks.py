"""Testes do CRUD de tarefas via dashboard (BR-TUI-018).

Referências:
    - BR-TUI-018: Dashboard CRUD — Tarefas
    - ADR-019: Test Naming Convention
    - ADR-034: Dashboard-first CRUD
"""

from datetime import date

import pytest
from textual.app import App, ComposeResult

from timeblock.tui.screens.dashboard.screen import DashboardScreen


class DashboardTasksTestApp(App):
    """App de teste para CRUD de tarefas no dashboard."""

    def compose(self) -> ComposeResult:
        yield DashboardScreen(id="dashboard-view")


class TestBRTUI018CRUDTasks:
    """BR-TUI-018: Dashboard CRUD — Tarefas."""

    @pytest.mark.asyncio
    async def test_br_tui_018_n_on_tasks_opens_form(self):
        """n no panel tarefas abre FormModal."""
        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            await pilot.press("n")
            await pilot.pause()
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_018_form_has_three_fields(self):
        """FormModal de tarefa tem 3 campos: título, data, horário."""
        from textual.widgets import Input

        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            await pilot.press("n")
            await pilot.pause()
            inputs = app.screen.query(Input)
            assert len(inputs) == 3

    @pytest.mark.asyncio
    async def test_br_tui_018_esc_closes_form(self):
        """Esc fecha FormModal de tarefa sem criar."""
        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            await pilot.press("n")
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_018_e_without_selection_no_modal(self):
        """e no panel tarefas sem seleção não abre modal."""
        from timeblock.tui.widgets.tasks_panel import TasksPanel

        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            # Panel vazio — get_selected_item() retorna None
            tasks_panel = app.query_one(TasksPanel)
            tasks_panel.update_data([])
            await pilot.press("e")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_018_x_without_selection_no_modal(self):
        """x no panel tarefas sem seleção não abre modal."""
        from timeblock.tui.widgets.tasks_panel import TasksPanel

        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            tasks_panel = app.query_one(TasksPanel)
            tasks_panel.update_data([])
            await pilot.press("x")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_018_validation_title_required(self):
        """Submit sem título mantém modal aberto com erro."""
        from textual.widgets import Input

        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            await pilot.press("n")
            await pilot.pause()
            # Limpa campo título e tenta submeter
            title_input = app.screen.query_one("#fm-input-title", Input)
            await pilot.click(title_input)
            title_input.clear()
            await pilot.press("enter")
            await pilot.pause()
            # Modal permanece aberto
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_018_coexists_with_ctrl_k(self):
        """O ctrl+enter não é interceptado pelo dispatcher de tarefas."""
        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            await pilot.press("ctrl+enter")
            await pilot.pause()
            # ctrl+enter não deve abrir modal de CRUD
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_018_n_opens_form_with_date_default(self):
        """FormModal de nova tarefa traz data default igual a hoje (DD/MM)."""
        from textual.widgets import Input

        app = DashboardTasksTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"
            await pilot.press("n")
            await pilot.pause()
            date_input = app.screen.query_one("#fm-input-date", Input)
            today = date.today()
            expected = f"{today.day:02d}/{today.month:02d}"
            assert date_input.value == expected
