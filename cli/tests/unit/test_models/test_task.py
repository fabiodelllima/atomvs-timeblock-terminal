"""Tests for Task model.

BR validada: BR-TASK-001 (Estrutura de Task)
"""

from datetime import datetime

from sqlmodel import Session

from src.timeblock.models.task import Task


def test_task_creation(session: Session) -> None:
    """Test creating a task. Validates BR-TASK-001."""
    task = Task(
        title="Doctor Appointment",
        scheduled_datetime=datetime(2025, 10, 17, 14, 0),
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.id is not None
    assert task.title == "Doctor Appointment"
    assert task.completed_datetime is None


def test_task_completion(session: Session) -> None:
    """Test completing a task. Validates BR-TASK-001."""
    task = Task(
        title="Task",
        scheduled_datetime=datetime(2025, 10, 17, 10, 0),
        completed_datetime=datetime(2025, 10, 17, 10, 30),
    )
    session.add(task)
    session.commit()

    assert task.completed_datetime is not None


def test_task_with_description(session: Session) -> None:
    """Test task with description and color. Validates BR-TASK-001."""
    task = Task(
        title="Meeting",
        scheduled_datetime=datetime(2025, 10, 17, 15, 0),
        description="Quarterly review",
        color="#FF5733",
    )
    session.add(task)
    session.commit()

    assert task.description == "Quarterly review"
    assert task.color == "#FF5733"
