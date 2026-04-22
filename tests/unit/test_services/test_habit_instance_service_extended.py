"""Testes estendidos para HabitInstanceService - Sprint 1.2 Fase 2.

BRs validadas:
- BR-HABIT-003: Geração de Instâncias
- BR-HABITINSTANCE-001: Status Principal
- BR-SKIP-001: Categorização de Skip
"""

from datetime import date, time, timedelta

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from timeblock.models import Habit, HabitInstance, Recurrence, Routine, Status
from timeblock.models.enums import DoneSubstatus
from timeblock.services.habit_instance_service import HabitInstanceService


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine: Engine):
    """Mock get_engine_context para usar banco de teste."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr(
        "timeblock.services.habit_instance_service.get_engine_context",
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


class TestGenerateInstancesIdempotency:
    """Testa idempotência de generate_instances().

    Reproduz e previne regressão do bug da issue #2: chamadas repetidas
    de generate_instances para o mesmo (habit_id, date) criavam duplicatas
    ao invés de pular existentes. A BR-HABIT-003 documenta explicitamente
    "Não duplica instâncias existentes" como comportamento esperado.
    """

    def test_generate_is_idempotent_for_same_period(
        self, everyday_habit: Habit, session: Session
    ) -> None:
        """Chamar generate_instances duas vezes para o mesmo período não duplica.

        DADO: hábito EVERYDAY e período de 7 dias
        QUANDO: generate_instances é chamado duas vezes seguidas
        ENTÃO: o banco contém exatamente uma instância por (habit_id, date),
               não duas.
        """
        assert everyday_habit.id is not None, "fixture everyday_habit deve ter id após commit"
        habit_id = everyday_habit.id

        start = date.today()
        end = start + timedelta(days=6)

        first = HabitInstanceService.generate_instances(habit_id, start, end)
        assert len(first) == 7, "primeira geração deve criar 7 instâncias"

        second = HabitInstanceService.generate_instances(habit_id, start, end)

        # Verifica estado real do banco, não apenas o retorno do método.
        # Se o fix escolher retornar [] na segunda chamada mas ainda inserir
        # no banco, o retorno engana — só a query direta detecta duplicata.
        rows = session.exec(select(HabitInstance).where(HabitInstance.habit_id == habit_id)).all()
        assert len(rows) == 7, (
            f"Esperava 7 instâncias no banco após dupla geração, encontrou {len(rows)}. "
            f"generate_instances não está sendo idempotente — reintroduziu bug da issue #2."
        )

        # Segunda chamada deve devolver lista vazia (nada novo foi criado),
        # sinalizando idempotência ao chamador.
        assert second == [], (
            f"Segunda chamada deveria retornar [] (nada criado), retornou {len(second)} itens"
        )


class TestMarkCompleted:
    """Testa método mark_completed(). Validates BR-HABITINSTANCE-001."""

    def test_mark_completed_success(self, everyday_habit: Habit) -> None:
        """Marca instância como completada com sucesso."""
        instances = HabitInstanceService.generate_instances(
            everyday_habit.id, date.today(), date.today()
        )
        instance_id = instances[0].id

        updated = HabitInstanceService.mark_completed(
            instance_id, done_substatus=DoneSubstatus.FULL
        )

        assert updated is not None
        assert updated.status == Status.DONE
        assert updated.done_substatus == DoneSubstatus.FULL

    def test_mark_completed_nonexistent(self) -> None:
        """Marcar instância inexistente retorna None."""
        result = HabitInstanceService.mark_completed(99999, done_substatus=DoneSubstatus.FULL)
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
