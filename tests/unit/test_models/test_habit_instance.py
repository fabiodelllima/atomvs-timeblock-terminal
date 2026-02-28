"""Testes para o modelo HabitInstance.

BR validada: BR-HABITINSTANCE-001 (Status Principal)
"""

from datetime import date, time

import pytest
from sqlmodel import Session

from timeblock.models.habit import Habit, Recurrence
from timeblock.models.habit_instance import HabitInstance, Status
from timeblock.models.routine import Routine


@pytest.fixture
def habit(session: Session) -> Habit:
    """Cria hábito de teste."""
    routine = Routine(name="Test")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Exercise",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


def test_habit_instance_creation(session: Session, habit: Habit) -> None:
    """Testa criação de instância de hábito. Validates BR-HABITINSTANCE-001."""
    instance = HabitInstance(
        habit_id=habit.id,
        date=date(2025, 10, 16),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)

    assert instance.id is not None
    assert instance.date == date(2025, 10, 16)
    assert instance.status == Status.PENDING
