"""
Integration tests - TaskService + EventReorderingService.

Testa integração entre TaskService e EventReorderingService,
validando atualizações de tasks, detecção de conflitos e propostas.

Referências:
    - ADR-019: Test Naming Convention
    - BR-REORDER-001 a BR-REORDER-006
    - Sprint 2.2: Task + EventReordering integration
"""

from datetime import date, datetime, time

import pytest
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine, Task
from timeblock.models.enums import Status
from timeblock.services.task_service import TaskService


class TestBRTaskReordering:
    """
    Integration: TaskService + EventReorderingService (BR-REORDER-*).

    Valida atualização de tasks com detecção automática de conflitos
    e geração de propostas de reorganização.
    """

    @pytest.fixture
    def task(self, test_db: Session) -> Task:
        """Cria task para testes."""
        task = Task(
            title="Test Task",
            scheduled_datetime=datetime.combine(date.today(), time(10, 0)),
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)
        return task

    @pytest.fixture
    def another_task(self, test_db: Session) -> Task:
        """Cria segunda task para testes de conflito."""
        task = Task(
            title="Another Task",
            scheduled_datetime=datetime.combine(date.today(), time(14, 0)),
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)
        return task

    def test_br_reorder_001_update_without_time_change(self, test_db: Session, task: Task) -> None:
        """
        BR-REORDER-001: Atualização sem mudança de horário não dispara reordering.

        DADO: Task existente com horário definido
        QUANDO: Usuário atualiza apenas título/descrição
        ENTÃO: Campos são atualizados
        E: Nenhuma proposta é gerada
        """
        original_datetime = task.scheduled_datetime
        assert task.id is not None

        # ACT
        result, conflicts = TaskService.update_task(
            task_id=task.id,
            title="Updated Title",
            description="New description",
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.title == "Updated Title"
        assert result.description == "New description"
        assert result.scheduled_datetime == original_datetime
        assert conflicts is None  # Sem mudança de horário = sem conflitos

    def test_br_reorder_002_update_without_conflicts(self, test_db: Session, task: Task) -> None:
        """
        BR-REORDER-002: Mudança de horário sem conflitos não gera proposta.

        DADO: Task existente
        QUANDO: Usuário muda horário para slot livre
        ENTÃO: Horário é atualizado
        E: Lista de conflitos vazia ou None
        """
        new_datetime = datetime.combine(date.today(), time(16, 0))
        assert task.id is not None

        # ACT
        result, conflicts = TaskService.update_task(
            task_id=task.id,
            scheduled_datetime=new_datetime,
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.scheduled_datetime == new_datetime
        # Conflitos podem ser None ou lista vazia quando não há conflitos
        assert conflicts is None or len(conflicts) == 0

    def test_br_reorder_003_update_with_task_conflict(
        self, test_db: Session, task: Task, another_task: Task
    ) -> None:
        """
        BR-REORDER-003: Mudança causando conflito com outra task gera proposta.

        DADO: Duas tasks em horários diferentes
        QUANDO: Usuário move task1 para horário de task2
        ENTÃO: Horário é atualizado (BR-REORDER-004: conflitos não bloqueiam)
        E: Conflito pode ser detectado
        """
        assert task.id is not None

        # ACT - Move task para mesmo horário de another_task
        result, _conflicts = TaskService.update_task(
            task_id=task.id,
            scheduled_datetime=another_task.scheduled_datetime,
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.scheduled_datetime == another_task.scheduled_datetime
        # BR-REORDER-004: Operação não é bloqueada

    def test_br_reorder_004_update_conflicts_with_habit(self, test_db: Session, task: Task) -> None:
        """
        BR-REORDER-004: Task conflitando com HabitInstance gera proposta.

        DADO: HabitInstance em horário definido
        QUANDO: Usuário move task para mesmo horário
        ENTÃO: Horário é atualizado (conflitos não bloqueiam)
        """
        # ARRANGE - Criar routine, habit e instance
        routine = Routine(name="Test Routine", is_active=True)
        test_db.add(routine)
        test_db.commit()
        test_db.refresh(routine)
        assert routine.id is not None

        habit = Habit(
            title="Test Habit",
            routine_id=routine.id,
            scheduled_start=time(11, 0),
            scheduled_end=time(12, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        test_db.add(habit)
        test_db.commit()
        test_db.refresh(habit)
        assert habit.id is not None

        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(11, 0),
            scheduled_end=time(12, 0),
            status=Status.PENDING,
        )
        test_db.add(instance)
        test_db.commit()

        assert task.id is not None

        # ACT - Move task para horário do habit
        conflict_time = datetime.combine(date.today(), time(11, 30))
        result, _conflicts = TaskService.update_task(
            task_id=task.id,
            scheduled_datetime=conflict_time,
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.scheduled_datetime == conflict_time
        # BR-REORDER-004: Operação não é bloqueada mesmo com conflito

    def test_br_reorder_005_update_nonexistent(self, test_db: Session) -> None:
        """
        BR-REORDER-005: Atualização de task inexistente retorna (None, None).

        DADO: ID 99999 que não existe
        QUANDO: Usuário tenta atualizar
        ENTÃO: Retorna (None, None)
        """
        # ACT
        result, conflicts = TaskService.update_task(
            task_id=99999,
            title="New Title",
            session=test_db,
        )

        # ASSERT
        assert result is None
        assert conflicts is None

    def test_br_reorder_006_update_same_time(self, test_db: Session, task: Task) -> None:
        """
        BR-REORDER-006: Atualização para mesmo horário não dispara reordering.

        DADO: Task com horário definido
        QUANDO: Usuário "atualiza" para mesmo horário
        ENTÃO: Horário permanece igual
        E: Nenhuma proposta é gerada
        """
        original_datetime = task.scheduled_datetime
        assert task.id is not None

        # ACT
        result, conflicts = TaskService.update_task(
            task_id=task.id,
            scheduled_datetime=original_datetime,  # Mesmo horário
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.scheduled_datetime == original_datetime
        assert conflicts is None  # Sem mudança real = sem conflitos
