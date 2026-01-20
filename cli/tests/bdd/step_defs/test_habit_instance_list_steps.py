"""Step definitions for BR-HABITINSTANCE-006: Instance Listing."""

from datetime import date, time, timedelta

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine
from timeblock.services.habit_instance_service import HabitInstanceService

scenarios("../features/habit_instance_list.feature")


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


@given('a habit "Gym" exists in the routine with schedule 07:00-08:00')
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
    context["habit_gym"] = habit


@given("instances are generated for 7 days")
def create_instances_7_days(session: Session, context):
    """Gera instâncias para 7 dias."""
    habit = context["habit_gym"]
    today = date.today()
    instances = []
    for i in range(7):
        instance = HabitInstance(
            habit_id=habit.id,
            date=today + timedelta(days=i),
            scheduled_start=habit.scheduled_start,
            scheduled_end=habit.scheduled_end,
        )
        session.add(instance)
        instances.append(instance)
    session.commit()
    context["instances_gym"] = instances


@given('another habit "Meditation" exists in the routine')
def create_habit_meditation(session: Session, context):
    """Cria hábito Meditation na rotina."""
    habit = Habit(
        routine_id=context["routine"].id,
        title="Meditation",
        scheduled_start=time(6, 0),
        scheduled_end=time(6, 30),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    context["habit_meditation"] = habit


@given('instances of "Meditation" exist for 7 days')
def create_meditation_instances(session: Session, context):
    """Gera instâncias de Meditation para 7 dias."""
    habit = context["habit_meditation"]
    today = date.today()
    for i in range(7):
        instance = HabitInstance(
            habit_id=habit.id,
            date=today + timedelta(days=i),
            scheduled_start=habit.scheduled_start,
            scheduled_end=habit.scheduled_end,
        )
        session.add(instance)
    session.commit()


@when("I list instances without filters")
def list_instances_no_filter(session: Session, context):
    """Lista instâncias sem filtros."""
    service = HabitInstanceService()
    context["result"] = service.list_instances(session=session)


@when('I list instances filtering by habit "Gym"')
def list_instances_by_habit(session: Session, context):
    """Lista instâncias filtrando por hábito."""
    service = HabitInstanceService()
    habit_id = context["habit_gym"].id
    context["result"] = service.list_instances(habit_id=habit_id, session=session)


@when("I list instances with date_start today and date_end today+2")
def list_instances_by_date_range(session: Session, context):
    """Lista instâncias por período."""
    service = HabitInstanceService()
    today = date.today()
    context["result"] = service.list_instances(
        date_start=today,
        date_end=today + timedelta(days=2),
        session=session,
    )


@when("I list instances with date_start in distant future")
def list_instances_distant_future(session: Session, context):
    """Lista instâncias com data futura."""
    service = HabitInstanceService()
    future = date.today() + timedelta(days=365)
    context["result"] = service.list_instances(date_start=future, session=session)


@then(parsers.parse("I should receive a list with {count:d} instances"))
def verify_instance_count(context, count: int):
    """Verifica quantidade de instâncias."""
    assert len(context["result"]) == count


@then('I should receive only "Gym" instances')
def verify_only_gym_instances(context):
    """Verifica que todas instâncias são de Gym."""
    for instance in context["result"]:
        assert instance.habit.title == "Gym"


@then("I should receive an empty list")
def verify_empty_list(context):
    """Verifica lista vazia."""
    assert context["result"] == []


@then("the list should not be None")
def verify_not_none(context):
    """Verifica que resultado não é None."""
    assert context["result"] is not None
