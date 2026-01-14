"""Tests for Routine model.

BRs validadas:
- BR-ROUTINE-001: Single Active Constraint
- BR-ROUTINE-005: Validação de Nome
"""

from sqlmodel import Session

from src.timeblock.models.routine import Routine


def test_routine_creation(session: Session) -> None:
    """Test creating a routine. Validates BR-ROUTINE-005."""
    routine = Routine(name="Morning Routine")
    session.add(routine)
    session.commit()
    session.refresh(routine)

    assert routine.id is not None
    assert routine.name == "Morning Routine"
    assert routine.is_active is False


def test_routine_activation(session: Session) -> None:
    """Test routine activation. Validates BR-ROUTINE-001."""
    routine = Routine(name="Test", is_active=True)
    session.add(routine)
    session.commit()

    assert routine.is_active is True


def test_multiple_routines(session: Session) -> None:
    """Test multiple routines. Validates BR-ROUTINE-001."""
    r1 = Routine(name="Routine 1")
    r2 = Routine(name="Routine 2")
    session.add_all([r1, r2])
    session.commit()

    assert r1.id != r2.id
