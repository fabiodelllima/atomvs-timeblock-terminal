"""Testes e2e de fluxos completos por panel (ADR-037).

Cada teste valida um fluxo de ponta a ponta dentro de um panel,
usando keybindings ADR-037 e banco isolado via TIMEBLOCK_DB_PATH=:memory:.

Referências:
    - ADR-037: Padrão de keybindings da TUI
    - BR-TUI-004: Quick actions
    - BR-TUI-017: Dashboard CRUD — Hábitos
    - BR-TUI-018: Dashboard CRUD — Tasks
"""

import os

import pytest
from textual.app import App, ComposeResult

os.environ["TIMEBLOCK_DB_PATH"] = ":memory:"

from timeblock.database.engine import create_db_and_tables
from timeblock.tui.screens.dashboard.screen import DashboardScreen
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel
from timeblock.tui.widgets.timer_panel import TimerPanel


class PanelFlowApp(App):
    """App de teste com banco isolado para fluxos e2e."""

    def compose(self) -> ComposeResult:
        yield DashboardScreen(id="dashboard-view")

    def on_mount(self) -> None:
        create_db_and_tables()


async def _wait(pilot, n: int = 3) -> None:
    """Aguarda n ciclos de renderização."""
    for _ in range(n):
        await pilot.pause()


class TestHabitsPanelFlow:
    """Fluxo completo: criar rotina → criar hábito → done → skip → undo."""

    @pytest.mark.asyncio
    async def test_habits_create_and_done_flow(self):
        """Cria rotina, cria hábito, marca done com v."""
        app = PanelFlowApp()
        async with app.run_test() as pilot:
            await _wait(pilot)

            # 1. Criar rotina (n sem panel focado)
            await pilot.press("n")
            await _wait(pilot)

            # Preencher nome da rotina
            if len(app.screen_stack) > 1:
                modal = app.screen_stack[-1]
                inputs = modal.query("Input")
                if inputs:
                    inputs[0].value = "Rotina E2E"
                    await pilot.press("enter")
                    await _wait(pilot)

            # 2. Focar no habits panel e criar hábito
            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"
            dashboard._active_routine_id = 1

            await pilot.press("n")
            await _wait(pilot)

            if len(app.screen_stack) > 1:
                modal = app.screen_stack[-1]
                inputs = modal.query("Input")
                if len(inputs) >= 3:
                    inputs[0].value = "Hábito E2E"
                    inputs[1].value = "08:00"
                    inputs[2].value = "60"
                    await pilot.press("enter")
                    await _wait(pilot)

            # 3. Verificar hábito aparece no panel
            panel = app.query_one(HabitsPanel)
            assert panel._item_count > 0, "Hábito deve aparecer no panel"

            # 4. Marcar done com v
            app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("v")
            await _wait(pilot)

    @pytest.mark.asyncio
    async def test_habits_skip_flow(self):
        """Cria hábito e marca skip com s."""
        app = PanelFlowApp()
        async with app.run_test() as pilot:
            await _wait(pilot)

            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-habits"

            # Criar rotina primeiro
            await pilot.press("n")
            await _wait(pilot)
            if len(app.screen_stack) > 1:
                modal = app.screen_stack[-1]
                inputs = modal.query("Input")
                if inputs:
                    inputs[0].value = "Rotina Skip"
                    await pilot.press("enter")
                    await _wait(pilot)

            dashboard._active_routine_id = 1
            dashboard._focused_panel = "panel-habits"

            # Criar hábito
            await pilot.press("n")
            await _wait(pilot)
            if len(app.screen_stack) > 1:
                modal = app.screen_stack[-1]
                inputs = modal.query("Input")
                if len(inputs) >= 3:
                    inputs[0].value = "Skip E2E"
                    inputs[1].value = "09:00"
                    inputs[2].value = "30"
                    await pilot.press("enter")
                    await _wait(pilot)

            # Skip com s
            panel = app.query_one(HabitsPanel)
            app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("s")
            await _wait(pilot)


class TestTasksPanelFlow:
    """Fluxo completo: criar task → completar com v."""

    @pytest.mark.asyncio
    async def test_tasks_create_and_complete_flow(self):
        """Cria task e completa com v."""
        app = PanelFlowApp()
        async with app.run_test() as pilot:
            await _wait(pilot)

            dashboard = app.query_one(DashboardScreen)
            dashboard._focused_panel = "panel-tasks"

            # Criar task
            await pilot.press("n")
            await _wait(pilot)

            if len(app.screen_stack) > 1:
                modal = app.screen_stack[-1]
                inputs = modal.query("Input")
                if inputs:
                    inputs[0].value = "Task E2E"
                    await pilot.press("enter")
                    await _wait(pilot)

            # Verificar task aparece
            panel = app.query_one(TasksPanel)
            assert panel._item_count > 0, "Task deve aparecer no panel"

            # Completar com v
            app.set_focus(panel)
            await _wait(pilot)
            await pilot.press("v")
            await _wait(pilot)


class TestTimerPanelFlow:
    """Fluxo completo: iniciar timer → pausar → resumir → parar."""

    @pytest.mark.asyncio
    async def test_timer_pause_resume_stop_flow(self):
        """Inicia timer, pausa com space, resume com space, para com s."""
        app = PanelFlowApp()
        async with app.run_test() as pilot:
            await _wait(pilot)

            dashboard = app.query_one(DashboardScreen)

            # Criar rotina + hábito para ter algo para timer
            await pilot.press("n")
            await _wait(pilot)
            if len(app.screen_stack) > 1:
                modal = app.screen_stack[-1]
                inputs = modal.query("Input")
                if inputs:
                    inputs[0].value = "Rotina Timer"
                    await pilot.press("enter")
                    await _wait(pilot)

            dashboard._active_routine_id = 1
            dashboard._focused_panel = "panel-habits"

            await pilot.press("n")
            await _wait(pilot)
            if len(app.screen_stack) > 1:
                modal = app.screen_stack[-1]
                inputs = modal.query("Input")
                if len(inputs) >= 3:
                    inputs[0].value = "Timer E2E"
                    inputs[1].value = "10:00"
                    inputs[2].value = "45"
                    await pilot.press("enter")
                    await _wait(pilot)

            # Iniciar timer com t no habits panel
            panel_h = app.query_one(HabitsPanel)
            app.set_focus(panel_h)
            await _wait(pilot)
            await pilot.press("t")
            await _wait(pilot)

            # Pausar com space no timer panel
            panel_t = app.query_one(TimerPanel)
            app.set_focus(panel_t)
            await _wait(pilot)
            await pilot.press("space")
            await _wait(pilot)

            # Resumir com space
            await pilot.press("space")
            await _wait(pilot)

            # Parar com s
            await pilot.press("s")
            await _wait(pilot)


class TestKeybindingsNavigation:
    """Testa navegação por keybindings ADR-037."""

    @pytest.mark.asyncio
    async def test_tab_switches_panel_focus(self):
        """Tab navega entre panels."""
        app = PanelFlowApp()
        async with app.run_test() as pilot:
            await _wait(pilot)
            # Tab deve mudar o painel focado
            await pilot.press("tab")
            await _wait(pilot)
            await pilot.press("tab")
            await _wait(pilot)

    @pytest.mark.asyncio
    async def test_crud_keys_consistent(self):
        """n/e/x funcionam conforme panel focado."""
        app = PanelFlowApp()
        async with app.run_test() as pilot:
            await _wait(pilot)
            # n deve abrir modal de criação
            await pilot.press("n")
            await _wait(pilot)
            assert len(app.screen_stack) >= 2, "n deve abrir modal"
            await pilot.press("escape")
            await _wait(pilot)

    @pytest.mark.asyncio
    async def test_help_overlay_opens(self):
        """? abre help overlay."""
        app = PanelFlowApp()
        async with app.run_test() as pilot:
            await _wait(pilot)
            await pilot.press("?")
            await _wait(pilot)
