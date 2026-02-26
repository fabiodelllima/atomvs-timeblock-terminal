"""Tests for BR-TUI-002: Screen Navigation (Content Swap).

Refinamento dos testes existentes. Os testes anteriores verificam
a propriedade active_screen e a NavBar. Estes verificam que o
conteúdo do #content-area troca de fato via display toggle.
"""

import pytest

from timeblock.tui.app import TimeBlockApp


@pytest.mark.asyncio
class TestBRTUI002ContentSwap:
    """BR-TUI-002: Navegação troca conteúdo visível no content-area."""

    async def test_br_tui_002_dashboard_visible_on_start(self):
        """Dashboard é o conteúdo visível ao abrir a TUI."""
        async with TimeBlockApp().run_test() as pilot:
            assert pilot.app.query_one("#dashboard-view").display is True

    async def test_br_tui_002_routines_replaces_dashboard(self):
        """Navegar para Routines oculta Dashboard e exibe RoutinesScreen."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("2")

            assert pilot.app.query_one("#dashboard-view").display is False
            assert pilot.app.query_one("#routines-view").display is True

    async def test_br_tui_002_habits_replaces_content(self):
        """Navegar para Habits exibe HabitsScreen."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("3")

            assert pilot.app.query_one("#routines-view").display is False
            assert pilot.app.query_one("#habits-view").display is True

    async def test_br_tui_002_tasks_replaces_content(self):
        """Navegar para Tasks exibe TasksScreen."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("4")

            assert pilot.app.query_one("#tasks-view").display is True

    async def test_br_tui_002_timer_replaces_content(self):
        """Navegar para Timer exibe TimerScreen."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("5")

            assert pilot.app.query_one("#timer-view").display is True

    async def test_br_tui_002_sequential_navigation_swaps(self):
        """Navegação sequencial troca conteúdo corretamente."""
        async with TimeBlockApp().run_test() as pilot:
            # Dashboard -> Routines
            await pilot.press("2")
            assert pilot.app.query_one("#routines-view").display is True
            assert pilot.app.query_one("#dashboard-view").display is False

            # Routines -> Habits
            await pilot.press("3")
            assert pilot.app.query_one("#habits-view").display is True
            assert pilot.app.query_one("#routines-view").display is False

            # Habits -> Dashboard
            await pilot.press("1")
            assert pilot.app.query_one("#dashboard-view").display is True
            assert pilot.app.query_one("#habits-view").display is False

    async def test_br_tui_002_escape_swaps_back_to_dashboard(self):
        """Escape troca conteúdo de volta para Dashboard."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("r")
            assert pilot.app.query_one("#routines-view").display is True

            await pilot.press("escape")
            assert pilot.app.query_one("#dashboard-view").display is True
            assert pilot.app.query_one("#routines-view").display is False

    async def test_br_tui_002_only_one_screen_visible(self):
        """Apenas uma screen visível por vez no content-area."""
        async with TimeBlockApp().run_test() as pilot:
            screen_ids = [
                "#dashboard-view",
                "#routines-view",
                "#habits-view",
                "#tasks-view",
                "#timer-view",
            ]

            for key in ["1", "2", "3", "4", "5"]:
                await pilot.press(key)
                visible = sum(1 for sid in screen_ids if pilot.app.query_one(sid).display is True)
                assert visible == 1, (
                    f"Esperava 1 screen visível após pressionar '{key}', encontrou {visible}"
                )
