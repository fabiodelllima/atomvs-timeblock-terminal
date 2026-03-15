"""CRUD de tarefas via dashboard (BR-TUI-018).

Responsabilidade única: montar modais e executar operações
de tarefas via TaskService. Sem dependência de rotina ativa.

Referências:
    - BR-TUI-018: Dashboard CRUD — Tarefas
    - ADR-034: Dashboard-first CRUD
    - FOWLER, 2018, p. 182 (Extract Delegate — RF-001)
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from datetime import time as dt_time
from typing import TYPE_CHECKING, Any

from timeblock.services.task_service import TaskService
from timeblock.tui.session import service_action
from timeblock.tui.widgets.confirm_dialog import ConfirmDialog
from timeblock.tui.widgets.form_modal import FormField, FormModal
from timeblock.utils.validators import parse_time_to_time

if TYPE_CHECKING:
    from textual.app import App


def _build_datetime(date_iso: str, time_str: str | None) -> datetime:
    """Combina data ISO (YYYY-MM-DD) e horário HH:MM em datetime.

    Se horário vazio ou ausente, usa 00:00.
    """
    year, month, day = (int(p) for p in date_iso.split("-"))
    if time_str:
        t = parse_time_to_time(time_str)
    else:
        t = dt_time(0, 0)
    return datetime(year, month, day, t.hour, t.minute)


def _today_dd_mm() -> str:
    """Retorna data de hoje no formato DD/MM."""
    today = date.today()
    return f"{today.day:02d}/{today.month:02d}"


def open_create_task(
    app: App,
    on_done: Callable[[], None],
) -> None:
    """Abre FormModal para criar tarefa (BR-TUI-018 regra 1).

    Campos: título (obrigatório), data (default hoje), horário (opcional).
    """
    fields = [
        FormField(
            name="title",
            label="Título",
            required=True,
            placeholder="Ex: Revisar relatório",
        ),
        FormField(
            name="date",
            label="Data (DD/MM ou DD/MM/YYYY)",
            field_type="date",
            required=False,
            default=_today_dd_mm(),
            placeholder="DD/MM",
        ),
        FormField(
            name="time",
            label="Horário (opcional)",
            field_type="time",
            required=False,
            placeholder="HH:MM",
        ),
    ]

    def on_submit(data: dict[str, Any]) -> None:
        date_iso = (
            data.get("date")
            or f"{date.today().year}-{date.today().month:02d}-{date.today().day:02d}"
        )
        time_str = data.get("time")
        scheduled = _build_datetime(date_iso, time_str)

        result, error = service_action(
            lambda s: TaskService.create_task(
                title=data["title"],
                scheduled_datetime=scheduled,
                session=s,
            )
        )
        if not error and result:
            on_done()

    app.push_screen(
        FormModal(
            title="Nova Tarefa",
            fields=fields,
            on_submit=on_submit,
        )
    )


def open_edit_task(
    app: App,
    task_data: dict[str, Any],
    on_done: Callable[[], None],
) -> None:
    """Abre FormModal para editar tarefa sob cursor (BR-TUI-018 regra 2)."""
    task_id = task_data["id"]
    fields = [
        FormField(name="title", label="Título", required=True),
        FormField(
            name="date",
            label="Data (DD/MM ou DD/MM/YYYY)",
            field_type="date",
            required=False,
        ),
        FormField(
            name="time",
            label="Horário (opcional)",
            field_type="time",
            required=False,
        ),
    ]
    edit_data = {
        "title": task_data.get("name", ""),
        "date": task_data.get("date", _today_dd_mm()),
        "time": task_data.get("time", ""),
    }

    def on_submit(data: dict[str, Any]) -> None:
        date_iso = (
            data.get("date")
            or f"{date.today().year}-{date.today().month:02d}-{date.today().day:02d}"
        )
        time_str = data.get("time")
        scheduled = _build_datetime(date_iso, time_str)

        service_action(
            lambda s: TaskService.update_task(
                task_id=task_id,
                title=data["title"],
                scheduled_datetime=scheduled,
                session=s,
            )
        )
        on_done()

    app.push_screen(
        FormModal(
            title="Editar Tarefa",
            fields=fields,
            edit_data=edit_data,
            on_submit=on_submit,
        )
    )


def open_delete_task(
    app: App,
    task_data: dict[str, Any],
    on_done: Callable[[], None],
) -> None:
    """Abre ConfirmDialog para deletar tarefa (BR-TUI-018 regra 3)."""
    task_id = task_data["id"]
    task_name = task_data.get("name", "tarefa")

    def on_confirm() -> None:
        service_action(lambda s: TaskService.delete_task(task_id, session=s))
        on_done()

    app.push_screen(
        ConfirmDialog(
            title="Deletar Tarefa",
            message=f"Deletar '{task_name}'?",
            on_confirm=on_confirm,
        )
    )
