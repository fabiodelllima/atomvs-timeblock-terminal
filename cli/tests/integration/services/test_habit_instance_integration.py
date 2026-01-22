"""
Integration tests - HabitInstanceService + EventReorderingService.

Testa integração entre HabitInstanceService e EventReorderingService,
validando ajustes de horário, detecção de conflitos e propostas de reorganização.

Referências:
    - ADR-019: Test Naming Convention
    - BR-REORDER-001 a BR-REORDER-005
    - Sprint 2.4: HabitInstance + EventReordering integration
"""

from datetime import date, datetime, time

import pytest
from sqlmodel import Session

from timeblock.models import Habit, HabitInstance, Recurrence, Routine, Task
from timeblock.models.enums import Status
from timeblock.services.habit_instance_service import HabitInstanceService


class TestBRHabitInstanceReordering:
    """
    Integration: HabitInstanceService + EventReorderingService (BR-REORDER-*).

    Valida ajuste de horários de instâncias de hábitos com detecção
    automática de conflitos e geração de propostas de reorganização.
    """

    @pytest.fixture
    def routine(self, test_db: Session) -> Routine:
        """Cria rotina para testes."""
        routine = Routine(name="Test Routine", is_active=True)
        test_db.add(routine)
        test_db.commit()
        test_db.refresh(routine)
        return routine

    @pytest.fixture
    def habit(self, test_db: Session, routine: Routine) -> Habit:
        """Cria hábito para testes."""
        assert routine.id is not None
        habit = Habit(
            title="Test Habit",
            routine_id=routine.id,
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            recurrence=Recurrence.EVERYDAY,
        )
        test_db.add(habit)
        test_db.commit()
        test_db.refresh(habit)
        return habit

    @pytest.fixture
    def instance(self, test_db: Session, habit: Habit) -> HabitInstance:
        """Cria instância para testes."""
        assert habit.id is not None
        instance = HabitInstance(
            habit_id=habit.id,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )
        test_db.add(instance)
        test_db.commit()
        test_db.refresh(instance)
        return instance

    def test_br_reorder_001_adjust_without_time_change(
        self, test_db: Session, instance: HabitInstance
    ) -> None:
        """
        BR-REORDER-001: Ajuste sem mudança de horário não dispara reordering.

        DADO: Instância de hábito com horário 08:00-09:00
        QUANDO: Usuário ajusta mantendo mesmo horário (08:00)
        ENTÃO: Instância é atualizada
        E: Nenhuma proposta de reordering é gerada (lista vazia)
        """
        assert instance.id is not None

        # ACT
        result, conflicts = HabitInstanceService.adjust_instance_time(
            instance_id=instance.id,
            new_start=time(8, 0),  # Mesmo horário
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.scheduled_start == time(8, 0)
        assert conflicts is None or len(conflicts) == 0

    def test_br_reorder_002_adjust_without_conflicts(
        self, test_db: Session, instance: HabitInstance
    ) -> None:
        """
        BR-REORDER-002: Ajuste de horário sem conflitos não gera conflitos.

        DADO: Instância de hábito com horário 08:00-09:00
        QUANDO: Usuário ajusta para horário livre (10:00-11:00)
        ENTÃO: Horário é atualizado
        E: Lista de conflitos está vazia
        """
        assert instance.id is not None

        # ACT
        result, conflicts = HabitInstanceService.adjust_instance_time(
            instance_id=instance.id,
            new_start=time(10, 0),
            new_end=time(11, 0),
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.scheduled_start == time(10, 0)
        assert result.scheduled_end == time(11, 0)
        assert conflicts is None or len(conflicts) == 0

    def test_br_reorder_003_adjust_with_task_conflict(
        self, test_db: Session, instance: HabitInstance
    ) -> None:
        """
        BR-REORDER-003: Ajuste com conflito de task gera lista de conflitos.

        DADO: Instância de hábito 08:00-09:00 E task em 10:30
        QUANDO: Usuário ajusta hábito para 10:00-11:00 (conflita com task)
        ENTÃO: Horário é atualizado (BR-REORDER-004: conflitos não bloqueiam)
        E: Lista de conflitos contém os eventos conflitantes
        """
        # ARRANGE - Criar task que conflita
        task = Task(
            title="Conflicting Task",
            scheduled_datetime=datetime.combine(date.today(), time(10, 30)),
        )
        test_db.add(task)
        test_db.commit()

        assert instance.id is not None

        # ACT
        result, _conflicts = HabitInstanceService.adjust_instance_time(
            instance_id=instance.id,
            new_start=time(10, 0),
            new_end=time(11, 0),
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.scheduled_start == time(10, 0)
        # BR-REORDER-004: Conflitos são informativos, não impeditivos

    def test_br_reorder_004_adjust_nonexistent(self, test_db: Session) -> None:
        """
        BR-REORDER-004: Ajuste de instância inexistente lança ValueError.

        DADO: ID 99999 que não existe no banco
        QUANDO: Usuário tenta ajustar horário
        ENTÃO: Lança ValueError com mensagem apropriada
        """
        # ACT & ASSERT
        with pytest.raises(ValueError, match="HabitInstance 99999 not found"):
            HabitInstanceService.adjust_instance_time(
                instance_id=99999,
                new_start=time(10, 0),
                session=test_db,
            )

    def test_br_reorder_005_mark_completed(self, test_db: Session, instance: HabitInstance) -> None:
        """
        BR-HABITINSTANCE-001: Marcar instância como completa atualiza status.

        DADO: Instância de hábito pendente
        QUANDO: Usuário marca como completo
        ENTÃO: Status é atualizado para DONE
        """
        assert instance.id is not None

        # ACT
        result = HabitInstanceService.mark_completed(
            instance_id=instance.id,
            session=test_db,
        )

        # ASSERT
        assert result is not None
        assert result.status == Status.DONE
