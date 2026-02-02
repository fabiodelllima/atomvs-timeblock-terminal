"""Testes CRUD para HabitInstanceService seguindo ADR-007."""

from datetime import date, time

from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine
from timeblock.services.habit_instance_service import HabitInstanceService


class TestHabitInstanceServiceGetInstance:
    """ADR-007: get_instance() pattern."""

    def test_get_instance_returns_existing(self, session: Session):
        """ADR-007: get_instance retorna HabitInstance se existe."""
        # Arrange: criar routine, habit, instance
        routine = Routine(name="Test Routine", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
        )
        session.add(instance)
        session.commit()
        session.refresh(instance)

        # Act: chamar método que não existe ainda
        service = HabitInstanceService()
        result = service.get_instance(instance.id, session)

        # Assert
        assert result is not None
        assert result.id == instance.id

    def test_get_instance_returns_none_if_not_exists(self, session: Session):
        """ADR-007: get_instance retorna None se não existe."""
        # Act: chamar método que não existe ainda
        service = HabitInstanceService()
        result = service.get_instance(999999, session)

        # Assert
        assert result is None
