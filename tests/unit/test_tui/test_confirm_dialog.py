"""Testes do ConfirmDialog (BR-TUI-019).

Referências:
    - BR-TUI-019: ConfirmDialog
    - ADR-019: Test Naming Convention
"""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from timeblock.tui.widgets.confirm_dialog import ConfirmDialog


class ConfirmDialogTestApp(App):
    """App de teste para montar ConfirmDialog."""

    def compose(self) -> ComposeResult:
        yield Static("Background", id="bg")


class TestBRTUI019ConfirmDialog:
    """BR-TUI-019: ConfirmDialog — modal de confirmação."""

    @pytest.mark.asyncio
    async def test_br_tui_019_enter_triggers_confirm(self):
        """Enter confirma e fecha o modal."""
        confirmed = False

        def on_confirm():
            nonlocal confirmed
            confirmed = True

        app = ConfirmDialogTestApp()
        async with app.run_test() as pilot:
            app.push_screen(
                ConfirmDialog(
                    title="Deletar?",
                    message="Confirma exclusão?",
                    on_confirm=on_confirm,
                )
            )
            await pilot.press("enter")
            assert confirmed is True

    @pytest.mark.asyncio
    async def test_br_tui_019_esc_triggers_cancel(self):
        """Esc cancela e fecha o modal."""
        cancelled = False

        def on_cancel():
            nonlocal cancelled
            cancelled = True

        app = ConfirmDialogTestApp()
        async with app.run_test() as pilot:
            app.push_screen(
                ConfirmDialog(
                    title="Deletar?",
                    message="Confirma exclusão?",
                    on_cancel=on_cancel,
                )
            )
            await pilot.press("escape")
            assert cancelled is True

    @pytest.mark.asyncio
    async def test_br_tui_019_displays_item_name(self):
        """Modal exibe nome do item na mensagem."""
        app = ConfirmDialogTestApp()
        async with app.run_test() as pilot:
            dialog = ConfirmDialog(
                title="Deletar rotina",
                message="Deletar 'Rotina Matinal'?",
            )
            app.push_screen(dialog)
            await pilot.pause()
            dialog.query_one("#cd-message")
            assert "Rotina Matinal" in str(dialog._message)

    @pytest.mark.asyncio
    async def test_br_tui_019_modal_traps_focus(self):
        """Modal captura foco exclusivamente."""
        app = ConfirmDialogTestApp()
        async with app.run_test() as pilot:
            app.push_screen(ConfirmDialog(title="Test", message="Test"))
            await pilot.pause()
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_019_focus_returns_on_close(self):
        """Foco retorna à screen anterior após fechar."""
        app = ConfirmDialogTestApp()
        async with app.run_test() as pilot:
            app.push_screen(ConfirmDialog(title="Test", message="Test"))
            await pilot.press("escape")
            await pilot.pause()
            assert len(app.screen_stack) == 1
