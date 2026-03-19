"""Step definitions para BR-HABITINSTANCE-002 (Done com substatus obrigatório).

Conecta cenários Gherkin do arquivo habit_instance_done.feature com código Python.

Referências:
    - BR-HABITINSTANCE-002: Substatus obrigatório para status finais
    - DT-034: mark_completed sem done_substatus (corrigido)
"""

from datetime import date, time

from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models.enums import (
    DoneSubstatus,
    SkipReason,
    Status,
)
from timeblock.models.habit import Habit, Recurrence
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.routine import Routine
from timeblock.services.habit_instance_service import HabitInstanceService

# Carregar todos os cenários do arquivo
scenarios("../features/habit_instance_done.feature")


# ==================== CONTEXTO (Background) ====================
# Steps reutilizados do habit_instance_undo_steps.py:
# - "a routine ... exists"
# - "a habit ... is scheduled for today"
# - "a HabitInstance with status PENDING exists"
# - "the instance is skipped with reason ... and note ..."
# Esses steps já existem e serão resolvidos pelo pytest-bdd.


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
    """Gera instância PENDING para hoje."""
    assert test_habit.id is not None
    instances = HabitInstanceService.generate_instances(
        test_habit.id, date.today(), date.today(), session=session
    )
    assert len(instances) > 0
    instance = instances[0]
    assert instance.status == Status.PENDING
    return instance


@given(
    parsers.parse('the instance is skipped with reason "{reason}" and note "{note}"'),
)
def marcar_skipped(session: Session, test_instance: HabitInstance, reason: str, note: str):
    """Marca instância como skipped via service."""
    assert test_instance.id is not None
    skip_reason = SkipReason[reason.upper()]
    result = HabitInstanceService.skip_habit_instance(
        test_instance.id,
        skip_reason=skip_reason,
        skip_note=note,
        session=session,
    )
    # Atualizar referência
    test_instance.status = result.status
    test_instance.not_done_substatus = result.not_done_substatus
    test_instance.skip_reason = result.skip_reason
    test_instance.skip_note = result.skip_note


# ==================== AÇÕES (When) ====================


@when(
    parsers.parse('the user marks the instance as done with substatus "{substatus}"'),
    target_fixture="done_result",
)
def marcar_done(session: Session, test_instance: HabitInstance, substatus: str):
    """Marca instância como done via mark_completed."""
    assert test_instance.id is not None
    done_sub = DoneSubstatus(substatus.lower())
    result = HabitInstanceService.mark_completed(
        test_instance.id,
        done_substatus=done_sub,
        session=session,
    )
    return result


@when(
    parsers.parse('the user marks instance {instance_id:d} as done with substatus "{substatus}"'),
    target_fixture="done_result",
)
def marcar_done_por_id(session: Session, instance_id: int, substatus: str):
    """Marca instância por ID (pode não existir)."""
    done_sub = DoneSubstatus(substatus.lower())
    result = HabitInstanceService.mark_completed(
        instance_id,
        done_substatus=done_sub,
        session=session,
    )
    return result


# ==================== ASSERÇÕES (Then) ====================


@then(parsers.parse('the status should be "{expected_status}"'))
def verificar_status(done_result: HabitInstance, expected_status: str):
    """Verifica status da instância."""
    assert done_result is not None
    assert done_result.status == Status(expected_status.lower())


@then(parsers.parse('done_substatus should be "{expected}"'))
def verificar_done_substatus(done_result: HabitInstance, expected: str):
    """Verifica done_substatus."""
    assert done_result is not None
    assert done_result.done_substatus == DoneSubstatus(expected.lower())


@then("done_substatus should be NULL")
def verificar_done_substatus_null(done_result: HabitInstance):
    """Verifica done_substatus é None."""
    assert done_result is not None
    assert done_result.done_substatus is None


@then("not_done_substatus should be NULL")
def verificar_not_done_substatus_null(done_result: HabitInstance):
    """Verifica not_done_substatus é None."""
    assert done_result is not None
    assert done_result.not_done_substatus is None


@then("skip_reason should be NULL")
def verificar_skip_reason_null(done_result: HabitInstance):
    """Verifica skip_reason é None."""
    assert done_result is not None
    assert done_result.skip_reason is None


@then("skip_note should be NULL")
def verificar_skip_note_null(done_result: HabitInstance):
    """Verifica skip_note é None."""
    assert done_result is not None
    assert done_result.skip_note is None


@then("completion_percentage should be NULL")
def verificar_completion_null(done_result: HabitInstance):
    """Verifica completion_percentage é None."""
    assert done_result is not None
    assert done_result.completion_percentage is None


@then("the result should be None")
def verificar_result_none(done_result):
    """Verifica que resultado é None (instância não encontrada)."""
    assert done_result is None
