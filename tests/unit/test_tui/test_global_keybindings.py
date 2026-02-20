"""Tests for BR-TUI-004: Global Keybindings."""

import pytest

from timeblock.tui.app import TimeBlockApp


class TestBRTUI004GlobalKeybindings:
    """BR-TUI-004: Keybindings globais funcionam em qualquer screen."""

    @pytest.mark.asyncio
    async def test_br_tui_004_quit_keybinding(self):
        """Pressionar q encerra a aplicação."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("q")
            assert pilot.app.is_running is False

    @pytest.mark.asyncio
    async def test_br_tui_004_help_overlay(self):
        """Pressionar ? exibe overlay de ajuda."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("?")
            help_overlay = pilot.app.query("#help-overlay")
            assert len(help_overlay) == 1

    @pytest.mark.asyncio
    async def test_br_tui_004_escape_closes_help(self):
        """Escape fecha o overlay de ajuda."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("?")
            assert len(pilot.app.query("#help-overlay")) == 1
            await pilot.press("escape")
            assert len(pilot.app.query("#help-overlay")) == 0

    @pytest.mark.asyncio
    async def test_br_tui_004_escape_returns_to_dashboard(self):
        """Escape sem modal aberto volta ao Dashboard."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("r")  # Vai para Routines
            assert pilot.app.active_screen == "routines"
            await pilot.press("escape")
            assert pilot.app.active_screen == "dashboard"

    @pytest.mark.asyncio
    async def test_br_tui_004_global_keys_work_from_any_screen(self):
        """Keybindings globais funcionam em qualquer screen."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("t")  # Vai para Tasks
            assert pilot.app.active_screen == "tasks"
            await pilot.press("?")
            help_overlay = pilot.app.query("#help-overlay")
            assert len(help_overlay) == 1
