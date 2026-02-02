"""Testes para BR-ROUTINE-006: Soft Delete e Purge.

Valida BR-ROUTINE-006 isoladamente para não misturar
com o test_br_routine.py existente (BR-001 a BR-005).
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from timeblock.models import Habit, Recurrence, Routine
from timeblock.services.routine_service import RoutineService


class TestBRRoutine006:
    """Valida BR-ROUTINE-006: Soft Delete e Purge."""

    def _create_routine_with_habits(self, session: Session, name: str = "Rotina Teste") -> Routine:
        """Helper: cria rotina com habits vinculados."""
        from datetime import time

        routine = Routine(name=name, is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            title="Habit vinculado",
            routine_id=routine.id,
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.WEEKDAYS,
        )
        session.add(habit)
        session.commit()
        return routine

    def test_br_routine_006_delete_removes_routine(self, session: Session):
        """BR-ROUTINE-006: delete_routine remove rotina do banco."""
        service = RoutineService(session)
        routine = service.create_routine("Para deletar")
        session.commit()
        routine_id = routine.id

        service.delete_routine(routine_id)
        session.commit()

        assert session.get(Routine, routine_id) is None

    def test_br_routine_006_delete_nonexistent_raises(self, session: Session):
        """BR-ROUTINE-006: delete rotina inexistente lança ValueError."""
        service = RoutineService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.delete_routine(999)

    def test_br_routine_006_hard_delete_no_habits(self, session: Session):
        """BR-ROUTINE-006: hard_delete funciona em rotina sem habits."""
        routine = Routine(name="Sem habits", is_active=False)
        session.add(routine)
        session.commit()
        session.refresh(routine)
        routine_id = routine.id

        service = RoutineService(session)
        service.hard_delete_routine(routine_id)

        assert session.get(Routine, routine_id) is None

    def test_br_routine_006_hard_delete_with_habits_blocked(self, session: Session):
        """BR-ROUTINE-006: hard_delete com habits é bloqueado pelo banco (FK)."""
        routine = self._create_routine_with_habits(session)
        service = RoutineService(session)

        with pytest.raises(IntegrityError):
            service.hard_delete_routine(routine.id)

    def test_br_routine_006_hard_delete_nonexistent_raises(self, session: Session):
        """BR-ROUTINE-006: hard_delete inexistente lança ValueError."""
        service = RoutineService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.hard_delete_routine(999)

    def test_br_routine_006_deactivate_preserves_routine(self, session: Session):
        """BR-ROUTINE-006: deactivate não remove, apenas desativa."""
        service = RoutineService(session)
        routine = service.create_routine("Para desativar")
        session.commit()
        routine_id = routine.id

        service.deactivate_routine(routine_id)
        session.commit()

        persisted = session.get(Routine, routine_id)
        assert persisted is not None
        assert persisted.is_active is False
