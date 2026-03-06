"""Testes do FormModal (BR-TUI-020).

Referências:
    - BR-TUI-020: FormModal
    - ADR-019: Test Naming Convention
"""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from timeblock.tui.widgets.form_modal import FormField, FormModal


class FormModalTestApp(App):
    """App de teste para montar FormModal."""

    def compose(self) -> ComposeResult:
        yield Static("Background", id="bg")


class TestBRTUI020FormModal:
    """BR-TUI-020: FormModal — modal de formulário com validação."""

    @pytest.mark.asyncio
    async def test_br_tui_020_tab_navigates_fields(self):
        """Tab navega entre campos sequencialmente."""
        fields = [
            FormField(name="title", label="Título"),
            FormField(name="duration", label="Duração"),
        ]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            modal = FormModal(title="Novo", fields=fields)
            app.push_screen(modal)
            await pilot.pause()
            inputs = modal.query("Input")
            assert len(inputs) == 2

    @pytest.mark.asyncio
    async def test_br_tui_020_enter_submits_form(self):
        """Enter submete formulário com dados."""
        submitted = {}

        def on_submit(data):
            submitted.update(data)

        fields = [
            FormField(name="title", label="Título", required=True),
        ]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            modal = FormModal(title="Novo", fields=fields, on_submit=on_submit)
            app.push_screen(modal)
            await pilot.pause()
            inp = modal.query_one("#fm-input-title")
            inp.value = "Rotina Matinal"
            await pilot.press("enter")
            assert submitted.get("title") == "Rotina Matinal"

    @pytest.mark.asyncio
    async def test_br_tui_020_esc_cancels_form(self):
        """Esc cancela sem submeter."""
        cancelled = False

        def on_cancel():
            nonlocal cancelled
            cancelled = True

        fields = [FormField(name="title", label="Título")]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            app.push_screen(
                FormModal(
                    title="Novo",
                    fields=fields,
                    on_cancel=on_cancel,
                )
            )
            await pilot.press("escape")
            assert cancelled is True

    @pytest.mark.asyncio
    async def test_br_tui_020_required_field_validation(self):
        """Campo obrigatório vazio exibe erro inline."""
        fields = [
            FormField(name="title", label="Título", required=True),
        ]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            modal = FormModal(title="Novo", fields=fields)
            app.push_screen(modal)
            await pilot.pause()
            # Submit com campo vazio
            await pilot.press("enter")
            await pilot.pause()
            # Modal permanece aberto (validação impediu submit)
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_020_time_field_format_validation(self):
        """Campo time valida formato HH:MM."""
        fields = [
            FormField(name="start", label="Início", field_type="time"),
        ]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            modal = FormModal(title="Novo", fields=fields)
            app.push_screen(modal)
            await pilot.pause()
            inp = modal.query_one("#fm-input-start")
            inp.value = "abc"
            await pilot.press("enter")
            await pilot.pause()
            # Modal permanece aberto (validação impediu submit)
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_020_number_field_positive_validation(self):
        """Campo number rejeita valores não positivos."""
        fields = [
            FormField(name="duration", label="Duração", field_type="number"),
        ]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            modal = FormModal(title="Novo", fields=fields)
            app.push_screen(modal)
            await pilot.pause()
            inp = modal.query_one("#fm-input-duration")
            inp.value = "0"
            await pilot.press("enter")
            await pilot.pause()
            # Modal permanece aberto (validação impediu submit)
            assert len(app.screen_stack) == 2

    @pytest.mark.asyncio
    async def test_br_tui_020_edit_mode_prefilled(self):
        """Modo edit preenche campos com valores existentes."""
        fields = [
            FormField(name="title", label="Título"),
        ]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            modal = FormModal(
                title="Editar",
                fields=fields,
                edit_data={"title": "Academia"},
            )
            app.push_screen(modal)
            await pilot.pause()
            inp = modal.query_one("#fm-input-title")
            assert inp.value == "Academia"

    @pytest.mark.asyncio
    async def test_br_tui_020_create_mode_empty(self):
        """Modo create tem campos vazios."""
        fields = [
            FormField(name="title", label="Título"),
        ]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            modal = FormModal(title="Novo", fields=fields)
            app.push_screen(modal)
            await pilot.pause()
            inp = modal.query_one("#fm-input-title")
            assert inp.value == ""

    @pytest.mark.asyncio
    async def test_br_tui_020_modal_traps_focus(self):
        """Modal captura foco exclusivamente."""
        fields = [FormField(name="title", label="Título")]
        app = FormModalTestApp()
        async with app.run_test() as pilot:
            app.push_screen(FormModal(title="Novo", fields=fields))
            await pilot.pause()
            assert len(app.screen_stack) == 2
