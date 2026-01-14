"""Testes para HabitInstanceService.

BRs validadas:
- BR-HABITINSTANCE-005: Edição de Instancia
- BR-REORDER-001: Definição de Conflito
"""

from datetime import date, datetime, time, timedelta

import pytest
from sqlmodel import Session

from src.timeblock.models import (
    Habit,
    HabitInstance,
    Routine,
    Status,
)
from src.timeblock.services.habit_instance_service import HabitInstanceService
from src.timeblock.services.task_service import TaskService


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock engine context para todos os services."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "src.timeblock.services.habit_instance_service.get_engine_context",
        mock_get_engine,
    )
    monkeypatch.setattr(
        "src.timeblock.services.task_service.get_engine_context",
        mock_get_engine,
    )
    monkeypatch.setattr(
        "src.timeblock.services.event_reordering_service.get_engine_context",
        mock_get_engine,
    )


@pytest.fixture
def sample_instance(session: Session) -> HabitInstance:
    """Cria instância de teste."""
    routine = Routine(name="Test Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Test Habit",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence="EVERYDAY",
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)

    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance


class TestAdjustInstanceTimeBasic:
    """Tests for adjust_instance_time. Validates BR-HABITINSTANCE-005."""

    def test_adjust_time_successfully(self, sample_instance: HabitInstance) -> None:
        """Adjusts time successfully."""
        updated, conflicts = HabitInstanceService.adjust_instance_time(
            sample_instance.id, time(9, 0), time(10, 0)
        )
        assert updated.scheduled_start == time(9, 0)
        assert updated.scheduled_end == time(10, 0)
        assert conflicts == []

    def test_adjust_time_invalid(self, sample_instance: HabitInstance) -> None:
        """Rejects invalid time range."""
        with pytest.raises(ValueError):
            HabitInstanceService.adjust_instance_time(
                sample_instance.id, time(10, 0), time(9, 0)
            )

    def test_adjust_time_nonexistent(self) -> None:
        """Raises error for nonexistent instance."""
        with pytest.raises(ValueError):
            HabitInstanceService.adjust_instance_time(999, time(9, 0), time(10, 0))

    def test_returns_tuple(self, sample_instance: HabitInstance) -> None:
        """Returns tuple (instance, conflicts)."""
        result = HabitInstanceService.adjust_instance_time(
            sample_instance.id, time(9, 0), time(10, 0)
        )
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestConflictDetection:
    """Tests for conflict detection. Validates BR-REORDER-001."""

    def test_detect_conflict_with_task(
        self, sample_instance: HabitInstance
    ) -> None:
        """Detects conflict with overlapping task."""
        now = datetime.combine(date.today(), time(9, 30))
        TaskService.create_task("Reunião", now, 60)

        _updated, conflicts = HabitInstanceService.adjust_instance_time(
            sample_instance.id, time(9, 0), time(10, 30)
        )

        assert len(conflicts) > 0

    def test_no_conflict_different_day(self, session: Session) -> None:
        """No conflict when events are on different days."""
        routine = Routine(name="Test Routine")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence="EVERYDAY",
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        inst1 = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            status=Status.PENDING,
        )
        inst2 = HabitInstance(
            habit_id=habit.id,
            date=date.today() + timedelta(days=1),
            scheduled_start=time(15, 0),
            scheduled_end=time(16, 0),
            status=Status.PENDING,
        )
        session.add_all([inst1, inst2])
        session.commit()
        session.refresh(inst2)

        _updated, conflicts = HabitInstanceService.adjust_instance_time(
            inst2.id, time(9, 0), time(10, 0)
        )
        assert conflicts == []
