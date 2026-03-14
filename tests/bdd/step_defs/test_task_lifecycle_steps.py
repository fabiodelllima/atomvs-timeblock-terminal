"""Step definitions para BR-TASK-007 a BR-TASK-010: Task Lifecycle."""

from datetime import datetime, timedelta

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models import Task
from timeblock.services.task_service import TaskService

scenarios("../features/task_lifecycle.feature")


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def context() -> dict:
    """Contexto compartilhado entre steps."""
    return {}


# =============================================================================
# Background & Given
# =============================================================================


@given(parsers.parse('a task "{name}" scheduled for tomorrow at {hour:d}:{minute:d} exists'))
def create_task_tomorrow(session: Session, context: dict, name: str, hour: int, minute: int):
    """Cria task agendada para amanhã."""
    tomorrow = datetime.now().replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ) + timedelta(days=1)
    task = TaskService.create_task(
        title=name,
        scheduled_datetime=tomorrow,
        session=session,
    )
    context.setdefault("tasks", {})[name] = task
    context["current_task"] = task


@given(parsers.parse('a task "{name}" scheduled for yesterday at {hour:d}:{minute:d} exists'))
def create_task_yesterday(session: Session, context: dict, name: str, hour: int, minute: int):
    """Cria task agendada para ontem (overdue)."""
    yesterday = datetime.now().replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ) - timedelta(days=1)
    task = TaskService.create_task(
        title=name,
        scheduled_datetime=yesterday,
        session=session,
    )
    context.setdefault("tasks", {})[name] = task
    context["current_task"] = task


# =============================================================================
# When
# =============================================================================


@when("I complete the task")
def complete_current_task(session: Session, context: dict):
    """Conclui a task corrente."""
    task = context["current_task"]
    TaskService.complete_task(task.id, session=session)
    session.refresh(task)


@when(parsers.parse('I complete the task "{name}"'))
def complete_named_task(session: Session, context: dict, name: str):
    """Conclui task por nome."""
    task = context["tasks"][name]
    TaskService.complete_task(task.id, session=session)
    session.refresh(task)
    context["current_task"] = task


@when("I cancel the task")
def cancel_current_task(session: Session, context: dict):
    """Cancela a task corrente (soft delete)."""
    task = context["current_task"]
    TaskService.cancel_task(task.id, session=session)
    session.refresh(task)


@when("I reopen the task")
def reopen_current_task(session: Session, context: dict):
    """Reabre task cancelada."""
    task = context["current_task"]
    TaskService.reopen_task(task.id, session=session)
    session.refresh(task)


@when(parsers.parse("I reschedule the task to {days:d} days later"))
def reschedule_later(session: Session, context: dict, days: int):
    """Reagenda task para N dias depois."""
    task = context["current_task"]
    new_dt = task.scheduled_datetime + timedelta(days=days)
    TaskService.update_task(task.id, scheduled_datetime=new_dt, session=session)
    session.refresh(task)


@when(parsers.parse("I reschedule the task to {days:d} day earlier"))
def reschedule_earlier(session: Session, context: dict, days: int):
    """Reagenda task para N dias antes."""
    task = context["current_task"]
    new_dt = task.scheduled_datetime - timedelta(days=days)
    TaskService.update_task(task.id, scheduled_datetime=new_dt, session=session)
    session.refresh(task)


# =============================================================================
# Then
# =============================================================================


@then(parsers.parse('the task status should be "{expected_status}"'))
def check_current_task_status(context: dict, expected_status: str):
    """Verifica status derivado da task corrente."""
    task = context["current_task"]
    assert task.derived_status == expected_status


@then(parsers.parse('the task "{name}" status should be "{expected_status}"'))
def check_named_task_status(context: dict, name: str, expected_status: str):
    """Verifica status derivado de task nomeada."""
    task = context["tasks"][name]
    assert task.derived_status == expected_status


@then("the task should have completed_datetime set")
def check_completed_datetime_set(context: dict):
    """Verifica que completed_datetime foi preenchido."""
    task = context["current_task"]
    assert task.completed_datetime is not None


@then("the task should have cancelled_datetime set")
def check_cancelled_datetime_set(context: dict):
    """Verifica que cancelled_datetime foi preenchido."""
    task = context["current_task"]
    assert task.cancelled_datetime is not None


@then("the task should not have cancelled_datetime set")
def check_cancelled_datetime_not_set(context: dict):
    """Verifica que cancelled_datetime é None."""
    task = context["current_task"]
    assert task.cancelled_datetime is None


@then("the task should still exist in the database")
def check_task_exists(session: Session, context: dict):
    """Verifica que task não foi removida do banco (soft delete)."""
    task = context["current_task"]
    db_task = session.get(Task, task.id)
    assert db_task is not None


@then("the task original_scheduled_datetime should equal scheduled_datetime")
def check_original_equals_scheduled(context: dict):
    """Verifica imutabilidade do original na criação."""
    task = context["current_task"]
    assert task.original_scheduled_datetime == task.scheduled_datetime


@then("the task original_scheduled_datetime should not change")
def check_original_unchanged(context: dict):
    """Verifica que original não muda após reschedule."""
    task = context["current_task"]
    # original foi capturado na criação e não deve mudar
    assert task.original_scheduled_datetime != task.scheduled_datetime


@then(parsers.parse("the task postponement_count should be {expected:d}"))
def check_postponement_count(context: dict, expected: int):
    """Verifica contador de adiamentos."""
    task = context["current_task"]
    assert task.postponement_count == expected


@then(parsers.parse('the pending tasks list should not contain "{name}"'))
def check_not_in_pending(session: Session, name: str):
    """Verifica que task não aparece na lista de pendentes."""
    pending = TaskService.list_pending_tasks(session=session)
    titles = [t.title for t in pending]
    assert name not in titles


@then(parsers.parse('the all tasks list should contain "{name}"'))
def check_in_all_tasks(session: Session, name: str):
    """Verifica que task aparece na lista completa."""
    all_tasks = TaskService.list_tasks(session=session)
    titles = [t.title for t in all_tasks]
    assert name in titles


@then("the task should be marked as completed_on_time")
def check_completed_on_time(context: dict):
    """Verifica pontualidade da conclusão."""
    task = context["current_task"]
    assert task.completed_datetime.date() <= task.original_scheduled_datetime.date()


@then(parsers.parse('the task "{name}" should have days_late greater than 0'))
def check_days_late(context: dict, name: str):
    """Verifica atraso na conclusão."""
    task = context["tasks"][name]
    days_late = (task.completed_datetime.date() - task.original_scheduled_datetime.date()).days
    assert days_late > 0


@then(parsers.parse("the task days_postponed should be {expected:d}"))
def check_days_postponed(context: dict, expected: int):
    """Verifica total de dias adiados."""
    task = context["current_task"]
    days = (task.scheduled_datetime - task.original_scheduled_datetime).days
    assert days == expected


@then(parsers.parse("the task was_postponed should be {expected}"))
def check_was_postponed(context: dict, expected: str):
    """Verifica flag de adiamento."""
    task = context["current_task"]
    assert (task.postponement_count > 0) == (expected.lower() == "true")
