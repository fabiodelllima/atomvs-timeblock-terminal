"""Fixtures para testes de integração (BR-TEST-001, ADR-033).

Engine e schema criados uma vez por sessão de teste (scope="session").
Cada teste roda em transação isolada com rollback automático.
Services chamam commit() internamente — join_transaction_mode="conditional_savepoint"
converte commits em savepoint releases, mantendo o rollback funcional.

Referências:
    - ADR-033: Fixture scope="session" com rollback transacional
    - BR-TEST-001: Isolamento por rollback
    - HUMBLE; FARLEY, 2010, p. 375
    - SQLAlchemy 2.0: Joining a Session into an External Transaction
"""

from datetime import UTC, datetime, time
from typing import Any

import pytest
from sqlalchemy import Engine, event
from sqlmodel import Session, SQLModel, create_engine

from timeblock.models import Habit, Recurrence, Routine, Task


@pytest.fixture(scope="session")
def integration_engine():
    """Engine de DB em memória, criada uma vez por sessão de teste.

    Schema criado uma vez (O(1) em vez de O(N) por teste).
    Compatível com pytest-xdist: cada worker recebe engine independente.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, echo=False
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(
        dbapi_conn: Any,
        connection_record: Any,
    ) -> None:
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def integration_session(integration_engine: Engine):
    """Sessão com rollback transacional por teste.

    Cada teste recebe sessão dentro de transação externa.
    join_transaction_mode="conditional_savepoint" faz com que session.commit()
    nos services vire savepoint release (não commit real).
    Ao final do teste, a transação externa é revertida.
    """
    connection = integration_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="conditional_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_db(integration_session: Session):
    """Alias para integration_session (compatibilidade)."""
    return integration_session


@pytest.fixture
def sample_routine(integration_session: Session):
    """Rotina de exemplo para testes de integração."""
    routine = Routine(name="Test Routine", is_active=True)
    integration_session.add(routine)
    integration_session.flush()
    integration_session.refresh(routine)
    return routine


@pytest.fixture
def sample_habits(integration_session: Session, sample_routine: Routine):
    """Hábitos de exemplo para testes de integração."""
    habit1 = Habit(
        routine_id=sample_routine.id,
        title="Exercise",
        scheduled_start=time(7, 0),
        scheduled_end=time(8, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    habit2 = Habit(
        routine_id=sample_routine.id,
        title="Reading",
        scheduled_start=time(20, 0),
        scheduled_end=time(21, 0),
        recurrence=Recurrence.WEEKDAYS,
    )
    integration_session.add(habit1)
    integration_session.add(habit2)
    integration_session.flush()
    integration_session.refresh(habit1)
    integration_session.refresh(habit2)
    return [habit1, habit2]


@pytest.fixture
def sample_task(integration_session: Session):
    """Task de exemplo para testes de integração."""
    task = Task(
        title="Dentist Appointment",
        scheduled_datetime=datetime.now(UTC),
        original_scheduled_datetime=datetime.now(UTC),
    )
    integration_session.add(task)
    integration_session.flush()
    integration_session.refresh(task)
    return task
