"""Testes para HabitService - operações de update e delete.

BRs validadas:
- BR-HABIT-004: Modificação de Habito
- BR-HABIT-005: Deleção de Habito
"""

from datetime import time

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session

from timeblock.models import Habit, Recurrence, Routine
from timeblock.services.habit_service import HabitService


@pytest.fixture
def test_routine(session: Session) -> Routine:
    """Cria rotina de teste."""
    routine = Routine(name="Test Routine", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)
    return routine


@pytest.fixture
def test_habit(test_routine: Routine) -> Habit:
    """Cria hábito de teste."""
    return HabitService.create_habit(
        routine_id=test_routine.id,
        title="Test Habit",
        scheduled_start=time(10, 0),
        scheduled_end=time(11, 0),
        recurrence=Recurrence.EVERYDAY,
    )


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine: Engine):
    """Mock do get_engine_context."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr("timeblock.services.habit_service.get_engine_context", mock_get_engine)


class TestUpdateHabit:
    """Testes para update_habit. Validates BR-HABIT-004."""

    def test_update_habit_title(self, test_habit: Habit) -> None:
        """Atualiza título."""
        updated = HabitService.update_habit(test_habit.id, title="Novo Título")
        assert updated is not None
        assert updated.title == "Novo Título"

    def test_update_habit_times(self, test_habit: Habit) -> None:
        """Atualiza horários."""
        updated = HabitService.update_habit(
            test_habit.id,
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
        )
        assert updated.scheduled_start == time(8, 0)
        assert updated.scheduled_end == time(9, 0)

    def test_update_habit_recurrence(self, test_habit: Habit) -> None:
        """Atualiza recorrência."""
        updated = HabitService.update_habit(
            test_habit.id,
            recurrence=Recurrence.WEEKDAYS,
        )
        assert updated.recurrence == Recurrence.WEEKDAYS

    def test_update_habit_color(self, test_habit: Habit) -> None:
        """Atualiza cor."""
        updated = HabitService.update_habit(test_habit.id, color="#FF5733")
        assert updated.color == "#FF5733"

    def test_update_habit_multiple_fields(self, test_habit: Habit) -> None:
        """Atualiza múltiplos campos."""
        updated = HabitService.update_habit(
            test_habit.id,
            title="Atualizado",
            scheduled_start=time(6, 0),
            color="#123456",
        )
        assert updated.title == "Atualizado"
        assert updated.scheduled_start == time(6, 0)
        assert updated.color == "#123456"

    def test_update_habit_not_found(self) -> None:
        """Retorna None para ID inexistente."""
        assert HabitService.update_habit(9999, title="Teste") is None

    def test_update_habit_with_empty_title(self, test_habit: Habit) -> None:
        """Rejeita título vazio."""
        with pytest.raises(ValueError, match="cannot be empty"):
            HabitService.update_habit(test_habit.id, title="   ")

    def test_update_habit_with_title_too_long(self, test_habit: Habit) -> None:
        """Rejeita título muito longo."""
        with pytest.raises(ValueError, match="cannot exceed 200"):
            HabitService.update_habit(test_habit.id, title="X" * 201)

    def test_update_habit_with_invalid_times(self, test_habit: Habit) -> None:
        """Rejeita start >= end."""
        with pytest.raises(ValueError, match="Start time must be before end time"):
            HabitService.update_habit(
                test_habit.id,
                scheduled_start=time(15, 0),
                scheduled_end=time(14, 0),
            )


class TestDeleteHabit:
    """Testes para delete_habit. Validates BR-HABIT-005."""

    def test_delete_habit_success(self, test_habit: Habit) -> None:
        """Remove hábito com sucesso."""
        assert HabitService.delete_habit(test_habit.id) is True
        assert HabitService.get_habit(test_habit.id) is None

    def test_delete_habit_not_found(self) -> None:
        """Retorna False para ID inexistente."""
        assert HabitService.delete_habit(9999) is False
