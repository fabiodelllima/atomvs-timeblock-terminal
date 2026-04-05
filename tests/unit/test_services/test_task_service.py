"""Testes para TaskService.

BRs validadas:
- BR-TASK-001: Estrutura de Task
- BR-TASK-002: Completar Task
- BR-TASK-003: Deleção de Task
"""

from datetime import datetime

import pytest
from sqlalchemy.engine import Engine

from timeblock.services.task_service import TaskService


@pytest.fixture(autouse=True)
def mock_engine(monkeypatch, test_engine: Engine):
    """Mock do get_engine_context."""
    from contextlib import contextmanager

    @contextmanager
    def mock_get_engine():
        yield test_engine

    monkeypatch.setattr("timeblock.services.task_service.get_engine_context", mock_get_engine)


class TestCreateTask:
    """Testes para create_task. Validates BR-TASK-001."""

    def test_create_task_success(self) -> None:
        """Cria tarefa com sucesso."""
        task = TaskService.create_task(
            title="Dentist",
            scheduled_datetime=datetime(2025, 10, 20, 14, 0),
        )
        assert task.id is not None
        assert task.title == "Dentist"
        assert task.scheduled_datetime == datetime(2025, 10, 20, 14, 0)

    def test_create_task_with_description(self) -> None:
        """Cria tarefa com descrição."""
        task = TaskService.create_task(
            title="Meeting",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
            description="Discuss Q4 results",
        )
        assert task.description == "Discuss Q4 results"

    def test_create_task_with_color(self) -> None:
        """Cria tarefa com cor."""
        task = TaskService.create_task(
            title="Important",
            scheduled_datetime=datetime(2025, 10, 20, 15, 0),
            color="#FF0000",
        )
        assert task.color == "#FF0000"

    def test_create_task_strips_whitespace(self) -> None:
        """Remove espaços do título."""
        task = TaskService.create_task(
            title="  Task  ",
            scheduled_datetime=datetime(2025, 10, 20, 12, 0),
        )
        assert task.title == "Task"

    def test_create_task_with_empty_title(self) -> None:
        """Rejeita título vazio."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TaskService.create_task(
                title="   ",
                scheduled_datetime=datetime(2025, 10, 20, 12, 0),
            )

    def test_create_task_with_title_too_long(self) -> None:
        """Rejeita título muito longo."""
        with pytest.raises(ValueError, match="cannot exceed 200"):
            TaskService.create_task(
                title="X" * 201,
                scheduled_datetime=datetime(2025, 10, 20, 12, 0),
            )


class TestGetTask:
    """Testes para get_task."""

    def test_get_task_found(self) -> None:
        """Busca tarefa existente."""
        created = TaskService.create_task(
            title="Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )
        found = TaskService.get_task(created.id)
        assert found is not None
        assert found.id == created.id

    def test_get_task_not_found(self) -> None:
        """Retorna None se não existe."""
        assert TaskService.get_task(9999) is None


class TestListTasks:
    """Testes para list_tasks."""

    def test_list_tasks_all(self) -> None:
        """Lista todas as tarefas."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks()
        assert len(tasks) == 3

    def test_list_tasks_with_start(self) -> None:
        """Filtra por data inicial."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks(start=datetime(2025, 10, 21, 0, 0))
        assert len(tasks) == 2

    def test_list_tasks_with_end(self) -> None:
        """Filtra por data final."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks(end=datetime(2025, 10, 21, 23, 59))
        assert len(tasks) == 2

    def test_list_tasks_with_range(self) -> None:
        """Filtra por período."""
        TaskService.create_task("Task 1", datetime(2025, 10, 20, 10, 0))
        TaskService.create_task("Task 2", datetime(2025, 10, 21, 11, 0))
        TaskService.create_task("Task 3", datetime(2025, 10, 22, 12, 0))

        tasks = TaskService.list_tasks(
            start=datetime(2025, 10, 21, 0, 0),
            end=datetime(2025, 10, 21, 23, 59),
        )
        assert len(tasks) == 1
        assert tasks[0].title == "Task 2"


class TestCompleteTask:
    """Testes para complete_task. Validates BR-TASK-002."""

    def test_complete_task_success(self) -> None:
        """Completa tarefa com sucesso."""
        task = TaskService.create_task(
            title="Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )

        completed = TaskService.complete_task(task.id)
        assert completed is not None
        assert completed.completed_datetime is not None

    def test_complete_task_not_found(self) -> None:
        """Retorna None se não existe."""
        assert TaskService.complete_task(9999) is None


class TestDeleteTask:
    """Testes para delete_task. Validates BR-TASK-003."""

    def test_delete_task_success(self) -> None:
        """Remove tarefa com sucesso."""
        task = TaskService.create_task(
            title="Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )

        assert TaskService.delete_task(task.id) is True
        assert TaskService.get_task(task.id) is None

    def test_delete_task_not_found(self) -> None:
        """Retorna False se não existe."""
        assert TaskService.delete_task(9999) is False


class TestUpdateTask:
    """Testes para update_task. Validates BR-TASK-005."""

    def test_update_task_not_found(self) -> None:
        """GAP-001: update_task com ID inexistente retorna (None, None)."""
        result, _conflicts = TaskService.update_task(
            task_id=9999,
            title="Ghost",
        )
        assert result is None

    def test_update_task_empty_title(self) -> None:
        """GAP-005: update_task com título vazio levanta ValueError."""
        task = TaskService.create_task(
            title="Original",
            scheduled_datetime=datetime(2025, 11, 1, 10, 0),
        )
        with pytest.raises(ValueError, match="cannot be empty"):
            TaskService.update_task(task.id, title="   ")

    def test_update_task_title_too_long(self) -> None:
        """Error path: update_task com título > 200 chars levanta ValueError."""
        task = TaskService.create_task(
            title="Original",
            scheduled_datetime=datetime(2025, 11, 1, 10, 0),
        )
        with pytest.raises(ValueError, match="cannot exceed 200"):
            TaskService.update_task(task.id, title="X" * 201)


class TestCancelTask:
    """Testes para cancel_task. Validates BR-TASK-009."""

    def test_cancel_task_not_found(self) -> None:
        """GAP-002: cancel_task com ID inexistente retorna None."""
        assert TaskService.cancel_task(9999) is None


class TestReopenTask:
    """Testes para reopen_task. Validates BR-TASK-009."""

    def test_reopen_task_not_found(self) -> None:
        """GAP-003: reopen_task com ID inexistente retorna None."""
        assert TaskService.reopen_task(9999) is None


class TestCompleteTaskErrorPaths:
    """Error paths para complete_task. Validates BR-TASK-002."""

    def test_complete_task_already_completed(self) -> None:
        """GAP-004: complete_task em task já completada sobrescreve timestamp.

        Documenta comportamento atual: idempotente (não levanta erro).
        O segundo complete_datetime é diferente do primeiro.
        """
        task = TaskService.create_task(
            title="Task",
            scheduled_datetime=datetime(2025, 10, 20, 10, 0),
        )
        first = TaskService.complete_task(task.id)
        first_dt = first.completed_datetime

        second = TaskService.complete_task(task.id)
        assert second is not None
        assert second.completed_datetime is not None
        assert second.completed_datetime >= first_dt
