"""Testes para mark_completed com done_substatus obrigatório (BR-HABITINSTANCE-002).

Validates:
    - BR-HABITINSTANCE-002: Status finais requerem substatus correspondente
    - DT-034: mark_completed sem done_substatus (corrigido)
"""

from datetime import date, time

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine, Status
from timeblock.models.enums import DoneSubstatus, SkipReason
from timeblock.services.habit_instance_service import HabitInstanceService


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch: pytest.MonkeyPatch, test_engine: Engine) -> None:
    """Mock get_engine_context para usar banco de teste."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "timeblock.services.habit_instance_service.get_engine_context",
        mock_get_engine,
    )


@pytest.fixture()
def everyday_habit(session: Session) -> Habit:
    """Cria rotina + hábito diário para testes."""
    routine = Routine(name="Rotina Mark Completed")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        routine_id=routine.id,
        title="Hábito de Teste",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        target_minutes=60,
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@pytest.fixture()
def pending_instance(everyday_habit: Habit) -> "HabitInstance":
    """Gera instância PENDING para hoje."""
    assert everyday_habit.id is not None
    instances = HabitInstanceService.generate_instances(
        everyday_habit.id, date.today(), date.today()
    )
    assert len(instances) > 0
    return instances[0]


@pytest.fixture()
def skipped_instance(pending_instance: "HabitInstance") -> "HabitInstance":
    """Cria instância previamente skipped (HEALTH + nota)."""
    assert pending_instance.id is not None
    return HabitInstanceService.skip_habit_instance(
        pending_instance.id,
        skip_reason=SkipReason.HEALTH,
        skip_note="Gripe forte",
    )


class TestBRHabitinstance002DoneSetsSubstatus:
    """mark_completed seta done_substatus corretamente (BR-HABITINSTANCE-002)."""

    def test_br_habitinstance_002_done_sets_substatus_full(
        self, pending_instance: "HabitInstance"
    ) -> None:
        """FULL substatus é gravado corretamente."""
        assert pending_instance.id is not None
        result = HabitInstanceService.mark_completed(
            pending_instance.id, done_substatus=DoneSubstatus.FULL
        )
        assert result is not None
        assert result.status == Status.DONE
        assert result.done_substatus == DoneSubstatus.FULL

    def test_br_habitinstance_002_done_sets_substatus_partial(
        self, pending_instance: "HabitInstance"
    ) -> None:
        """PARTIAL substatus é gravado corretamente."""
        assert pending_instance.id is not None
        result = HabitInstanceService.mark_completed(
            pending_instance.id, done_substatus=DoneSubstatus.PARTIAL
        )
        assert result is not None
        assert result.status == Status.DONE
        assert result.done_substatus == DoneSubstatus.PARTIAL

    def test_br_habitinstance_002_done_sets_substatus_overdone(
        self, pending_instance: "HabitInstance"
    ) -> None:
        """OVERDONE substatus é gravado corretamente."""
        assert pending_instance.id is not None
        result = HabitInstanceService.mark_completed(
            pending_instance.id, done_substatus=DoneSubstatus.OVERDONE
        )
        assert result is not None
        assert result.status == Status.DONE
        assert result.done_substatus == DoneSubstatus.OVERDONE

    def test_br_habitinstance_002_done_sets_substatus_excessive(
        self, pending_instance: "HabitInstance"
    ) -> None:
        """EXCESSIVE substatus é gravado corretamente."""
        assert pending_instance.id is not None
        result = HabitInstanceService.mark_completed(
            pending_instance.id, done_substatus=DoneSubstatus.EXCESSIVE
        )
        assert result is not None
        assert result.status == Status.DONE
        assert result.done_substatus == DoneSubstatus.EXCESSIVE


class TestBRHabitinstance002DoneClearsConflicts:
    """mark_completed limpa campos conflitantes (BR-HABITINSTANCE-002)."""

    def test_br_habitinstance_002_done_clears_skip_fields(
        self, skipped_instance: "HabitInstance"
    ) -> None:
        """Done sobre instância skipped limpa skip_reason, skip_note, not_done_substatus."""
        assert skipped_instance.id is not None
        assert skipped_instance.status == Status.NOT_DONE
        assert skipped_instance.skip_reason == SkipReason.HEALTH
        assert skipped_instance.skip_note == "Gripe forte"

        result = HabitInstanceService.mark_completed(
            skipped_instance.id, done_substatus=DoneSubstatus.FULL
        )

        assert result is not None
        assert result.status == Status.DONE
        assert result.done_substatus == DoneSubstatus.FULL
        assert result.not_done_substatus is None
        assert result.skip_reason is None
        assert result.skip_note is None
        assert result.completion_percentage is None

    def test_br_habitinstance_002_done_validates_consistency(
        self, pending_instance: "HabitInstance"
    ) -> None:
        """mark_completed chama validate_status_consistency() antes de persistir."""
        assert pending_instance.id is not None
        result = HabitInstanceService.mark_completed(
            pending_instance.id, done_substatus=DoneSubstatus.FULL
        )
        assert result is not None
        result.validate_status_consistency()


class TestBRHabitinstance002DoneEdgeCases:
    """Casos-limite de mark_completed (BR-HABITINSTANCE-002)."""

    def test_br_habitinstance_002_done_nonexistent_returns_none(self) -> None:
        """Instância inexistente retorna None."""
        result = HabitInstanceService.mark_completed(99999, done_substatus=DoneSubstatus.FULL)
        assert result is None
