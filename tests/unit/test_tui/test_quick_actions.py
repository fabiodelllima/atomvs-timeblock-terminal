"""Testes das quick actions via message pattern no dashboard (RF-001, BR-TUI-004).

Valida que HabitsPanel e TasksPanel emitem mensagens Textual
em vez de chamar services diretamente.

Referências:
    - BR-TUI-004: Quick Actions
    - RF-001: Extract Delegate (FOWLER, 2018, p. 182)
    - ADR-034: Dashboard-first CRUD
"""

import pytest
from textual.app import App, ComposeResult

from timeblock.tui.screens.dashboard.screen import DashboardScreen
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel


class QuickActionsTestApp(App):
    """App de teste para quick actions."""

    def compose(self) -> ComposeResult:
        yield DashboardScreen(id="dashboard-view")


class TestRF001HabitsQuickActions:
    """RF-001: HabitsPanel emite mensagens em vez de chamar services."""

    @pytest.mark.asyncio
    async def test_rf001_habits_panel_has_habit_done_request_message(self):
        """HabitsPanel define mensagem interna HabitDoneRequest."""
        assert hasattr(HabitsPanel, "HabitDoneRequest")

    @pytest.mark.asyncio
    async def test_rf001_habits_panel_has_habit_skip_request_message(self):
        """HabitsPanel define mensagem interna HabitSkipRequest."""
        assert hasattr(HabitsPanel, "HabitSkipRequest")

    @pytest.mark.asyncio
    async def test_rf001_ctrl_enter_posts_habit_done_request(self):
        """Ctrl+Enter com item selecionado posta HabitDoneRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_habits_panel_habit_done_request(
                self, message: HabitsPanel.HabitDoneRequest
            ) -> None:
                received.append(message.instance_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel._instances = [{"id": 42, "name": "Teste", "status": "pending"}]
            panel._set_item_count(1)
            app.set_focus(panel)
            await pilot.press("ctrl+enter")
            await pilot.pause()
        assert received == [42]

    @pytest.mark.asyncio
    async def test_rf001_ctrl_s_posts_habit_skip_request(self):
        """Ctrl+S com item selecionado posta HabitSkipRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_habits_panel_habit_skip_request(
                self, message: HabitsPanel.HabitSkipRequest
            ) -> None:
                received.append(message.instance_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel._instances = [{"id": 7, "name": "Teste", "status": "pending"}]
            panel._set_item_count(1)
            app.set_focus(panel)
            await pilot.press("ctrl+s")
            await pilot.pause()
        assert received == [7]

    @pytest.mark.asyncio
    async def test_rf001_ctrl_enter_without_selection_no_message(self):
        """Ctrl+Enter sem item selecionado não posta mensagem."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_habits_panel_habit_done_request(
                self, message: HabitsPanel.HabitDoneRequest
            ) -> None:
                received.append(message.instance_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel._instances = []
            panel._set_item_count(0)
            app.set_focus(panel)
            await pilot.press("ctrl+enter")
            await pilot.pause()
        assert received == []

    @pytest.mark.asyncio
    async def test_rf001_habits_panel_no_service_import_at_module_level(self):
        """HabitsPanel não importa services no nível de módulo."""
        import importlib
        import sys

        # Garante que o modulo nao tem dependencia direta de services
        mod = sys.modules.get("timeblock.tui.widgets.habits_panel")
        if mod is None:
            mod = importlib.import_module("timeblock.tui.widgets.habits_panel")
        source_file = mod.__file__ or ""
        with open(source_file) as f:
            source = f.read()
        assert "from timeblock.services" not in source
        assert "import HabitInstanceService" not in source


class TestRF001TasksQuickActions:
    """RF-001: TasksPanel emite mensagem em vez de chamar service."""

    @pytest.mark.asyncio
    async def test_rf001_tasks_panel_has_task_complete_request_message(self):
        """TasksPanel define mensagem interna TaskCompleteRequest."""
        assert hasattr(TasksPanel, "TaskCompleteRequest")

    @pytest.mark.asyncio
    async def test_rf001_ctrl_k_posts_task_complete_request(self):
        """Ctrl+Enter com item selecionado posta TaskCompleteRequest."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_tasks_panel_task_complete_request(
                self, message: TasksPanel.TaskCompleteRequest
            ) -> None:
                received.append(message.task_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TasksPanel)
            panel.update_data(
                [
                    {
                        "id": 99,
                        "name": "Tarefa",
                        "status": "pending",
                        "days": 0,
                        "proximity": "Hoje",
                        "date": "08/03",
                        "time": "--:--",
                    }
                ]
            )
            app.set_focus(panel)
            await pilot.press("ctrl+enter")
            await pilot.pause()
        assert received == [99]

    @pytest.mark.asyncio
    async def test_rf001_ctrl_k_without_selection_no_message(self):
        """Ctrl+Enter sem item selecionado não posta mensagem."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_tasks_panel_task_complete_request(
                self, message: TasksPanel.TaskCompleteRequest
            ) -> None:
                received.append(message.task_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TasksPanel)
            panel.update_data([])
            app.set_focus(panel)
            await pilot.press("ctrl+enter")
            await pilot.pause()
        assert received == []

    @pytest.mark.asyncio
    async def test_rf001_tasks_panel_no_service_import_at_module_level(self):
        """TasksPanel não importa services no nível de módulo."""
        import importlib
        import sys

        mod = sys.modules.get("timeblock.tui.widgets.tasks_panel")
        if mod is None:
            mod = importlib.import_module("timeblock.tui.widgets.tasks_panel")
        source_file = mod.__file__ or ""
        with open(source_file) as f:
            source = f.read()
        assert "from timeblock.services" not in source
        assert "import TaskService" not in source
