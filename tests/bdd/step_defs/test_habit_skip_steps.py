"""Step definitions para BR-HABIT-SKIP-001 (Skip de Habit com Categorização).

Conecta cenários Gherkin do arquivo habit_skip.feature com código Python.
"""

from datetime import date, time

from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models.enums import SkipReason, Status
from timeblock.models.habit import Habit, Recurrence
from timeblock.models.habit_instance import HabitInstance
from timeblock.models.routine import Routine
from timeblock.services.habit_instance_service import HabitInstanceService

# Carregar todos os cenários do arquivo
scenarios("../features/habit_skip.feature")


# ==================== CONTEXTO ====================


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
    'a habit "Academia" is scheduled for today at 07:00-08:30',
    target_fixture="test_habit",
)
def criar_habit(session: Session, test_routine: Routine):
    """Cria habit para testes."""
    assert test_routine.id is not None

    habit = Habit(
        routine_id=test_routine.id,
        title="Academia",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    assert habit.id is not None
    return habit


@given('a HabitInstance with status "PENDING" exists', target_fixture="test_instance")
def criar_habit_instance(session: Session, test_habit: Habit):
    """Cria HabitInstance PENDING para testes."""
    assert test_habit.id is not None

    instance = HabitInstance(
        habit_id=test_habit.id,
        date=date.today(),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    assert instance.id is not None
    return instance


# ==================== WHEN (AÇÕES) ====================


@when(parsers.parse('the user marks skip with category "{category}" and note "{note}"'))
def skip_com_nota(session: Session, test_instance: HabitInstance, category: str, note: str):
    """Executa skip com categoria e nota."""
    skip_reason = SkipReason[category]
    service = HabitInstanceService()

    result = service.skip_habit_instance(
        habit_instance_id=test_instance.id,
        skip_reason=skip_reason,
        skip_note=note,
        session=session,
    )

    session.info = {"result": result}


@when(parsers.parse('the user marks skip with category "{category}" without note'))
def skip_sem_nota(session: Session, test_instance: HabitInstance, category: str):
    """Executa skip com categoria sem nota."""
    skip_reason = SkipReason[category]
    service = HabitInstanceService()

    result = service.skip_habit_instance(
        habit_instance_id=test_instance.id,
        skip_reason=skip_reason,
        skip_note=None,
        session=session,
    )

    session.info = {"result": result}


@when("the user tries to skip HabitInstance with ID 99999")
def skip_id_inexistente(session: Session):
    """Tenta skip de ID inexistente."""
    service = HabitInstanceService()

    try:
        service.skip_habit_instance(
            habit_instance_id=99999,
            skip_reason=SkipReason.HEALTH,
            skip_note=None,
            session=session,
        )
        session.info = {"error": None}
    except ValueError as e:
        session.info = {"error": str(e)}


@given("the skip_note has 501 characters", target_fixture="nota_longa")
def nota_longa():
    """Cria nota com 501 caracteres."""
    return "A" * 501


@when(parsers.parse('the user tries skip with category "{category}" and that note'))
def skip_nota_longa(session: Session, test_instance: HabitInstance, category: str, nota_longa: str):
    """Tenta skip com nota muito longa."""
    skip_reason = SkipReason[category]
    service = HabitInstanceService()

    try:
        service.skip_habit_instance(
            habit_instance_id=test_instance.id,
            skip_reason=skip_reason,
            skip_note=nota_longa,
            session=session,
        )
        session.info = {"error": None}
    except ValueError as e:
        session.info = {"error": str(e)}


# ==================== THEN (ASSERÇÕES) ====================


@then(parsers.parse('the status should be "{expected_status}"'))
def verificar_status(session: Session, test_instance: HabitInstance, expected_status: str):
    """Verifica status da instância."""
    session.refresh(test_instance)
    assert test_instance.status.value == expected_status.lower()


@then(parsers.parse('the substatus should be "{expected_substatus}"'))
def verificar_substatus(session: Session, test_instance: HabitInstance, expected_substatus: str):
    """Verifica substatus da instância."""
    session.refresh(test_instance)
    assert test_instance.not_done_substatus is not None
    assert test_instance.not_done_substatus.value == expected_substatus.lower()


@then(parsers.parse('the skip_reason should be "{expected_reason}"'))
def verificar_skip_reason(session: Session, test_instance: HabitInstance, expected_reason: str):
    """Verifica skip_reason."""
    session.refresh(test_instance)
    assert test_instance.skip_reason is not None
    assert test_instance.skip_reason.value == expected_reason


@then(parsers.parse('the skip_note should be "{expected_note}"'))
def verificar_skip_note(session: Session, test_instance: HabitInstance, expected_note: str):
    """Verifica skip_note."""
    session.refresh(test_instance)
    assert test_instance.skip_note == expected_note


@then("the skip_note should be NULL")
def verificar_skip_note_null(session: Session, test_instance: HabitInstance):
    """Verifica que skip_note é None."""
    session.refresh(test_instance)
    assert test_instance.skip_note is None


@then("done_substatus should be NULL")
def verificar_done_substatus_null(session: Session, test_instance: HabitInstance):
    """Verifica que done_substatus é None."""
    session.refresh(test_instance)
    assert test_instance.done_substatus is None


@then("completion_percentage should be NULL")
def verificar_completion_null(session: Session, test_instance: HabitInstance):
    """Verifica que completion_percentage é None."""
    session.refresh(test_instance)
    assert test_instance.completion_percentage is None


@then(parsers.parse('the system should return error "{expected_error}"'))
def verificar_erro(session: Session, expected_error: str):
    """Verifica mensagem de erro."""
    error = session.info.get("error")  # type: ignore
    assert error is not None, "Esperava erro mas não foi lançado"
    assert expected_error in error, f"Erro esperado: '{expected_error}', recebido: '{error}'"
