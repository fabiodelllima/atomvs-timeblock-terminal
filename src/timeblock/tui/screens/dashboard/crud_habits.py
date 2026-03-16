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
from datetime import date, time
from typing import TYPE_CHECKING, Any

from sqlmodel import Session, col, select

from timeblock.models import Recurrence
from timeblock.models.enums import DoneSubstatus, TimerStatus
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.time_log import TimeLog
from timeblock.services.event_reordering_service import EventReorderingService
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.services.habit_service import HabitService
from timeblock.tui.session import service_action
from timeblock.tui.widgets.confirm_dialog import ConfirmDialog
from timeblock.tui.widgets.form_modal import FormField, FormModal
from timeblock.utils.validators import parse_time_to_time

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

DONE_SUBSTATUS_OPTIONS = [
    ("FULL", "Completo (90-110%)"),
    ("PARTIAL", "Parcial (<90%)"),
    ("OVERDONE", "Além do esperado (110-150%)"),
    ("EXCESSIVE", "Excessivo (>150%)"),
]


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
            field_type="select",
            default="EVERYDAY",
            options=RECURRENCE_OPTIONS,
        ),
    ]

    def on_submit(data: dict[str, Any]) -> None:
        start = parse_time_to_time(data["start"])
        duration = data["duration"]
        end = _calculate_end_time(start, duration)
        recurrence_value = data.get("recurrence", "EVERYDAY")
        recurrence = Recurrence(recurrence_value)

        def _create(s: Session) -> int | None:
            habit = HabitService(s).create_habit(
                routine_id=routine_id,
                title=data["title"],
                scheduled_start=start,
                scheduled_end=end,
                recurrence=recurrence,
            )
            return habit.id if habit else None

        habit_id, error = service_action(_create)
        if not error and habit_id:
            today = date.today()
            service_action(
                lambda s: HabitInstanceService.generate_instances(
                    habit_id=habit_id, start_date=today, end_date=today, session=s
                )
            )
            # Detectar conflitos (informar, nunca decidir)
            conflicts, _ = service_action(
                lambda s: EventReorderingService.detect_conflicts(
                    habit_id, "habit_instance", session=s
                )
            )

            if conflicts:
                names = ", ".join(
                    f"{c.conflicting_event_type}#{c.conflicting_event_id}" for c in conflicts[:3]
                )
                app.notify(
                    f"Conflito detectado com: {names}",
                    severity="warning",
                    timeout=5,
                )
            on_done()

    app.push_screen(
        FormModal(
            title="Novo Hábito",
            fields=fields,
            on_submit=on_submit,
        )
    )


def _find_done_timelog(session: Session, instance_id: int) -> dict[str, Any] | None:
    """Busca TimeLog DONE e calcula substatus/completion para restauração."""
    instance = session.get(HabitInstance, instance_id)
    if not instance:
        return None

    statement = (
        select(TimeLog)
        .where(
            TimeLog.habit_instance_id == instance_id,
            col(TimeLog.status) == TimerStatus.DONE,
        )
        .order_by(col(TimeLog.id).desc())
    )
    timelog = session.exec(statement).first()
    if not timelog or not timelog.duration_seconds:
        return None

    # Calcular completion_percentage (mesmo algoritmo de stop_timer)
    from datetime import datetime

    target_start = datetime.combine(instance.date, instance.scheduled_start)
    target_end = datetime.combine(instance.date, instance.scheduled_end)
    target_seconds = (target_end - target_start).total_seconds()
    if target_seconds <= 0:
        return None

    completion_percentage = int((timelog.duration_seconds / target_seconds) * 100)

    if completion_percentage < 90:
        done_substatus = DoneSubstatus.PARTIAL
    elif completion_percentage <= 110:
        done_substatus = DoneSubstatus.FULL
    elif completion_percentage <= 150:
        done_substatus = DoneSubstatus.OVERDONE
    else:
        done_substatus = DoneSubstatus.EXCESSIVE

    minutes = timelog.duration_seconds // 60
    return {
        "substatus": done_substatus,
        "completion_percentage": completion_percentage,
        "minutes": minutes,
    }


def _show_substatus_form(
    app: App,
    instance_id: int,
    on_done: Callable[[], None],
) -> None:
    """Abre FormModal com Select de DoneSubstatus (BR-TUI-022)."""
    fields = [
        FormField(
            name="substatus",
            label="Como foi a execução?",
            field_type="select",
            default="FULL",
            options=DONE_SUBSTATUS_OPTIONS,
        ),
    ]

    def on_submit(data: dict[str, Any]) -> None:
        substatus_value = data.get("substatus", "FULL")
        done_sub = DoneSubstatus(substatus_value)
        service_action(
            lambda s: HabitInstanceService.mark_completed(
                instance_id, done_substatus=done_sub, session=s
            )
        )
        on_done()

    app.push_screen(
        FormModal(
            title="Marcar Concluído",
            fields=fields,
            on_submit=on_submit,
        )
    )


def open_done_modal(
    app: App,
    instance_id: int,
    on_done: Callable[[], None],
) -> None:
    """Abre modal de done com detecção de TimeLog (BR-TUI-022, DT-037).

    Fluxo:
        1. Busca TimeLog DONE para a instância
        2. Se encontrado: ConfirmDialog oferece restauração
           - Enter: restaura substatus/completion do timer
           - Esc: abre FormModal para seleção manual
        3. Se não encontrado: abre FormModal diretamente
    """
    timelog_data, _ = service_action(lambda s: _find_done_timelog(s, instance_id))

    if timelog_data:
        substatus = timelog_data["substatus"]
        pct = timelog_data["completion_percentage"]
        minutes = timelog_data["minutes"]

        def on_confirm() -> None:
            service_action(
                lambda s: HabitInstanceService.mark_completed(
                    instance_id,
                    done_substatus=substatus,
                    completion_percentage=pct,
                    session=s,
                )
            )
            on_done()

        def on_cancel() -> None:
            _show_substatus_form(app, instance_id, on_done)

        app.push_screen(
            ConfirmDialog(
                title="Sessão Anterior Encontrada",
                message=f"Timer: {minutes}min ({pct}%). Restaurar como {substatus.value}?",
                on_confirm=on_confirm,
                on_cancel=on_cancel,
            )
        )
    else:
        _show_substatus_form(app, instance_id, on_done)


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
        FormField(
            name="recurrence",
            label="Recorrência",
            field_type="select",
            options=RECURRENCE_OPTIONS,
        ),
    ]
    sm = habit_data.get("start_minutes", 0)
    em = habit_data.get("end_minutes", 0)
    duration = em - sm
    sh, s_min = divmod(sm, 60)

    edit_data = {
        "title": habit_data.get("name", ""),
        "start": f"{sh:02d}:{s_min:02d}",
        "recurrence": habit_data.get("recurrence", "EVERYDAY"),
        "duration": str(max(duration, 0)),
    }

    def on_submit(data: dict[str, Any]) -> None:
        start = parse_time_to_time(data["start"])
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
