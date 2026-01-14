"""Testes estendidos para HabitInstanceService - Sprint 1.2 Fase 2.

BRs validadas:
- BR-HABIT-003: Geração de Instâncias
- BR-HABITINSTANCE-001: Status Principal
- BR-SKIP-001: Categorização de Skip
"""

from datetime import date, time, timedelta

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session

from src.timeblock.models import Habit, Recurrence, Routine, Status
from src.timeblock.services.habit_instance_service import HabitInstanceService


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine: Engine):
    """Mock get_engine_context para usar banco de teste."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "src.timeblock.services.habit_instance_service.get_engine_context",
        mock_get_engine,
    )


@pytest.fixture
def everyday_habit(session: Session) -> Habit:
    """Cria hábito com recorrência EVERYDAY."""
    routine = Routine(name="Rotina Matinal")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Exercício Matinal",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@pytest.fixture
def weekdays_habit(session: Session) -> Habit:
    """Cria hábito com recorrência WEEKDAYS."""
    routine = Routine(name="Rotina de Trabalho")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Revisão do Trabalho",
        scheduled_start=time(9, 0),
        scheduled_end=time(9, 30),
        recurrence=Recurrence.WEEKDAYS,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


class TestGenerateInstances:
    """Testa método generate_instances(). Validates BR-HABIT-003."""

    def test_generate_everyday_habit(self, everyday_habit: Habit) -> None:
        """Gera instâncias para hábito EVERYDAY durante 7 dias."""
        start = date.today()
        end = start + timedelta(days=6)

        instances = HabitInstanceService.generate_instances(everyday_habit.id, start, end)

        assert len(instances) == 7

        expected_dates = [start + timedelta(days=i) for i in range(7)]
        actual_dates = [inst.date for inst in instances]
        assert actual_dates == expected_dates

        for inst in instances:
            assert inst.scheduled_start == time(7, 0)
            assert inst.scheduled_end == time(8, 0)
            assert inst.status == Status.PENDING

    def test_generate_weekdays_only(self, weekdays_habit: Habit) -> None:
        """Gera instâncias para hábito WEEKDAYS - pula fins de semana."""
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        monday = today + timedelta(days=days_until_monday)
        sunday = monday + timedelta(days=6)

        instances = HabitInstanceService.generate_instances(weekdays_habit.id, monday, sunday)

        assert len(instances) == 5

        for inst in instances:
            weekday = inst.date.weekday()
            assert weekday < 5, f"Instância no fim de semana: {inst.date}"

    def test_generate_habit_not_found(self) -> None:
        """Gerar instâncias para hábito inexistente levanta erro."""
        with pytest.raises(ValueError, match="Habit 99999 not found"):
            HabitInstanceService.generate_instances(
                99999, date.today(), date.today() + timedelta(days=7)
            )

    def test_generate_single_day(self, everyday_habit: Habit) -> None:
        """Gera instâncias para período de um único dia."""
        target_date = date.today()

        instances = HabitInstanceService.generate_instances(
            everyday_habit.id, target_date, target_date
        )

        assert len(instances) == 1
        assert instances[0].date == target_date


class TestMarkCompleted:
    """Testa método mark_completed(). Validates BR-HABITINSTANCE-001."""

    def test_mark_completed_success(self, everyday_habit: Habit) -> None:
        """Marca instância como completada com sucesso."""
        instances = HabitInstanceService.generate_instances(
            everyday_habit.id, date.today(), date.today()
        )
        instance_id = instances[0].id

        updated = HabitInstanceService.mark_completed(instance_id)

        assert updated is not None
        assert updated.status == Status.DONE

    def test_mark_completed_nonexistent(self) -> None:
        """Marcar instância inexistente retorna None."""
        result = HabitInstanceService.mark_completed(99999)
        assert result is None


class TestMarkSkipped:
    """Testa método mark_skipped(). Validates BR-SKIP-001."""

    def test_mark_skipped_success(self, everyday_habit: Habit) -> None:
        """Marca instância como pulada com sucesso."""
        instances = HabitInstanceService.generate_instances(
            everyday_habit.id, date.today(), date.today()
        )
        instance_id = instances[0].id

        updated = HabitInstanceService.mark_skipped(instance_id)

        assert updated is not None
        assert updated.status == Status.NOT_DONE

    def test_mark_skipped_nonexistent(self) -> None:
        """Marcar instância inexistente retorna None."""
        result = HabitInstanceService.mark_skipped(99999)
        assert result is None
