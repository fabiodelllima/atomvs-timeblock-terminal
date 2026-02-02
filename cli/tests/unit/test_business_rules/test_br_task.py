"""Testes para Business Rules de Task.

Valida BRs:
- BR-TASK-006: Simplicidade Mantida (Design Constraint)
"""

from timeblock.models import Task

# BR-TASK-006: Simplicidade Mantida


class TestBRTask006:
    """Valida BR-TASK-006: Tasks são intencionalmente simples no MVP."""

    def test_br_task_006_no_subtasks_field(self):
        """BR-TASK-006: Task NÃO possui campo subtasks."""
        assert not hasattr(Task, "subtasks"), "Task não deve ter subtasks no MVP"

    def test_br_task_006_no_dependencies_field(self):
        """BR-TASK-006: Task NÃO possui campo dependencies."""
        assert not hasattr(Task, "dependencies"), "Task não deve ter dependencies no MVP"

    def test_br_task_006_no_priority_field(self):
        """BR-TASK-006: Task NÃO possui campo priority."""
        assert not hasattr(Task, "priority"), "Task não deve ter priority no MVP"

    def test_br_task_006_no_checklist_field(self):
        """BR-TASK-006: Task NÃO possui campo checklist."""
        assert not hasattr(Task, "checklist"), "Task não deve ter checklist no MVP"

    def test_br_task_006_has_only_expected_fields(self):
        """BR-TASK-006: Task possui apenas campos do MVP."""
        expected_fields = {
            "id",
            "title",
            "scheduled_datetime",
            "completed_datetime",
            "description",
            "color",
            "tag_id",
            "tag",
        }
        model_fields = set(Task.model_fields.keys())

        # Relationship "tag" não está em model_fields, verificar separado
        unexpected = model_fields - expected_fields
        assert not unexpected, f"Task possui campos inesperados no MVP: {unexpected}"
