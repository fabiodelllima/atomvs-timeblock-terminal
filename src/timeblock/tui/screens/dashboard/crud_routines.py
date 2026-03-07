"""CRUD de rotinas via dashboard (BR-TUI-016, RF-001).

Responsabilidade única: montar modais e executar operações
de rotinas via services. Nenhuma lógica de layout ou rendering.

Referências:
    - BR-TUI-016: Dashboard CRUD — Rotinas
    - RF-001: Extract Delegate (FOWLER, 2018, p. 182)
    - ADR-034: Dashboard-first CRUD
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from timeblock.services.routine_service import RoutineService
from timeblock.tui.session import service_action
from timeblock.tui.widgets.confirm_dialog import ConfirmDialog
from timeblock.tui.widgets.form_modal import FormField, FormModal

if TYPE_CHECKING:
    from textual.app import App


def open_create_routine(app: App, on_done: Callable[[], None]) -> None:
    """Abre FormModal para criar rotina (BR-TUI-016 regra 1)."""
    fields = [
        FormField(name="name", label="Nome da rotina", required=True),
    ]

    def on_submit(data: dict) -> None:
        result, error = service_action(
            lambda s: RoutineService(s).create_routine(data["name"], auto_activate=True)
        )
        if not error and result:
            on_done()

    app.push_screen(
        FormModal(
            title="Nova Rotina",
            fields=fields,
            on_submit=on_submit,
        )
    )


def open_edit_routine(
    app: App,
    routine_id: int,
    routine_name: str,
    on_done: Callable[[], None],
) -> None:
    """Abre FormModal para editar rotina ativa (BR-TUI-016 regra 2)."""
    fields = [
        FormField(name="name", label="Nome da rotina", required=True),
    ]

    def on_submit(data: dict) -> None:
        service_action(lambda s: RoutineService(s).update_routine(routine_id, name=data["name"]))
        on_done()

    app.push_screen(
        FormModal(
            title="Editar Rotina",
            fields=fields,
            edit_data={"name": routine_name},
            on_submit=on_submit,
        )
    )


def open_delete_routine(
    app: App,
    routine_id: int,
    routine_name: str,
    on_done: Callable[[], None],
) -> None:
    """Abre ConfirmDialog para deletar rotina (BR-TUI-016 regra 3)."""

    def on_confirm() -> None:
        service_action(lambda s: RoutineService(s).delete_routine(routine_id))
        on_done()

    app.push_screen(
        ConfirmDialog(
            title="Deletar Rotina",
            message=f"Deletar '{routine_name}'?",
            on_confirm=on_confirm,
        )
    )
