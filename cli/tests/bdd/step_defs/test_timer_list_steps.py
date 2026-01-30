"""Step definitions for BR-TIMER-008: TimeLog Listing."""

from datetime import date, datetime, time, timedelta

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine
from timeblock.models.time_log import TimeLog
from timeblock.services.timer_service import TimerService

scenarios("../features/timer_list.feature")


@pytest.fixture
def context():
    """Shared context between steps."""
    return {}


@given('an active routine "Test Routine" exists')
def create_active_routine(session: Session, context):
    """Cria rotina ativa para testes."""
    routine = Routine(name="Test Routine", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    context["routine"] = routine


@given('a habit "Gym" exists in the routine')
def create_habit_gym(session: Session, context):
    """Cria hábito Gym na rotina."""
    habit = Habit(
        routine_id=context["routine"].id,
        title="Gym",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    context["habit"] = habit


@given("instances are generated for 3 days")
def create_instances_3_days(session: Session, context):
    """Gera instâncias para 3 dias."""
    habit = context["habit"]
    today = date.today()
    instances = []
    for i in range(3):
        instance = HabitInstance(
            habit_id=habit.id,
            date=today + timedelta(days=i),
            scheduled_start=habit.scheduled_start,
            scheduled_end=habit.scheduled_end,
        )
        session.add(instance)
        instances.append(instance)
    session.commit()
    for inst in instances:
        session.refresh(inst)
    context["instances"] = instances


@given("timelogs exist for the instances")
def create_timelogs(session: Session, context):
    """Cria timelogs para as instâncias."""
    timelogs = []
    for instance in context["instances"]:
        start = datetime.combine(instance.date, time(7, 0))
        end = datetime.combine(instance.date, time(8, 0))
        timelog = TimeLog(
            habit_instance_id=instance.id,
            start_time=start,
            end_time=end,
            duration_seconds=3600,
        )
        session.add(timelog)
        timelogs.append(timelog)
    session.commit()
    context["timelogs"] = timelogs


@when("I list timelogs without filters")
def list_timelogs_no_filter(session: Session, context):
    """Lista timelogs sem filtros."""
    service = TimerService()
    context["result"] = service.list_timelogs(session=session)


@when("I list timelogs filtering by the first instance")
def list_timelogs_by_instance(session: Session, context):
    """Lista timelogs filtrando por instância."""
    service = TimerService()
    instance_id = context["instances"][0].id
    context["result"] = service.list_timelogs(habit_instance_id=instance_id, session=session)


@when("I list timelogs with date_start today and date_end today")
def list_timelogs_by_date_range(session: Session, context):
    """Lista timelogs por período."""
    service = TimerService()
    today = date.today()
    context["result"] = service.list_timelogs(
        date_start=today,
        date_end=today,
        session=session,
    )


@when("I list timelogs with date_start in distant future")
def list_timelogs_distant_future(session: Session, context):
    """Lista timelogs com data futura."""
    service = TimerService()
    future = date.today() + timedelta(days=365)
    context["result"] = service.list_timelogs(date_start=future, session=session)


@then(parsers.parse("I should receive a list with {count:d} timelogs"))
def verify_timelog_count(context, count: int):
    """Verifica quantidade de timelogs."""
    assert len(context["result"]) == count


@then(parsers.parse("I should receive a list with {count:d} timelog"))
def verify_timelog_count_singular(context, count: int):
    """Verifica quantidade de timelogs (singular)."""
    assert len(context["result"]) == count


@then("I should receive only timelogs from the first instance")
def verify_only_first_instance(context):
    """Verifica que todos timelogs são da primeira instância."""
    first_instance_id = context["instances"][0].id
    for timelog in context["result"]:
        assert timelog.habit_instance_id == first_instance_id


@then("I should receive an empty timelog list")
def verify_empty_list(context):
    """Verifica lista vazia."""
    assert context["result"] == []


@then("the timelog list should not be None")
def verify_not_none(context):
    """Verifica que resultado não é None."""
    assert context["result"] is not None
