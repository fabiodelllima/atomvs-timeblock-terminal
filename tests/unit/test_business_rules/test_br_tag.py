"""Testes para Business Rules de Tag.

Valida BRs:
- BR-TAG-001: Estrutura de Tag
- BR-TAG-002: Associação com Eventos (Habits/Tasks)
"""

import pytest
from sqlmodel import Session, select

from timeblock.models import Habit, Recurrence, Routine, Tag, Task
from timeblock.services.tag_service import TagService

# BR-TAG-001: Estrutura de Tag


class TestBRTag001:
    """Valida BR-TAG-001: Estrutura de Tag."""

    def test_br_tag_001_color_has_default(self, session: Session):
        """BR-TAG-001: color tem default cinza (#808080)."""
        tag = Tag(name="Trabalho")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        assert tag.color == "#808080"

    def test_br_tag_001_color_is_required(self, session: Session):
        """BR-TAG-001: color é campo obrigatório (NOT NULL via default)."""
        tag = Tag(name="Teste")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        # Mesmo sem informar, color existe via default
        assert tag.color is not None

    def test_br_tag_001_name_unique(self, session: Session):
        """BR-TAG-001: name deve ser único."""
        service = TagService(session)
        service.create_tag("Saúde")
        session.commit()

        with pytest.raises(ValueError, match="já existe"):
            service.create_tag("Saúde")

    def test_br_tag_001_name_max_length(self, session: Session):
        """BR-TAG-001: name aceita até 50 caracteres."""
        service = TagService(session)

        # Dentro do limite
        tag = service.create_tag("A" * 50)
        session.commit()
        assert len(tag.name) == 50

        # Acima do limite
        with pytest.raises(ValueError, match="50 caracteres"):
            service.create_tag("B" * 51)

    def test_br_tag_001_name_min_length(self, session: Session):
        """BR-TAG-001: name requer pelo menos 1 caractere."""
        service = TagService(session)

        with pytest.raises(ValueError, match="vazio"):
            service.create_tag("")

    def test_br_tag_001_name_whitespace_only(self, session: Session):
        """BR-TAG-001: name apenas com espaços é rejeitado."""
        service = TagService(session)

        with pytest.raises(ValueError, match="vazio"):
            service.create_tag("   ")

    def test_br_tag_001_custom_color(self, session: Session):
        """BR-TAG-001: cor customizada é aceita."""
        service = TagService(session)
        tag = service.create_tag("Urgente", color="#ff0000")
        session.commit()

        assert tag.color == "#ff0000"

    def test_br_tag_001_default_color_amarelo(self, session: Session):
        """BR-TAG-001: cor padrão do service é amarelo (#fbd75b)."""
        service = TagService(session)
        tag = service.create_tag("Default")
        session.commit()

        assert tag.color == "#fbd75b"

    def test_br_tag_001_id_autoincrement(self, session: Session):
        """BR-TAG-001: id é gerado automaticamente."""
        service = TagService(session)
        tag = service.create_tag("Auto")
        session.commit()

        assert tag.id is not None
        assert tag.id > 0


# BR-TAG-002: Associação com Eventos


class TestBRTag002:
    """Valida BR-TAG-002: Associação Tag com Habits e Tasks."""

    def _create_routine(self, session: Session) -> Routine:
        """Helper: cria rotina para vincular habits."""
        routine = Routine(name="Rotina Teste", is_active=True)
        session.add(routine)
        session.commit()
        session.refresh(routine)
        return routine

    def test_br_tag_002_habit_has_optional_tag(self, session: Session):
        """BR-TAG-002: Habit pode ter 0 ou 1 tag (tag_id nullable)."""
        routine = self._create_routine(session)
        from datetime import time

        habit = Habit(
            title="Sem tag",
            routine_id=routine.id,
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.WEEKDAYS,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        assert habit.tag_id is None

    def test_br_tag_002_habit_with_tag(self, session: Session):
        """BR-TAG-002: Habit pode receber uma tag."""
        routine = self._create_routine(session)
        tag = Tag(name="Saúde")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        from datetime import time

        habit = Habit(
            title="Com tag",
            routine_id=routine.id,
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.WEEKDAYS,
            tag_id=tag.id,
        )
        session.add(habit)
        session.commit()
        session.refresh(habit)

        assert habit.tag_id == tag.id

    def test_br_tag_002_task_has_optional_tag(self, session: Session):
        """BR-TAG-002: Task pode ter 0 ou 1 tag (tag_id nullable)."""
        from datetime import datetime

        task = Task(
            title="Sem tag",
            scheduled_datetime=datetime(2026, 2, 1, 9, 0),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.tag_id is None

    def test_br_tag_002_task_with_tag(self, session: Session):
        """BR-TAG-002: Task pode receber uma tag."""
        from datetime import datetime

        tag = Tag(name="Projeto")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        task = Task(
            title="Com tag",
            scheduled_datetime=datetime(2026, 2, 1, 9, 0),
            tag_id=tag.id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.tag_id == tag.id

    def test_br_tag_002_delete_tag_nullifies_habit(self, session: Session):
        """BR-TAG-002: Deletar tag seta tag_id = NULL nos habits."""
        routine = self._create_routine(session)
        tag = Tag(name="Temporária")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        from datetime import time

        habit = Habit(
            title="Vinculado",
            routine_id=routine.id,
            scheduled_start=time(9, 0),
            scheduled_end=time(10, 0),
            recurrence=Recurrence.WEEKDAYS,
            tag_id=tag.id,
        )
        session.add(habit)
        session.commit()

        # Act: deletar tag
        session.delete(tag)
        session.commit()

        # Assert: habit persiste com tag_id NULL
        session.refresh(habit)
        assert habit.tag_id is None

    def test_br_tag_002_delete_tag_nullifies_task(self, session: Session):
        """BR-TAG-002: Deletar tag seta tag_id = NULL nas tasks."""
        from datetime import datetime

        tag = Tag(name="Temporária")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        task = Task(
            title="Vinculado",
            scheduled_datetime=datetime(2026, 2, 1, 9, 0),
            tag_id=tag.id,
        )
        session.add(task)
        session.commit()

        # Act: deletar tag
        session.delete(tag)
        session.commit()

        # Assert: task persiste com tag_id NULL
        session.refresh(task)
        assert task.tag_id is None

    def test_br_tag_002_multiple_habits_one_tag(self, session: Session):
        """BR-TAG-002: Uma tag pode ser usada por múltiplos habits."""
        routine = self._create_routine(session)
        tag = Tag(name="Compartilhada")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        from datetime import time

        for i in range(3):
            habit = Habit(
                title=f"Habit {i}",
                routine_id=routine.id,
                scheduled_start=time(9 + i, 0),
                scheduled_end=time(10 + i, 0),
                recurrence=Recurrence.WEEKDAYS,
                tag_id=tag.id,
            )
            session.add(habit)
        session.commit()

        habits_with_tag = session.exec(select(Habit).where(Habit.tag_id == tag.id)).all()
        assert len(habits_with_tag) == 3
