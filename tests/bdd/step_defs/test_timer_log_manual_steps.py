"""Step definitions para BR-TIMER-007: Log Manual de Tempo."""

from datetime import date, time

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine
from timeblock.models.enums import DoneSubstatus, Status
from timeblock.services.timer_service import TimerService

scenarios("../features/timer_log_manual.feature")


@pytest.fixture
def context():
    """Contexto compartilhado entre steps."""
    return {}


# ============================================================
# Background Steps
# ============================================================
@given('an active routine "Morning Routine" exists')
def create_routine(session: Session, context):
    """Cria rotina ativa."""
    routine = Routine(name="Morning Routine", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    context["routine"] = routine


@given('a habit "Meditation" with 60 minutes duration exists')
def create_habit(session: Session, context):
    """Cria hábito com 60 minutos de duração."""
    habit = Habit(
        routine_id=context["routine"].id,
        title="Meditation",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),  # 60 min
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    context["habit"] = habit


@given("a pending instance for today exists")
def create_instance(session: Session, context):
    """Cria instância PENDING para hoje."""
    habit = context["habit"]
    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=habit.scheduled_start,
        scheduled_end=habit.scheduled_end,
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    context["instance"] = instance


# ============================================================
# When Steps - Modo Intervalo
# ============================================================
@when(parsers.parse('I log time with start "{start}" and end "{end}"'))
def log_time_interval(session: Session, context, start: str, end: str):
    """Registra tempo com intervalo start/end."""
    instance = context["instance"]
    start_time = time.fromisoformat(start)
    end_time = time.fromisoformat(end)

    service = TimerService()
    timelog = service.log_manual(
        habit_instance_id=instance.id,
        start_time=start_time,
        end_time=end_time,
        session=session,
    )
    context["timelog"] = timelog


@when(parsers.parse("I log time with duration {minutes:d} minutes"))
def log_time_duration(session: Session, context, minutes: int):
    """Registra tempo com duração em minutos."""
    instance = context["instance"]

    service = TimerService()
    timelog = service.log_manual(
        habit_instance_id=instance.id,
        duration_minutes=minutes,
        session=session,
    )
    context["timelog"] = timelog


# ============================================================
# When Steps - Validação de Erros
# ============================================================
@when(parsers.parse('I try to log time with start "{start}" and end "{end}"'))
def try_log_invalid_interval(session: Session, context, start: str, end: str):
    """Tenta registrar com intervalo inválido."""
    instance = context["instance"]
    start_time = time.fromisoformat(start)
    end_time = time.fromisoformat(end)

    service = TimerService()
    try:
        service.log_manual(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=end_time,
            session=session,
        )
        context["error"] = None
    except ValueError as e:
        context["error"] = str(e)


@when(parsers.parse("I try to log time with duration {minutes:d} minutes"))
def try_log_invalid_duration(session: Session, context, minutes: int):
    """Tenta registrar com duração inválida."""
    instance = context["instance"]

    service = TimerService()
    try:
        service.log_manual(
            habit_instance_id=instance.id,
            duration_minutes=minutes,
            session=session,
        )
        context["error"] = None
    except ValueError as e:
        context["error"] = str(e)


@when(
    parsers.parse('I try to log time with start "{start}" and end "{end}" and duration {minutes:d}')
)
def try_log_mixed_mode(session: Session, context, start: str, end: str, minutes: int):
    """Tenta registrar misturando modos."""
    instance = context["instance"]
    start_time = time.fromisoformat(start)
    end_time = time.fromisoformat(end)

    service = TimerService()
    try:
        service.log_manual(
            habit_instance_id=instance.id,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=minutes,
            session=session,
        )
        context["error"] = None
    except ValueError as e:
        context["error"] = str(e)


@when(parsers.parse('I try to log time with only start "{start}"'))
def try_log_incomplete_interval(session: Session, context, start: str):
    """Tenta registrar com intervalo incompleto."""
    instance = context["instance"]
    start_time = time.fromisoformat(start)

    service = TimerService()
    try:
        service.log_manual(
            habit_instance_id=instance.id,
            start_time=start_time,
            session=session,
        )
        context["error"] = None
    except ValueError as e:
        context["error"] = str(e)


# ============================================================
# Then Steps
# ============================================================
@then(parsers.parse("a TimeLog should be created with duration {seconds:d} seconds"))
def verify_timelog_duration(context, seconds: int):
    """Verifica TimeLog criado com duração correta."""
    timelog = context["timelog"]
    assert timelog is not None
    assert timelog.duration_seconds == seconds


@then("the instance should be marked as DONE")
def verify_instance_done(session: Session, context):
    """Verifica instância marcada como DONE."""
    session.refresh(context["instance"])
    assert context["instance"].status == Status.DONE


@then(parsers.parse("the instance should have completion {percentage:d}%"))
def verify_completion(session: Session, context, percentage: int):
    """Verifica completion percentage."""
    session.refresh(context["instance"])
    assert context["instance"].completion_percentage == percentage


@then(parsers.parse("the instance should have substatus {substatus}"))
def verify_substatus(session: Session, context, substatus: str):
    """Verifica substatus da instância."""
    session.refresh(context["instance"])
    # Converter PARTIAL -> partial para match com enum
    expected = DoneSubstatus(substatus.lower())
    assert context["instance"].done_substatus == expected


@then(parsers.parse('I should receive a validation error "{message}"'))
def verify_error(context, message: str):
    """Verifica mensagem de erro de validação."""
    assert context["error"] is not None
    assert message in context["error"]
