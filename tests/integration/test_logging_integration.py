"""Testes de integração para logging nos services (DT-022).

Referências:
    - DT-022: Logging estruturado
    - ADR-019: Test Naming Convention
"""

import os
import tempfile
from datetime import date, time, timedelta
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, create_engine

from timeblock.models import Habit, Recurrence, Routine
from timeblock.services.habit_instance_service import HabitInstanceService
from timeblock.utils.logger import (
    _reset_for_testing,
    configure_logging,
    disable_logging,
    enable_logging,
)


@pytest.fixture(autouse=True)
def _reset_logging():
    """Reseta estado do logging entre cada teste."""
    _reset_for_testing()
    yield
    _reset_for_testing()
    enable_logging()


@pytest.fixture
def test_engine():
    """Engine SQLite em memória para testes isolados."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine):
    """Mock get_engine_context para usar banco de teste."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "timeblock.services.habit_instance_service.get_engine_context", mock_get_engine
    )


@pytest.fixture
def habit(test_engine):
    """Cria hábito de teste."""
    with Session(test_engine) as session:
        routine = Routine(name="Test Routine")
        session.add(routine)
        session.commit()
        session.refresh(routine)

        habit = Habit(
            routine_id=routine.id,
            title="Test Habit",
            scheduled_start=time(7, 0),
            scheduled_end=time(8, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit


class TestServiceLogging:
    """Testa logs gerados pelos services."""

    def test_generate_instances_logs(self, habit):
        """Verifica logs ao gerar instâncias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "service.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True, level="INFO")
                start = date.today()
                end = start + timedelta(days=6)
                _instances = HabitInstanceService.generate_instances(habit.id, start, end)

                for handler in __import__("logging").getLogger("timeblock").handlers:
                    handler.flush()

                content = log_path.read_text()
                assert "Gerando" in content
                assert f"habit_id={habit.id}" in content
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)

    def test_error_logs(self):
        """Verifica logs de erro ao tentar operação inválida."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "service.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True, level="ERROR")
                with pytest.raises(ValueError):
                    HabitInstanceService.generate_instances(99999, date.today(), date.today())

                for handler in __import__("logging").getLogger("timeblock").handlers:
                    handler.flush()

                content = log_path.read_text()
                assert "não encontrado" in content or "not found" in content.lower()
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)

    def test_disable_suppresses_service_logs(self, habit):
        """disable_logging suprime logs dos services."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "service.jsonl"
            os.environ["ATOMVS_LOG_FILE"] = str(log_path)
            try:
                configure_logging(console=False, log_file=True)
                disable_logging()
                _instances = HabitInstanceService.generate_instances(
                    habit.id, date.today(), date.today()
                )

                for handler in __import__("logging").getLogger("timeblock").handlers:
                    handler.flush()

                if log_path.exists():
                    assert log_path.read_text().strip() == ""
            finally:
                os.environ.pop("ATOMVS_LOG_FILE", None)
                enable_logging()
