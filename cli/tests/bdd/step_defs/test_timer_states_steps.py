"""Step definitions para BR-TIMER-002 e BR-TIMER-003: Estados de Timer."""

from datetime import date, time

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session, select

from timeblock.models import Habit, HabitInstance, Routine, TimeLog
from timeblock.models.enums import Status, TimerStatus
from timeblock.models.habit import Recurrence
from timeblock.services.timer_service import TimerService

scenarios("../features/timer_states.feature")


# =============================================================================
# Fixtures (Dados de Teste)
# =============================================================================


@pytest.fixture
def context() -> dict:
    """Contexto compartilhado entre steps."""
    return {}


# =============================================================================
# Steps de Background
# =============================================================================


@given(parsers.parse('an active routine "{name}" exists'))
def create_active_routine(session: Session, context: dict, name: str):
    """Cria rotina ativa no banco."""
    routine = Routine(name=name, is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    context["routine"] = routine


@given(parsers.parse('a habit "{name}" exists in the routine'))
def create_habit_in_routine(session: Session, context: dict, name: str):
    """Cria hábito vinculado à rotina."""
    routine = context["routine"]
    habit = Habit(
        title=name,
        routine_id=routine.id,
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 30),
        recurrence=Recurrence.WEEKDAYS,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    context["habit"] = habit


@given("a pending instance exists for today")
def create_pending_instance(session: Session, context: dict):
    """Cria instância PENDING para data de hoje."""
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


# =============================================================================
# Steps Given - Estados de Timer
# =============================================================================


@given("a RUNNING timer exists")
def create_running_timer(session: Session, context: dict):
    """Cria timer no estado RUNNING."""
    instance = context["instance"]
    timelog = TimerService.start_timer(instance.id, session)
    context["timelog"] = timelog


@given("a PAUSED timer exists")
def create_paused_timer(session: Session, context: dict):
    """Cria timer no estado PAUSED."""
    instance = context["instance"]
    timelog = TimerService.start_timer(instance.id, session)
    TimerService.pause_timer(timelog.id, session)
    session.refresh(timelog)
    context["timelog"] = timelog


@given("a CANCELLED timelog exists")
def create_cancelled_timelog(session: Session, context: dict):
    """Cria timelog CANCELLED."""
    instance = context["instance"]
    timelog = TimerService.start_timer(instance.id, session)
    TimerService.reset_timer(timelog.id, session)
    session.refresh(timelog)
    context["timelog"] = timelog


@given(parsers.parse("a DONE timelog with id {timelog_id:d} exists"))
def create_done_timelog_with_id(session: Session, context: dict, timelog_id: int):
    """Cria timelog DONE com ID específico para referência."""
    instance = context["instance"]
    timelog = TimerService.start_timer(instance.id, session)
    TimerService.stop_timer(timelog.id, session)
    session.refresh(timelog)
    # ID é auto-gerado, armazenamos mapeamento para referência no teste
    context["timelog"] = timelog
    context["timelog_id_map"] = {timelog_id: timelog.id}


@given("the instance has a DONE timelog")
def create_instance_with_done_timelog(session: Session, context: dict):
    """Cria instância com timelog DONE para testar múltiplas sessões."""
    instance = context["instance"]
    timelog = TimerService.start_timer(instance.id, session)
    TimerService.stop_timer(timelog.id, session)
    session.refresh(timelog)
    context["done_timelog"] = timelog


# =============================================================================
# Steps When - Ações do Timer
# =============================================================================


@when("I start the timer for the instance")
def start_timer(session: Session, context: dict):
    """Inicia timer para a instância."""
    instance = context["instance"]
    try:
        timelog = TimerService.start_timer(instance.id, session)
        context["timelog"] = timelog
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when("I pause the timer")
def pause_timer(session: Session, context: dict):
    """Pausa o timer ativo."""
    try:
        timelog = context["timelog"]
        TimerService.pause_timer(timelog.id, session)
        session.refresh(timelog)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when("I try to pause the timer")
def try_pause_timer(session: Session, context: dict):
    """Tenta pausar timer (esperando erro)."""
    try:
        timelog = context["timelog"]
        TimerService.pause_timer(timelog.id, session)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when("I resume the timer")
def resume_timer(session: Session, context: dict):
    """Retoma timer pausado."""
    try:
        timelog = context["timelog"]
        TimerService.resume_timer(timelog.id, session)
        session.refresh(timelog)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when("I try to resume the timer")
def try_resume_timer(session: Session, context: dict):
    """Tenta retomar timer (esperando erro)."""
    try:
        timelog = context["timelog"]
        TimerService.resume_timer(timelog.id, session)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when("I stop the timer")
def stop_timer(session: Session, context: dict):
    """Para o timer ativo."""
    try:
        timelog = context["timelog"]
        TimerService.stop_timer(timelog.id, session)
        session.refresh(timelog)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when("I reset the timer")
def reset_timer(session: Session, context: dict):
    """Reseta o timer ativo."""
    try:
        timelog = context["timelog"]
        TimerService.reset_timer(timelog.id, session)
        session.refresh(timelog)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when(parsers.parse('I reset the timer with reason "{reason}"'))
def reset_timer_with_reason(session: Session, context: dict, reason: str):
    """Reseta timer com motivo de cancelamento."""
    try:
        timelog = context["timelog"]
        TimerService.reset_timer(timelog.id, session, reason=reason)
        session.refresh(timelog)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when(parsers.parse('I reset session {session_id:d} with reason "{reason}"'))
def reset_specific_session(session: Session, context: dict, session_id: int, reason: str):
    """Reseta sessão específica por ID."""
    try:
        # Mapeia ID do teste para ID real
        actual_id = context.get("timelog_id_map", {}).get(session_id, session_id)
        TimerService.reset_timer(actual_id, session, reason=reason)
        timelog = session.get(TimeLog, actual_id)
        context["reset_timelog"] = timelog
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


@when("I try to reset the session")
def try_reset_session(session: Session, context: dict):
    """Tenta resetar sessão (esperando erro)."""
    try:
        timelog = context["timelog"]
        TimerService.reset_timer(timelog.id, session)
        context["error"] = None
    except Exception as e:
        context["error"] = str(e)


# =============================================================================
# Steps Then - Asserções
# =============================================================================


@then(parsers.parse('the timelog should have status "{status}"'))
def check_timelog_status(context: dict, status: str):
    """Verifica status do timelog."""
    timelog = context["timelog"]
    expected = TimerStatus[status]
    assert timelog.status == expected, f"Esperado {expected}, obtido {timelog.status}"


@then("the timelog should have start_time set")
def check_start_time_set(context: dict):
    """Verifica que start_time está definido."""
    timelog = context["timelog"]
    assert timelog.start_time is not None


@then("the timelog should have pause_start set")
def check_pause_start_set(context: dict):
    """Verifica que pause_start está definido."""
    timelog = context["timelog"]
    assert timelog.pause_start is not None


@then("the timelog should have end_time set")
def check_end_time_set(context: dict):
    """Verifica que end_time está definido."""
    timelog = context["timelog"]
    assert timelog.end_time is not None


@then("the paused time should be accumulated")
def check_paused_time_accumulated(context: dict):
    """Verifica que tempo pausado foi acumulado."""
    timelog = context["timelog"]
    assert timelog.paused_duration is not None
    assert timelog.paused_duration >= 0


@then("the paused time should be preserved")
def check_paused_time_preserved(context: dict):
    """Verifica que tempo pausado foi preservado após stop."""
    timelog = context["timelog"]
    assert timelog.paused_duration is not None


@then(parsers.parse('the instance should have status "{status}"'))
def check_instance_status(session: Session, context: dict, status: str):
    """Verifica status da instância."""
    instance = context["instance"]
    session.refresh(instance)
    expected = Status[status]
    assert instance.status == expected, f"Esperado {expected}, obtido {instance.status}"


@then(parsers.parse('the instance should remain "{status}"'))
def check_instance_remains(session: Session, context: dict, status: str):
    """Verifica que instância permanece no status esperado."""
    instance = context["instance"]
    session.refresh(instance)
    expected = Status[status]
    assert instance.status == expected


@then(parsers.parse('it should return error "{error_msg}"'))
def check_error_message(context: dict, error_msg: str):
    """Verifica mensagem de erro."""
    assert context.get("error") is not None, "Esperava erro mas nenhum ocorreu"
    assert error_msg.lower() in context["error"].lower()


@then(parsers.parse('the timelog should have cancel_reason "{reason}"'))
def check_cancel_reason(context: dict, reason: str):
    """Verifica cancel_reason do timelog."""
    timelog = context["timelog"]
    assert timelog.cancel_reason == reason


@then(parsers.parse('timelog {timelog_id:d} should have status "{status}"'))
def check_specific_timelog_status(context: dict, timelog_id: int, status: str):
    """Verifica status de timelog específico."""
    timelog = context.get("reset_timelog") or context["timelog"]
    expected = TimerStatus[status]
    assert timelog.status == expected


@then(parsers.parse('timelog {timelog_id:d} should have cancel_reason "{reason}"'))
def check_specific_timelog_reason(context: dict, timelog_id: int, reason: str):
    """Verifica cancel_reason de timelog específico."""
    timelog = context.get("reset_timelog") or context["timelog"]
    assert timelog.cancel_reason == reason


@then(parsers.parse('it should create a new timelog with status "{status}"'))
def check_new_timelog_created(context: dict, status: str):
    """Verifica que novo timelog foi criado."""
    timelog = context["timelog"]
    expected = TimerStatus[status]
    assert timelog.status == expected
    # Verifica que é diferente do done_timelog
    done_timelog = context.get("done_timelog")
    if done_timelog:
        assert timelog.id != done_timelog.id


@then(parsers.parse("the instance should have {count:d} timelogs"))
def check_instance_timelog_count(session: Session, context: dict, count: int):
    """Verifica quantidade de timelogs da instância."""
    instance = context["instance"]
    timelogs = list(session.exec(select(TimeLog).where(TimeLog.habit_instance_id == instance.id)))
    assert len(timelogs) == count, f"Esperado {count} timelogs, obtido {len(timelogs)}"
