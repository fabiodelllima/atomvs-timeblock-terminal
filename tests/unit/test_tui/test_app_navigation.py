"""Tests for BR-TUI-002: Screen Navigation."""

import pytest


@pytest.mark.asyncio
class TestBRTUI002ScreenNavigation:
    """BR-TUI-002: Navegação entre screens via keybindings."""

    async def test_br_tui_002_initial_screen_is_dashboard(self):
        """Screen inicial deve ser Dashboard."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            app = pilot.app
            assert app.active_screen == "dashboard"

    async def test_br_tui_002_numeric_keybinding_navigation(self):
        """Keybindings numéricos navegam entre screens."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            app = pilot.app

            await pilot.press("2")
            assert app.active_screen == "routines"

            await pilot.press("1")
            assert app.active_screen == "dashboard"

    async def test_br_tui_002_mnemonic_keybinding_navigation(self):
        """Keybindings mnemônicos navegam entre screens."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            app = pilot.app

            await pilot.press("r")
            assert app.active_screen == "routines"

            await pilot.press("d")
            assert app.active_screen == "dashboard"

            await pilot.press("h")
            assert app.active_screen == "habits"

            await pilot.press("t")
            assert app.active_screen == "tasks"

            await pilot.press("m")
            assert app.active_screen == "timer"

    async def test_br_tui_002_nav_bar_shows_active_screen(self):
        """Nav bar deve indicar screen ativa."""
        from timeblock.tui.app import TimeBlockApp

        async with TimeBlockApp().run_test() as pilot:
            nav_bar = pilot.app.query_one("NavBar")
            assert nav_bar is not None
