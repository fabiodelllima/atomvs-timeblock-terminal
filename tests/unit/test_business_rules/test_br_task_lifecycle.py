"""Testes unitários para BR-TASK-007 a BR-TASK-010: Task Lifecycle.

Todos os testes devem FALHAR (RED) até a implementação do modelo
e dos métodos de service correspondentes.
"""

from datetime import datetime, timedelta

import pytest
from sqlmodel import Session

from timeblock.models import Task
from timeblock.services.task_service import TaskService

# =============================================================================
# BR-TASK-007: Derivação de Status
# =============================================================================


@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
class TestBRTask007:
    """Valida BR-TASK-007: Status derivado de timestamps."""

    def test_br_task_007_pending_status_derivation(self, session: Session):
        """Task sem completed/cancelled e data futura → PENDING."""
        tomorrow = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Futura", scheduled_datetime=tomorrow, session=session)
        assert task.derived_status == "pending"

    def test_br_task_007_completed_status_derivation(self, session: Session):
        """Task com completed_datetime → COMPLETED."""
        tomorrow = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(
            title="Concluída", scheduled_datetime=tomorrow, session=session
        )
        assert task.id is not None
        TaskService.complete_task(task.id, session=session)
        session.refresh(task)
        assert task.derived_status == "completed"

    def test_br_task_007_cancelled_status_derivation(self, session: Session):
        """Task com cancelled_datetime → CANCELLED."""
        tomorrow = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(
            title="Cancelada", scheduled_datetime=tomorrow, session=session
        )
        assert task.id is not None
        TaskService.cancel_task(task.id, session=session)
        session.refresh(task)
        assert task.derived_status == "cancelled"

    def test_br_task_007_overdue_status_derivation(self, session: Session):
        """Task pendente com data passada → OVERDUE."""
        yesterday = datetime.now() - timedelta(days=1)
        task = TaskService.create_task(
            title="Atrasada", scheduled_datetime=yesterday, session=session
        )
        assert task.derived_status == "overdue"

    def test_br_task_007_cancelled_overrides_completed(self, session: Session):
        """Cancelamento prevalece sobre conclusão (precedência fixa)."""
        tomorrow = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(
            title="Ambígua", scheduled_datetime=tomorrow, session=session
        )
        assert task.id is not None
        TaskService.complete_task(task.id, session=session)
        TaskService.cancel_task(task.id, session=session)
        session.refresh(task)
        assert task.derived_status == "cancelled"


# =============================================================================
# BR-TASK-008: Rastreamento de Adiamento
# =============================================================================


@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
class TestBRTask008:
    """Valida BR-TASK-008: Rastreamento de adiamento."""

    def test_br_task_008_original_datetime_set_on_creation(self, session: Session):
        """original_scheduled_datetime == scheduled_datetime na criação."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Nova", scheduled_datetime=dt, session=session)
        assert task.original_scheduled_datetime == task.scheduled_datetime

    def test_br_task_008_original_datetime_immutable_on_update(self, session: Session):
        """original_scheduled_datetime não muda ao atualizar scheduled."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Atualizada", scheduled_datetime=dt, session=session)
        original = task.original_scheduled_datetime
        assert task.id is not None
        new_dt = dt + timedelta(days=3)
        TaskService.update_task(task.id, scheduled_datetime=new_dt, session=session)
        session.refresh(task)
        assert task.original_scheduled_datetime == original

    def test_br_task_008_postponement_count_increments_on_later_date(self, session: Session):
        """Reagendar para data posterior incrementa postponement_count."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Adiada", scheduled_datetime=dt, session=session)
        assert task.id is not None
        new_dt = dt + timedelta(days=2)
        TaskService.update_task(task.id, scheduled_datetime=new_dt, session=session)
        session.refresh(task)
        assert task.postponement_count == 1

    def test_br_task_008_postponement_count_unchanged_on_earlier_date(self, session: Session):
        """Reagendar para data anterior não incrementa."""
        dt = datetime.now() + timedelta(days=5)
        task = TaskService.create_task(title="Antecipada", scheduled_datetime=dt, session=session)
        assert task.id is not None
        new_dt = dt - timedelta(days=2)
        TaskService.update_task(task.id, scheduled_datetime=new_dt, session=session)
        session.refresh(task)
        assert task.postponement_count == 0

    def test_br_task_008_postponement_count_unchanged_on_same_date(self, session: Session):
        """Reagendar para mesma data não incrementa."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Mesma data", scheduled_datetime=dt, session=session)
        assert task.id is not None
        TaskService.update_task(task.id, scheduled_datetime=dt, session=session)
        session.refresh(task)
        assert task.postponement_count == 0

    def test_br_task_008_days_postponed_calculation(self, session: Session):
        """Delta scheduled - original fornece dias adiados."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Delta", scheduled_datetime=dt, session=session)
        assert task.id is not None
        new_dt = dt + timedelta(days=7)
        TaskService.update_task(task.id, scheduled_datetime=new_dt, session=session)
        session.refresh(task)
        days = (task.scheduled_datetime - task.original_scheduled_datetime).days
        assert days == 7


# =============================================================================
# BR-TASK-009: Cancelamento Soft Delete
# =============================================================================


@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
class TestBRTask009:
    """Valida BR-TASK-009: Cancelamento como soft delete."""

    def test_br_task_009_cancel_sets_datetime(self, session: Session):
        """cancel_task seta cancelled_datetime."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Cancelar", scheduled_datetime=dt, session=session)
        assert task.id is not None
        TaskService.cancel_task(task.id, session=session)
        session.refresh(task)
        assert task.cancelled_datetime is not None

    def test_br_task_009_cancel_preserves_record(self, session: Session):
        """Soft delete mantém registro no banco."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Preservada", scheduled_datetime=dt, session=session)
        assert task.id is not None
        task_id = task.id
        TaskService.cancel_task(task_id, session=session)
        db_task = session.get(Task, task_id)
        assert db_task is not None

    def test_br_task_009_cancelled_excluded_from_pending(self, session: Session):
        """Task cancelada não aparece em list_pending_tasks."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Excluída", scheduled_datetime=dt, session=session)
        assert task.id is not None
        TaskService.cancel_task(task.id, session=session)
        pending = TaskService.list_pending_tasks(session=session)
        assert all(t.id != task.id for t in pending)

    def test_br_task_009_cancelled_included_in_all(self, session: Session):
        """Task cancelada aparece em list_tasks."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Visível", scheduled_datetime=dt, session=session)
        assert task.id is not None
        TaskService.cancel_task(task.id, session=session)
        all_tasks = TaskService.list_tasks(session=session)
        assert any(t.id == task.id for t in all_tasks)

    def test_br_task_009_reopen_clears_cancelled_datetime(self, session: Session):
        """reopen_task limpa cancelled_datetime."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Reaberta", scheduled_datetime=dt, session=session)
        assert task.id is not None
        TaskService.cancel_task(task.id, session=session)
        TaskService.reopen_task(task.id, session=session)
        session.refresh(task)
        assert task.cancelled_datetime is None


# =============================================================================
# BR-TASK-010: Métricas de Lifecycle
# =============================================================================


@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
@pytest.mark.xfail(reason="RED — awaiting Task lifecycle implementation")
class TestBRTask010:
    """Valida BR-TASK-010: Métricas calculadas de lifecycle."""

    def test_br_task_010_time_to_completion_calculation(self, session: Session):
        """time_to_completion = completed - original_scheduled."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Medida", scheduled_datetime=dt, session=session)
        assert task.id is not None
        TaskService.complete_task(task.id, session=session)
        session.refresh(task)
        assert task.completed_datetime is not None
        delta = task.completed_datetime - task.original_scheduled_datetime
        assert delta.total_seconds() != 0

    def test_br_task_010_on_time_detection(self, session: Session):
        """Task concluída antes ou no dia agendado é on_time."""
        tomorrow = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(
            title="Pontual", scheduled_datetime=tomorrow, session=session
        )
        assert task.id is not None
        TaskService.complete_task(task.id, session=session)
        session.refresh(task)
        assert task.completed_datetime is not None
        assert task.completed_datetime.date() <= task.original_scheduled_datetime.date()

    def test_br_task_010_days_late_calculation(self, session: Session):
        """Task concluída após a data original tem days_late > 0."""
        yesterday = datetime.now() - timedelta(days=2)
        task = TaskService.create_task(
            title="Atrasada", scheduled_datetime=yesterday, session=session
        )
        assert task.id is not None
        TaskService.complete_task(task.id, session=session)
        session.refresh(task)
        assert task.completed_datetime is not None
        days_late = max(
            0,
            (task.completed_datetime.date() - task.original_scheduled_datetime.date()).days,
        )
        assert days_late > 0

    def test_br_task_010_completion_rate(self, session: Session):
        """Taxa de conclusão = completed / total."""
        base = datetime.now() + timedelta(days=1)
        for i in range(4):
            TaskService.create_task(
                title=f"T{i}",
                scheduled_datetime=base + timedelta(hours=i),
                session=session,
            )
        all_tasks = TaskService.list_tasks(session=session)
        for t in all_tasks[:2]:
            assert t.id is not None
            TaskService.complete_task(t.id, session=session)
        all_tasks = TaskService.list_tasks(session=session)
        completed = sum(1 for t in all_tasks if t.completed_datetime is not None)
        rate = completed / len(all_tasks)
        # Valida campo original_scheduled_datetime para garantir RED
        assert all_tasks[0].original_scheduled_datetime is not None
        assert rate == pytest.approx(0.5)

    def test_br_task_010_cancellation_rate(self, session: Session):
        """Taxa de cancelamento = cancelled / total."""
        base = datetime.now() + timedelta(days=1)
        for i in range(4):
            TaskService.create_task(
                title=f"C{i}",
                scheduled_datetime=base + timedelta(hours=i),
                session=session,
            )
        all_tasks = TaskService.list_tasks(session=session)
        assert all_tasks[0].id is not None
        TaskService.cancel_task(all_tasks[0].id, session=session)
        all_tasks = TaskService.list_tasks(session=session)
        cancelled = sum(1 for t in all_tasks if getattr(t, "cancelled_datetime", None) is not None)
        rate = cancelled / len(all_tasks)
        assert rate == pytest.approx(0.25)

    def test_br_task_010_postponement_aggregates(self, session: Session):
        """Métricas agregadas de adiamento."""
        base = datetime.now() + timedelta(days=1)
        t1 = TaskService.create_task(title="P1", scheduled_datetime=base, session=session)
        t2 = TaskService.create_task(
            title="P2",
            scheduled_datetime=base + timedelta(hours=1),
            session=session,
        )
        assert t1.id is not None
        # t1 adiada 2x, t2 nunca adiada
        TaskService.update_task(t1.id, scheduled_datetime=base + timedelta(days=3), session=session)
        session.refresh(t1)
        TaskService.update_task(t1.id, scheduled_datetime=base + timedelta(days=5), session=session)
        session.refresh(t1)
        assert t1.postponement_count == 2
        assert t2.postponement_count == 0

    def test_br_task_010_migration_fallback_original_datetime(self, session: Session):
        """Tasks sem original_scheduled_datetime usam scheduled como fallback."""
        dt = datetime.now() + timedelta(days=1)
        task = TaskService.create_task(title="Fallback", scheduled_datetime=dt, session=session)
        # Na criação, original == scheduled (simula task pré-migração)
        assert task.original_scheduled_datetime == task.scheduled_datetime
