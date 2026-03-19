"""Testes de placeholders editáveis nos panels do dashboard (BR-TUI-013).

Valida navegação em placeholders e abertura de FormModal contextual
ao pressionar Enter em panel vazio.

Referências:
    - BR-TUI-013: Placeholders editáveis
    - RF-007: Parameterize Function (FOWLER, 2018, p. 310)
    - ADR-034: Dashboard-first CRUD
"""

import pytest
from textual.app import App, ComposeResult

from timeblock.tui.screens.dashboard.screen import DashboardScreen
from timeblock.tui.widgets.focusable_panel import FocusablePanel
from timeblock.tui.widgets.habits_panel import HabitsPanel
from timeblock.tui.widgets.tasks_panel import TasksPanel


class PlaceholderTestApp(App):
    """App de teste para placeholders."""

    def compose(self) -> ComposeResult:
        yield DashboardScreen(id="dashboard-view")


class TestBRTUI013PlaceholderShown:
    """BR-TUI-013: Placeholders exibidos quando panel está vazio."""

    def test_br_tui_013_focusable_panel_has_placeholder_activated_message(self):
        """FocusablePanel define mensagem PlaceholderActivated."""
        assert hasattr(FocusablePanel, "PlaceholderActivated")

    def test_br_tui_013_focusable_panel_has_enter_placeholder_mode(self):
        """FocusablePanel define método _enter_placeholder_mode (RF-007)."""
        assert hasattr(FocusablePanel, "_enter_placeholder_mode")

    def test_br_tui_013_enter_placeholder_mode_returns_count_plus_hint(self):
        """_enter_placeholder_mode retorna count placeholders + linha vazia + hint."""

        # Instância mínima para testar o método
        panel = HabitsPanel()
        lines = panel._enter_placeholder_mode("---", "Crie algo", count=3)
        # 3 placeholders + 1 vazia + 1 hint = 5
        assert len(lines) == 5
        assert all("---" in line for line in lines[:3])
        assert lines[3] == ""
        assert "Crie algo" in lines[4]

    def test_br_tui_013_habits_panel_empty_sets_placeholders_flag(self):
        """HabitsPanel com lista vazia ativa _showing_placeholders."""
        panel = HabitsPanel()
        panel.update_data([])
        assert panel._showing_placeholders is True
        assert panel._item_count == 3

    def test_br_tui_013_habits_panel_with_items_clears_placeholders_flag(self):
        """HabitsPanel com itens desativa _showing_placeholders."""
        panel = HabitsPanel()
        panel.update_data(
            [
                {
                    "id": 1,
                    "name": "Treino",
                    "status": "pending",
                    "substatus": None,
                    "start_minutes": 420,
                    "end_minutes": 480,
                    "actual_minutes": None,
                }
            ]
        )
        assert panel._showing_placeholders is False

    def test_br_tui_013_tasks_panel_empty_sets_placeholders_flag(self):
        """TasksPanel com lista vazia ativa _showing_placeholders."""
        panel = TasksPanel()
        panel.update_data([])
        assert panel._showing_placeholders is True
        assert panel._item_count == 2

    def test_br_tui_013_is_placeholder_index_true_when_showing(self):
        """_is_placeholder_index retorna True para índice válido em modo placeholder."""
        panel = HabitsPanel()
        panel.update_data([])
        assert panel._is_placeholder_index(0) is True
        assert panel._is_placeholder_index(2) is True

    def test_br_tui_013_is_placeholder_index_false_when_real_items(self):
        """_is_placeholder_index retorna False quando panel tem itens reais."""
        panel = HabitsPanel()
        panel.update_data(
            [
                {
                    "id": 1,
                    "name": "Treino",
                    "status": "pending",
                    "substatus": None,
                    "start_minutes": 420,
                    "end_minutes": 480,
                    "actual_minutes": None,
                }
            ]
        )
        assert panel._is_placeholder_index(0) is False


class StandaloneHabitsApp(App):
    """App isolado — apenas HabitsPanel, sem DashboardScreen."""

    def compose(self) -> ComposeResult:
        yield HabitsPanel(id="panel-habits")


class TestBRTUI013PlaceholderNavigable:
    """BR-TUI-013: Placeholders são navegáveis com cursor."""

    @pytest.mark.asyncio
    async def test_br_tui_013_placeholder_cursor_moves_down(self):
        """Cursor avança nos placeholders com seta para baixo."""
        app = StandaloneHabitsApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel.update_data([])
            app.set_focus(panel)
            await pilot.pause()
            assert panel.cursor_index == 0
            await pilot.press("down")
            await pilot.pause()
            assert panel.cursor_index == 1

    @pytest.mark.asyncio
    async def test_br_tui_013_placeholder_cursor_bounded(self):
        """Cursor não ultrapassa o último placeholder."""
        app = StandaloneHabitsApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(HabitsPanel)
            panel.update_data([])
            app.set_focus(panel)
            await pilot.pause()
            # count=3, índice máximo = 2
            await pilot.press("down")
            await pilot.press("down")
            await pilot.press("down")
            await pilot.pause()
            assert panel.cursor_index == 2


class TestBRTUI013PlaceholderOpensForm:
    """BR-TUI-013: Enter em placeholder abre FormModal contextual."""

    @pytest.mark.asyncio
    async def test_br_tui_013_enter_on_tasks_placeholder_opens_form(self):
        """Enter em placeholder do panel tasks abre FormModal."""
        app = PlaceholderTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TasksPanel)
            panel.update_data([])
            app.set_focus(panel)
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_013_enter_on_habits_placeholder_no_form_without_routine(self):
        """Enter em placeholder de hábitos sem rotina ativa não abre form."""
        app = PlaceholderTestApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            dashboard = app.query_one(DashboardScreen)
            dashboard._active_routine_id = None
            panel = app.query_one(HabitsPanel)
            panel.update_data([])
            app.set_focus(panel)
            await pilot.press("enter")
            await pilot.pause()
            assert len(app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_013_enter_on_real_item_no_placeholder_message(self):
        """Enter em item real não posta PlaceholderActivated."""
        received: list = []

        class CaptureApp(App):
            def compose(self) -> ComposeResult:
                yield DashboardScreen(id="dashboard-view")

            def on_focusable_panel_placeholder_activated(
                self, message: FocusablePanel.PlaceholderActivated
            ) -> None:
                received.append(message.panel_id)

        app = CaptureApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            panel = app.query_one(TasksPanel)
            panel.update_data(
                [
                    {
                        "id": 1,
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
            await pilot.press("enter")
            await pilot.pause()
        assert received == []
