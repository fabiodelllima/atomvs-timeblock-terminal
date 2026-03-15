"""Step definitions para BR-HABITINSTANCE-007 (Undo com preservação de TimeLog).

Conecta cenários Gherkin do arquivo habit_instance_undo.feature com código Python.

Referências:
    - BR-HABITINSTANCE-007: Undo com preservação de TimeLog
    - ADR-038 D1: Undo é transição válida
    - DT-035: Handler undo precisa limpar todos os campos
"""

from datetime import date, datetime, time

from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models.enums import (
    DoneSubstatus,
    SkipReason,
    Status,
    TimerStatus,
)
from timeblock.models.habit import Habit, Recurrence
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.routine import Routine
from timeblock.models.time_log import TimeLog
from timeblock.services.habit_instance_service import HabitInstanceService

# Carregar todos os cenários do arquivo
scenarios("../features/habit_instance_undo.feature")


# ==================== CONTEXTO (Background) ====================


@given('a routine "Rotina Matinal" exists', target_fixture="test_routine")
def criar_rotina(session: Session):
    """Cria rotina para testes."""
    routine = Routine(name="Rotina Matinal")
    session.add(routine)
    session.commit()
    session.refresh(routine)
    assert routine.id is not None
    return routine


@given(
    'a habit "Exercício" is scheduled for today at 08:00-09:00',
    target_fixture="test_habit",
)
def criar_habit(session: Session, test_routine: Routine):
    """Cria habit para testes."""
    assert test_routine.id is not None
    habit = Habit(
        routine_id=test_routine.id,
        title="Exercício",
        scheduled_start=time(8, 0),
        scheduled_end=time(9, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    assert habit.id is not None
    return habit


@given(
    'a HabitInstance with status "PENDING" exists',
    target_fixture="test_instance",
)
def criar_instance(session: Session, test_habit: Habit):
    """Cria HabitInstance PENDING para testes."""
    assert test_habit.id is not None
    instance = HabitInstance(
        habit_id=test_habit.id,
        date=date.today(),
        scheduled_start=time(8, 0),
        scheduled_end=time(9, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    assert instance.id is not None
    return instance


# ==================== GIVEN (precondições de cenário) ====================


@given(
    parsers.parse(
        'the instance is marked DONE with substatus "{substatus}" and completion {pct:d}'
    ),
)
def marcar_done(session: Session, test_instance: HabitInstance, substatus: str, pct: int):
    """Marca instância como DONE com substatus e completion_percentage."""
    test_instance.status = Status.DONE
    test_instance.done_substatus = DoneSubstatus(substatus.lower())
    test_instance.completion_percentage = pct
    session.add(test_instance)
    session.commit()
    session.refresh(test_instance)


@given(
    parsers.parse('the instance is skipped with reason "{reason}" and note "{note}"'),
)
def marcar_skipped(session: Session, test_instance: HabitInstance, reason: str, note: str):
    """Marca instância como SKIPPED via service."""
    skip_reason = SkipReason[reason]
    HabitInstanceService.skip_habit_instance(
        habit_instance_id=test_instance.id,
        skip_reason=skip_reason,
        skip_note=note,
        session=session,
    )
    session.refresh(test_instance)


@given(
    parsers.parse(
        'a TimeLog with status "DONE" and duration {seconds:d} seconds exists for the instance'
    ),
    target_fixture="test_timelog",
)
def criar_timelog(session: Session, test_instance: HabitInstance, seconds: int):
    """Cria TimeLog DONE associado à instância."""
    timelog = TimeLog(
        habit_instance_id=test_instance.id,
        status=TimerStatus.DONE,
        start_time=datetime.combine(date.today(), time(8, 0)),
        end_time=datetime.combine(date.today(), time(8, 55)),
        duration_seconds=seconds,
    )
    session.add(timelog)
    session.commit()
    session.refresh(timelog)
    return timelog


# ==================== WHEN (ações) ====================


@when("the user executes undo")
def executar_undo(session: Session, test_instance: HabitInstance):
    """Executa reset_to_pending() na instância."""
    test_instance.reset_to_pending()
    session.add(test_instance)
    session.commit()
    session.refresh(test_instance)


# ==================== THEN (asserções) ====================


@then(parsers.parse('the status should be "{expected_status}"'))
def verificar_status(session: Session, test_instance: HabitInstance, expected_status: str):
    """Verifica status da instância."""
    session.refresh(test_instance)
    assert test_instance.status.value == expected_status.lower()


@then("done_substatus should be NULL")
def verificar_done_substatus_null(session: Session, test_instance: HabitInstance):
    """Verifica que done_substatus é None."""
    session.refresh(test_instance)
    assert test_instance.done_substatus is None


@then("not_done_substatus should be NULL")
def verificar_not_done_substatus_null(session: Session, test_instance: HabitInstance):
    """Verifica que not_done_substatus é None."""
    session.refresh(test_instance)
    assert test_instance.not_done_substatus is None


@then("skip_reason should be NULL")
def verificar_skip_reason_null(session: Session, test_instance: HabitInstance):
    """Verifica que skip_reason é None."""
    session.refresh(test_instance)
    assert test_instance.skip_reason is None


@then("skip_note should be NULL")
def verificar_skip_note_null(session: Session, test_instance: HabitInstance):
    """Verifica que skip_note é None."""
    session.refresh(test_instance)
    assert test_instance.skip_note is None


@then("completion_percentage should be NULL")
def verificar_completion_null(session: Session, test_instance: HabitInstance):
    """Verifica que completion_percentage é None."""
    session.refresh(test_instance)
    assert test_instance.completion_percentage is None


@then(parsers.parse('the TimeLog should still have status "{expected_status}"'))
def verificar_timelog_status(session: Session, test_timelog: TimeLog, expected_status: str):
    """Verifica que o TimeLog preserva seu status original."""
    session.refresh(test_timelog)
    assert test_timelog.status is not None
    assert test_timelog.status.value == expected_status.lower()


@then(parsers.parse("the TimeLog should still have duration {seconds:d} seconds"))
def verificar_timelog_duration(session: Session, test_timelog: TimeLog, seconds: int):
    """Verifica que o TimeLog preserva sua duration original."""
    session.refresh(test_timelog)
    assert test_timelog.duration_seconds == seconds


@then("the instance habit_id should be unchanged")
def verificar_habit_id(test_instance: HabitInstance, test_habit: Habit):
    """Verifica que habit_id não foi alterado."""
    assert test_instance.habit_id == test_habit.id


@then("the instance date should be unchanged")
def verificar_date(test_instance: HabitInstance):
    """Verifica que date não foi alterado."""
    assert test_instance.date == date.today()


@then("the instance scheduled_start should be unchanged")
def verificar_start(test_instance: HabitInstance):
    """Verifica que scheduled_start não foi alterado."""
    assert test_instance.scheduled_start == time(8, 0)


@then("the instance scheduled_end should be unchanged")
def verificar_end(test_instance: HabitInstance):
    """Verifica que scheduled_end não foi alterado."""
    assert test_instance.scheduled_end == time(9, 0)
