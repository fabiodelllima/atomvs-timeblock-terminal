"""Tests for BR-TUI-004: Global Keybindings (ADR-035)."""

import pytest

from timeblock.tui.app import TimeBlockApp
from timeblock.tui.screens.dashboard import loader
from timeblock.tui.widgets.confirm_dialog import ConfirmDialog


class TestBRTUI004GlobalKeybindings:
    """BR-TUI-004: Keybindings globais funcionam em qualquer screen."""

    @pytest.mark.asyncio
    async def test_br_tui_004_ctrl_q_opens_confirm(self):
        """Ctrl+Q abre ConfirmDialog em vez de encerrar imediatamente."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("ctrl+q")
            await pilot.pause()
            assert pilot.app.is_running is True
            assert len(pilot.app.screen_stack) == 2
            assert isinstance(pilot.app.screen, ConfirmDialog)

    @pytest.mark.asyncio
    async def test_br_tui_004_quit_confirm_exits(self):
        """Confirmar (Enter) no modal de saída solicita o encerramento."""
        app = TimeBlockApp()
        async with app.run_test() as pilot:
            exit_called = False

            def fake_exit(*args: object, **kwargs: object) -> None:
                nonlocal exit_called
                exit_called = True

            app.exit = fake_exit  # type: ignore[method-assign]
            await pilot.press("ctrl+q")
            await pilot.pause()
            assert len(pilot.app.screen_stack) == 2
            await pilot.press("enter")
            await pilot.pause()
            assert exit_called is True

    @pytest.mark.asyncio
    async def test_br_tui_004_quit_cancel_stays(self):
        """Cancelar (Esc) no modal de saída mantém a aplicação aberta."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("ctrl+q")
            await pilot.pause()
            assert pilot.app.is_running is True
            await pilot.press("escape")
            await pilot.pause()
            assert pilot.app.is_running is True
            assert len(pilot.app.screen_stack) == 1

    @pytest.mark.asyncio
    async def test_br_tui_004_quit_message_mentions_active_timer(self, monkeypatch):
        """Com timer ativo, a mensagem do modal de saída menciona o timer."""
        monkeypatch.setattr(
            loader,
            "load_active_timer",
            lambda: {"name": "Estudar Biologia", "status": "RUNNING"},
        )
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("ctrl+q")
            await pilot.pause()
            dialog = pilot.app.screen
            assert "Estudar Biologia" in str(dialog._message)
            assert "andamento" in str(dialog._message)

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
            await pilot.press("2")  # Vai para Routines
            assert pilot.app.active_screen == "routines"
            await pilot.press("escape")
            assert pilot.app.active_screen == "dashboard"

    @pytest.mark.asyncio
    async def test_br_tui_004_global_keys_work_from_any_screen(self):
        """Keybindings globais funcionam em qualquer screen."""
        async with TimeBlockApp().run_test() as pilot:
            await pilot.press("4")  # Vai para Tasks
            assert pilot.app.active_screen == "tasks"
            await pilot.press("?")
            help_overlay = pilot.app.query("#help-overlay")
            assert len(help_overlay) == 1
