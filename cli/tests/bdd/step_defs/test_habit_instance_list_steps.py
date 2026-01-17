"""Step definitions para BR-HABITINSTANCE-006: Listagem de Instâncias."""

from datetime import date, time, timedelta

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine
from timeblock.services.habit_instance_service import HabitInstanceService

scenarios("../features/habit_instance_list.feature")


@pytest.fixture
def context():
    """Contexto compartilhado entre steps."""
    return {}


@given('que existe uma rotina ativa "Rotina Teste"')
def rotina_ativa(session: Session, context):
    routine = Routine(name="Rotina Teste", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    context["routine"] = routine


@given('que existe um hábito "Academia" na rotina com horário 07:00-08:00')
def habito_academia(session: Session, context):
    habit = Habit(
        routine_id=context["routine"].id,
        title="Academia",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    context["habit_academia"] = habit


@given("que existem instâncias geradas para o período de 7 dias")
def instancias_7_dias(session: Session, context):
    habit = context["habit_academia"]
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
    context["instances_academia"] = instances


@given('que existe outro hábito "Meditação" na rotina')
def habito_meditacao(session: Session, context):
    habit = Habit(
        routine_id=context["routine"].id,
        title="Meditação",
        scheduled_start=time(6, 0),
        scheduled_end=time(6, 30),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    context["habit_meditacao"] = habit


@given('que existem instâncias de "Meditação" para 7 dias')
def instancias_meditacao(session: Session, context):
    habit = context["habit_meditacao"]
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


@when("eu listo instâncias sem filtros")
def listar_sem_filtros(session: Session, context):
    service = HabitInstanceService()
    context["result"] = service.list_instances(session=session)


@when('eu listo instâncias filtrando por hábito "Academia"')
def listar_por_habito(session: Session, context):
    service = HabitInstanceService()
    habit_id = context["habit_academia"].id
    context["result"] = service.list_instances(habit_id=habit_id, session=session)


@when("eu listo instâncias com data_start de hoje e data_end de hoje+2")
def listar_por_periodo(session: Session, context):
    service = HabitInstanceService()
    today = date.today()
    context["result"] = service.list_instances(
        date_start=today,
        date_end=today + timedelta(days=2),
        session=session,
    )


@when("eu listo instâncias com data_start no futuro distante")
def listar_futuro_distante(session: Session, context):
    service = HabitInstanceService()
    future = date.today() + timedelta(days=365)
    context["result"] = service.list_instances(date_start=future, session=session)


@then(parsers.parse("devo receber uma lista com {count:d} instâncias"))
def verificar_quantidade(context, count: int):
    assert len(context["result"]) == count


@then('devo receber apenas instâncias de "Academia"')
def verificar_apenas_academia(context):
    for instance in context["result"]:
        assert instance.habit.title == "Academia"


@then("devo receber uma lista vazia")
def verificar_lista_vazia(context):
    assert context["result"] == []


@then("a lista não deve ser None")
def verificar_nao_none(context):
    assert context["result"] is not None
