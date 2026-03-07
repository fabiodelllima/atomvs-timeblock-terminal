"""CRUD de hábitos via dashboard (BR-TUI-017, RF-001).

Responsabilidade única: montar modais e executar operações
de hábitos via services. Requer rotina ativa.

Referências:
    - BR-TUI-017: Dashboard CRUD — Hábitos
    - RF-001: Extract Delegate (FOWLER, 2018, p. 182)
    - ADR-034: Dashboard-first CRUD
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import time
from typing import TYPE_CHECKING, Any

from timeblock.models import Recurrence
from timeblock.services.habit_service import HabitService
from timeblock.tui.session import service_action
from timeblock.tui.widgets.confirm_dialog import ConfirmDialog
from timeblock.tui.widgets.form_modal import FormField, FormModal

if TYPE_CHECKING:
    from textual.app import App

RECURRENCE_OPTIONS = [
    ("EVERYDAY", "Todos os dias"),
    ("WEEKDAYS", "Dias úteis"),
    ("WEEKENDS", "Fins de semana"),
    ("MONDAY", "Segunda"),
    ("TUESDAY", "Terça"),
    ("WEDNESDAY", "Quarta"),
    ("THURSDAY", "Quinta"),
    ("FRIDAY", "Sexta"),
    ("SATURDAY", "Sábado"),
    ("SUNDAY", "Domingo"),
]


def _parse_time(value: str) -> time:
    """Converte string HH:MM para time."""
    parts = value.split(":")
    return time(int(parts[0]), int(parts[1]))


def _calculate_end_time(start: time, duration_minutes: int) -> time:
    """Calcula horário de fim a partir de início + duração."""
    total_minutes = start.hour * 60 + start.minute + duration_minutes
    end_hour = min(total_minutes // 60, 23)
    end_minute = total_minutes % 60
    return time(end_hour, end_minute)


def open_create_habit(
    app: App,
    routine_id: int,
    on_done: Callable[[], None],
) -> None:
    """Abre FormModal para criar hábito (BR-TUI-017 regra 1)."""
    fields = [
        FormField(name="title", label="Título", required=True, placeholder="Ex: Academia"),
        FormField(
            name="start",
            label="Horário início",
            field_type="time",
            required=True,
            placeholder="HH:MM",
        ),
        FormField(
            name="duration",
            label="Duração (min)",
            field_type="number",
            required=True,
            placeholder="Ex: 60",
        ),
        FormField(
            name="recurrence",
            label="Recorrência",
            default="EVERYDAY",
            placeholder="EVERYDAY",
        ),
    ]

    def on_submit(data: dict[str, Any]) -> None:
        start = _parse_time(data["start"])
        duration = data["duration"]
        end = _calculate_end_time(start, duration)
        recurrence_value = data.get("recurrence", "EVERYDAY")
        recurrence = Recurrence(recurrence_value)

        result, error = service_action(
            lambda s: HabitService(s).create_habit(
                routine_id=routine_id,
                title=data["title"],
                scheduled_start=start,
                scheduled_end=end,
                recurrence=recurrence,
            )
        )
        if not error and result:
            on_done()

    app.push_screen(
        FormModal(
            title="Novo Hábito",
            fields=fields,
            on_submit=on_submit,
        )
    )


def open_edit_habit(
    app: App,
    habit_data: dict[str, Any],
    on_done: Callable[[], None],
) -> None:
    """Abre FormModal para editar hábito sob cursor (BR-TUI-017 regra 2)."""
    habit_id = habit_data["id"]
    fields = [
        FormField(
            name="title",
            label="Título",
            required=True,
        ),
        FormField(
            name="start",
            label="Horário início",
            field_type="time",
            required=True,
        ),
        FormField(
            name="duration",
            label="Duração (min)",
            field_type="number",
            required=True,
        ),
    ]
    start_h = habit_data.get("start_hour", 0)
    end_h = habit_data.get("end_hour", 0)
    duration = (end_h - start_h) * 60

    edit_data = {
        "title": habit_data.get("name", ""),
        "start": f"{start_h:02d}:00",
        "duration": str(max(duration, 0)),
    }

    def on_submit(data: dict[str, Any]) -> None:
        start = _parse_time(data["start"])
        dur = data["duration"]
        end = _calculate_end_time(start, dur)

        service_action(
            lambda s: HabitService(s).update_habit(
                habit_id=habit_id,
                title=data["title"],
                scheduled_start=start,
                scheduled_end=end,
            )
        )
        on_done()

    app.push_screen(
        FormModal(
            title="Editar Hábito",
            fields=fields,
            edit_data=edit_data,
            on_submit=on_submit,
        )
    )


def open_delete_habit(
    app: App,
    habit_data: dict[str, Any],
    on_done: Callable[[], None],
) -> None:
    """Abre ConfirmDialog para deletar hábito (BR-TUI-017 regra 3)."""
    habit_id = habit_data["id"]
    habit_name = habit_data.get("name", "hábito")

    def on_confirm() -> None:
        service_action(lambda s: HabitService(s).delete_habit(habit_id))
        on_done()

    app.push_screen(
        ConfirmDialog(
            title="Deletar Hábito",
            message=f"Deletar '{habit_name}'?",
            on_confirm=on_confirm,
        )
    )
