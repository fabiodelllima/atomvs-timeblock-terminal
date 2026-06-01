"""Shared fixtures for query tests."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from datetime import UTC, datetime, time
from typing import TYPE_CHECKING, Any

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from timeblock.models import (
    Event,
    EventStatus,
    Habit,
    Recurrence,
)
from timeblock.services.routine_service import RoutineService

if TYPE_CHECKING:
    from collections.abc import Callable

    from timeblock.services.habit_service import HabitService


@pytest.fixture(autouse=True, scope="session")
def _isolate_production_database() -> Generator[None]:
    """Isola toda a suíte do banco de produção XDG (BR-TEST-003 / DT-078).

    Força TIMEBLOCK_DB_PATH para um arquivo temporário de sessão caso a
    variável não esteja definida, garantindo que nenhum teste resolva
    get_db_path() para ~/.local/share/atomvs/atomvs.db. Fixturas mais
    específicas (test_tui com :memory:, isolated_db com tmp próprio)
    sobrescrevem este piso. O valor original é restaurado ao final.

    Usa tempfile.mkdtemp() em vez de tmp_path_factory porque a fixture
    de sessão do pytest, quando resolvida dentro de uma autouse de
    escopo sessão, causa deadlock na coleta (DT-078).

    Referências:
        - BR-TEST-003: Isolamento Absoluto do Banco de Produção
        - DT-078: Testes de integração sem guarda global de banco isolado
        - ADR-026: Test Database Isolation Strategy
    """
    original = os.environ.get("TIMEBLOCK_DB_PATH")
    if original is None:
        tmp_dir = tempfile.mkdtemp(prefix="atomvs_suite_")
        os.environ["TIMEBLOCK_DB_PATH"] = os.path.join(tmp_dir, "test_suite.db")
    yield
    if original is None:
        os.environ.pop("TIMEBLOCK_DB_PATH", None)
    else:
        os.environ["TIMEBLOCK_DB_PATH"] = original


@pytest.fixture
def test_engine() -> Generator[Engine]:
    """Engine SQLite em memória para testes isolados."""
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(
        dbapi_conn: Any,
        _connection_record: Any,
    ) -> None:
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(test_engine: Engine) -> Generator[Session]:
    """Sessão de banco de dados para testes."""
    with Session(test_engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def test_db(session: Session) -> Session:
    """Alias para session (compatibilidade com testes antigos)."""
    return session


@pytest.fixture
def routine_service(session: Session) -> RoutineService:
    """Fixture que retorna instância de RoutineService."""
    return RoutineService(session)


@pytest.fixture
def habit_service(session: Session) -> HabitService:
    """Fixture que retorna instância de HabitService."""
    from timeblock.services.habit_service import HabitService

    return HabitService(session)


@pytest.fixture
def habit_service_helper(session: Session) -> Callable[..., Habit]:
    """Helper para criar habits usando session injetada."""
    from timeblock.services.habit_service import HabitService

    service = HabitService(session)

    def _create_habit(
        routine_id: int,
        title: str,
        scheduled_start: time,
        scheduled_end: time,
        recurrence: Recurrence,
        color: str | None = None,
    ) -> Habit:
        return service.create_habit(
            routine_id=routine_id,
            title=title,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            recurrence=recurrence,
            color=color,
        )

    return _create_habit


@pytest.fixture
def routine_delete_helper(
    session: Session,
) -> Callable[[int], None]:
    """Helper para deletar routines no test_engine."""

    def _delete_routine(routine_id: int) -> None:
        service = RoutineService(session)
        service.delete_routine(routine_id)

    return _delete_routine


@pytest.fixture
def sample_time_start() -> time:
    """Fixture que retorna hora de início padrão."""
    return time(9, 0)


@pytest.fixture
def sample_time_end() -> time:
    """Fixture que retorna hora de fim padrão."""
    return time(10, 0)


@pytest.fixture
def sample_date() -> datetime:
    """Fixture que retorna data padrão."""
    return datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)


@pytest.fixture
def sample_event(
    session: Session,
    sample_date: datetime,
) -> Event:
    """Fixture que cria um evento de exemplo."""
    start = sample_date.replace(hour=9, minute=0)
    end = sample_date.replace(hour=10, minute=0)
    event_obj = Event(
        title="Sample Event",
        scheduled_start=start,
        scheduled_end=end,
        status=EventStatus.PLANNED,
    )
    session.add(event_obj)
    session.commit()
    session.refresh(event_obj)
    return event_obj


@pytest.fixture
def mock_session() -> Any:
    """Mock de session para testes de services."""
    from unittest.mock import Mock

    session = Mock()
    session.get.return_value = None
    session.exec.return_value.all.return_value = []
    session.commit.return_value = None
    return session
