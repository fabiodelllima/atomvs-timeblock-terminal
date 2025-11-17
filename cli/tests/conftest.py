"""Shared fixtures for query tests."""

from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from src.timeblock.models import Event, EventStatus
from src.timeblock.services.routine_service import RoutineService


@pytest.fixture
def test_engine() -> Engine:
    """Engine SQLite em memória para testes isolados."""
    engine = create_engine("sqlite:///:memory:")

    # Habilitar foreign keys no SQLite (CRÍTICO para RESTRICT)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(  # noqa: ARG001
        dbapi_conn: Any,
        connection_record: Any,  # noqa: ARG001
    ) -> None:
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def sample_event(test_engine: Engine) -> Event:
    """Cria evento de exemplo para testes."""
    with Session(test_engine) as session:
        event = Event(
            title="Sample Event",
            scheduled_start=datetime.now(UTC),
            scheduled_end=datetime.now(UTC) + timedelta(hours=1),
            status=EventStatus.PLANNED,
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return event


@pytest.fixture
def session(test_engine: Engine) -> Generator[Session]:
    """Sessão de banco de dados para testes."""
    with Session(test_engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def routine_service(test_engine: Engine):
    """Helper para criar RoutineService com session."""
    def _create_routine(name: str, auto_activate: bool = False):
        with Session(test_engine) as session:
            service = RoutineService(session)
            routine = service.create_routine(name, auto_activate)
            session.commit()
            session.refresh(routine)
            return routine
    return _create_routine


@pytest.fixture
def routine_delete_helper(test_engine: Engine):
    """Helper para deletar routine (hard delete)."""
    def _hard_delete(routine_id: int, force: bool = False):
        with Session(test_engine) as session:
            service = RoutineService(session)
            service.hard_delete_routine(routine_id, force)
            session.commit()
    return _hard_delete


@pytest.fixture
def habit_service_helper(test_engine: Engine):
    """Helper para criar habits no test_engine."""
    def _create_habit(routine_id: int, title: str, scheduled_start, scheduled_end, recurrence, color=None):
        from src.timeblock.models import Habit
        with Session(test_engine) as session:
            habit = Habit(
                routine_id=routine_id,
                title=title.strip(),
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                recurrence=recurrence,
                color=color,
            )
            session.add(habit)
            session.commit()
            session.refresh(habit)
            return habit
    return _create_habit
