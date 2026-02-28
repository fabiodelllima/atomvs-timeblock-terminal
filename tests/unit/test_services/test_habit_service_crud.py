"""Testes para HabitService - operações CRUD.

BRs validadas:
- BR-HABIT-001: Estrutura de Habito
- BR-HABIT-004: Modificação de Habito
- BR-HABIT-005: Deleção de Habito
"""

from datetime import time

import pytest
from sqlmodel import Session

from timeblock.models import Recurrence, Routine
from timeblock.services.habit_service import HabitService


@pytest.fixture
def test_routine(session: Session) -> Routine:
    """Cria rotina de teste."""
    routine = Routine(name="Test Routine", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


class TestCreateHabit:
    """Testes para create_habit. Validates BR-HABIT-001."""

    def test_create_habit_success(self, session: Session, test_routine: Routine) -> None:
        """Cria hábito com sucesso."""
        habit_service = HabitService(session)
        habit = habit_service.create_habit(
            routine_id=test_routine.id,
            title="Exercício",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        assert habit.id is not None
        assert habit.title == "Exercício"
        assert habit.routine_id == test_routine.id

    def test_create_habit_with_color(self, session: Session, test_routine: Routine) -> None:
        """Cria hábito com cor."""
        habit_service = HabitService(session)
        habit = habit_service.create_habit(
            routine_id=test_routine.id,
            title="Meditação",
            scheduled_start=time(6, 0),
            scheduled_end=time(6, 30),
            recurrence=Recurrence.WEEKDAYS,
            color="#FF5733",
        )
        assert habit.color == "#FF5733"

    def test_create_habit_strips_whitespace(self, session: Session, test_routine: Routine) -> None:
        """Remove espaços do título."""
        habit_service = HabitService(session)
        habit = habit_service.create_habit(
            routine_id=test_routine.id,
            title="  Leitura  ",
            scheduled_start=time(20, 0),
            scheduled_end=time(21, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        assert habit.title == "Leitura"

    def test_create_habit_with_empty_title(self, session: Session, test_routine: Routine) -> None:
        """Rejeita título vazio."""
        habit_service = HabitService(session)
        with pytest.raises(ValueError, match="cannot be empty"):
            habit_service.create_habit(
                routine_id=test_routine.id,
                title="   ",
                scheduled_start=time(10, 0),
                scheduled_end=time(11, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_create_habit_with_title_too_long(
        self, session: Session, test_routine: Routine
    ) -> None:
        """Rejeita título muito longo."""
        habit_service = HabitService(session)
        with pytest.raises(ValueError, match="cannot exceed 200"):
            habit_service.create_habit(
                routine_id=test_routine.id,
                title="X" * 201,
                scheduled_start=time(10, 0),
                scheduled_end=time(11, 0),
                recurrence=Recurrence.EVERYDAY,
            )

    def test_create_habit_with_invalid_times(self, session: Session, test_routine: Routine) -> None:
        """Rejeita start >= end."""
        habit_service = HabitService(session)
        with pytest.raises(ValueError, match="Start time must be before end time"):
            habit_service.create_habit(
                routine_id=test_routine.id,
                title="Inválido",
                scheduled_start=time(10, 0),
                scheduled_end=time(9, 0),
                recurrence=Recurrence.EVERYDAY,
            )


class TestGetHabit:
    """Testes para get_habit."""

    def test_get_habit_found(self, session: Session, test_routine: Routine) -> None:
        """Busca hábito existente."""
        habit_service = HabitService(session)
        created = habit_service.create_habit(
            routine_id=test_routine.id,
            title="Yoga",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        found = habit_service.get_habit(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.title == "Yoga"

    def test_get_habit_not_found(self, session: Session) -> None:
        """Retorna None para ID inexistente."""
        habit_service = HabitService(session)
        assert habit_service.get_habit(9999) is None


class TestListHabits:
    """Testes para list_habits."""

    def test_list_habits_all(self, session: Session, test_routine: Routine) -> None:
        """Lista todos os hábitos."""
        routine2 = Routine(name="Routine 2", is_active=True)
        session.add(routine2)
        session.commit()
        session.refresh(routine2)

        habit_service = HabitService(session)
        habit_service.create_habit(
            routine_id=test_routine.id,
            title="Habit 1",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        habit_service.create_habit(
            routine_id=routine2.id,
            title="Habit 2",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.WEEKDAYS,
        )

        habits = habit_service.list_habits()
        assert len(habits) == 2

    def test_list_habits_by_routine(self, session: Session, test_routine: Routine) -> None:
        """Filtra hábitos por rotina."""
        routine2 = Routine(name="Routine 2", is_active=True)
        session.add(routine2)
        session.commit()
        session.refresh(routine2)

        habit_service = HabitService(session)
        habit_service.create_habit(
            routine_id=test_routine.id,
            title="Habit 1",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        habit_service.create_habit(
            routine_id=routine2.id,
            title="Habit 2",
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.WEEKDAYS,
        )

        habits = habit_service.list_habits(routine_id=test_routine.id)
        assert len(habits) == 1
        assert habits[0].routine_id == test_routine.id

    def test_list_habits_empty(self, session: Session) -> None:
        """Retorna lista vazia."""
        habit_service = HabitService(session)
        assert habit_service.list_habits() == []
