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
    from sqlmodel import Session
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
    """Abre ConfirmDialog para desativar rotina (BR-TUI-016, BR-ROUTINE-006)."""

    def on_confirm() -> None:
        _, error = service_action(lambda s: RoutineService(s).delete_routine(routine_id))
        if error:
            app.notify(error, severity="error")
            return
        # DT-048: ativar próxima rotina disponível após desativação
        service_action(lambda s: _activate_next_routine(s, exclude_id=routine_id))
        on_done()

    app.push_screen(
        ConfirmDialog(
            title="Desativar Rotina",
            message=f"Desativar '{routine_name}'?\nHábitos permanecem vinculados.",
            on_confirm=on_confirm,
        )
    )


def _activate_next_routine(s: Session, exclude_id: int | None = None) -> None:
    """Ativa a próxima rotina existente, se houver (DT-048)."""
    from sqlmodel import select

    from timeblock.models.routine import Routine

    stmt = select(Routine)
    if exclude_id is not None:
        stmt = stmt.where(Routine.id != exclude_id)
    remaining = s.exec(stmt).first()
    if remaining and remaining.id:
        RoutineService(s).activate_routine(remaining.id)


def open_select_routine(app: App, on_done: Callable[[], None]) -> None:
    """Abre FormModal com Select listando rotinas para troca (DT-047)."""
    from sqlmodel import select as sql_select

    from timeblock.models.routine import Routine

    routines, error = service_action(lambda s: list(s.exec(sql_select(Routine)).all()))
    if error or not routines or len(routines) < 2:
        app.notify("Apenas uma rotina disponível", severity="information")
        return

    options = [(str(r.id), r.name) for r in routines if r.id is not None]

    fields = [
        FormField(
            name="routine_id",
            label="Selecione a rotina",
            field_type="select",
            options=options,
        ),
    ]

    def on_submit(data: dict) -> None:
        selected_id = int(data["routine_id"])
        service_action(lambda s: RoutineService(s).activate_routine(selected_id))
        on_done()

    app.push_screen(
        FormModal(
            title="Trocar Rotina",
            fields=fields,
            on_submit=on_submit,
        )
    )
