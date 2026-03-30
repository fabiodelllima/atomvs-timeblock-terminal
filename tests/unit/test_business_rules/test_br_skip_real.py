"""Testes para Business Rules de Skip com modelo real.

Valida BRs usando HabitInstance real e HabitInstanceService:
- BR-SKIP-001: Categorização de Skip com Enum (8 categorias)
- BR-SKIP-002: Campos skip_reason e skip_note
- BR-SKIP-003: Prazo para justificar (24h)
- BR-SKIP-004: Integração via Service (skip_habit_instance)

Complementa test_br_skip.py (mocks v2.0) com testes contra ORM real.
"""

from datetime import date, datetime, time, timedelta

import pytest
from sqlmodel import Session

from timeblock.models import Habit, Recurrence, Routine
from timeblock.models.enums import (
    DoneSubstatus,
    NotDoneSubstatus,
    SkipReason,
    Status,
)
from timeblock.models.habit_instance import HabitInstance
from timeblock.services.habit_instance_service import HabitInstanceService


# =========================================================================
# Helpers
# =========================================================================


def _create_routine_and_instance(session: Session) -> HabitInstance:
    """Cria rotina + hábito + instância PENDING para testes de skip."""
    routine = Routine(name="Rotina Skip", is_active=True)
    session.add(routine)
    session.commit()
    session.refresh(routine)

    habit = Habit(
        title="Hábito Skip",
        routine_id=routine.id,
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        recurrence=Recurrence.EVERYDAY,
    )
    session.add(habit)
    session.commit()
    session.refresh(habit)

    instance = HabitInstance(
        habit_id=habit.id,
        date=date.today(),
        scheduled_start=time(9, 0),
        scheduled_end=time(10, 0),
        status=Status.PENDING,
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance


# =========================================================================
# BR-SKIP-001: Categorização de Skip com Enum
# =========================================================================


class TestBRSkip001Real:
    """Valida BR-SKIP-001 com SkipReason real do models/enums.py."""

    def test_br_skip_001_enum_has_8_categories(self):
        """BR-SKIP-001: SkipReason tem exatamente 8 categorias."""
        assert len(SkipReason) == 8

    def test_br_skip_001_values_in_portuguese(self):
        """BR-SKIP-001: Valores do enum em português lowercase."""
        expected = {
            "saude",
            "trabalho",
            "familia",
            "viagem",
            "clima",
            "falta_recursos",
            "emergencia",
            "outro",
        }
        actual = {r.value for r in SkipReason}
        assert actual == expected

    def test_br_skip_001_all_categories_accessible(self):
        """BR-SKIP-001: Todas as categorias são acessíveis por nome."""
        assert SkipReason.HEALTH.value == "saude"
        assert SkipReason.WORK.value == "trabalho"
        assert SkipReason.FAMILY.value == "familia"
        assert SkipReason.TRAVEL.value == "viagem"
        assert SkipReason.WEATHER.value == "clima"
        assert SkipReason.LACK_RESOURCES.value == "falta_recursos"
        assert SkipReason.EMERGENCY.value == "emergencia"
        assert SkipReason.OTHER.value == "outro"


# =========================================================================
# BR-SKIP-002: Campos skip_reason e skip_note
# =========================================================================


class TestBRSkip002Real:
    """Valida BR-SKIP-002 com HabitInstance real e service."""

    def test_br_skip_002_skip_sets_all_fields(self, session: Session):
        """BR-SKIP-002: skip_habit_instance preenche status, substatus, reason."""
        instance = _create_routine_and_instance(session)

        result = HabitInstanceService.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.HEALTH,
            skip_note="Dor de cabeça",
            session=session,
        )

        assert result.status == Status.NOT_DONE
        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED
        assert result.skip_reason == SkipReason.HEALTH
        assert result.skip_note == "Dor de cabeça"

    def test_br_skip_002_skip_clears_done_fields(self, session: Session):
        """BR-SKIP-002: skip limpa done_substatus e completion_percentage."""
        instance = _create_routine_and_instance(session)

        result = HabitInstanceService.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.WORK,
            session=session,
        )

        assert result.done_substatus is None
        assert result.completion_percentage is None

    def test_br_skip_002_skip_note_optional(self, session: Session):
        """BR-SKIP-002: skip_note é opcional (pode ser None)."""
        instance = _create_routine_and_instance(session)

        result = HabitInstanceService.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.EMERGENCY,
            skip_note=None,
            session=session,
        )

        assert result.skip_reason == SkipReason.EMERGENCY
        assert result.skip_note is None

    def test_br_skip_002_skip_note_with_text(self, session: Session):
        """BR-SKIP-002: skip_note aceita texto quando fornecido."""
        instance = _create_routine_and_instance(session)

        result = HabitInstanceService.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.FAMILY,
            skip_note="Compromisso familiar urgente",
            session=session,
        )

        assert result.skip_note == "Compromisso familiar urgente"

    def test_br_skip_002_skip_reason_required_for_justified(self, session: Session):
        """BR-SKIP-002: validate_status_consistency rejeita JUSTIFIED sem reason."""
        instance = _create_routine_and_instance(session)

        # Tentar setar manualmente sem skip_reason viola consistência
        instance.status = Status.NOT_DONE
        instance.not_done_substatus = NotDoneSubstatus.SKIPPED_JUSTIFIED
        instance.skip_reason = None

        with pytest.raises(ValueError, match="skip_reason obrigatório"):
            instance.validate_status_consistency()

    def test_br_skip_002_skip_reason_forbidden_without_justified(self, session: Session):
        """BR-SKIP-002: skip_reason só permitido com SKIPPED_JUSTIFIED."""
        instance = _create_routine_and_instance(session)

        instance.status = Status.NOT_DONE
        instance.not_done_substatus = NotDoneSubstatus.SKIPPED_UNJUSTIFIED
        instance.skip_reason = SkipReason.HEALTH

        with pytest.raises(ValueError, match="skip_reason só permitido"):
            instance.validate_status_consistency()


# =========================================================================
# BR-SKIP-003: Prazo para Justificar Skip (24h)
# =========================================================================


class TestBRSkip003Real:
    """Valida BR-SKIP-003: prazo de 24h para justificar skip."""

    def test_br_skip_003_within_deadline_can_justify(self, session: Session):
        """BR-SKIP-003: dentro de 24h, skip é aceito normalmente."""
        instance = _create_routine_and_instance(session)

        # Skip funciona em instância recente (sempre dentro do prazo)
        result = HabitInstanceService.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.WEATHER,
            session=session,
        )

        assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED

    def test_br_skip_003_deadline_calculation(self):
        """BR-SKIP-003: deadline é created_at + 24h."""
        created = datetime(2026, 3, 15, 8, 0)
        deadline = created + timedelta(hours=24)

        assert deadline == datetime(2026, 3, 16, 8, 0)
        assert datetime(2026, 3, 15, 20, 0) < deadline  # 12h depois: dentro
        assert datetime(2026, 3, 16, 9, 0) > deadline  # 25h depois: fora


# =========================================================================
# BR-SKIP-004: Integração Service — Skip + Undo
# =========================================================================


class TestBRSkip004Real:
    """Valida BR-SKIP-004: fluxo completo skip → undo via modelo real."""

    def test_br_skip_004_each_reason_creates_justified(self, session: Session):
        """BR-SKIP-004: cada SkipReason cria SKIPPED_JUSTIFIED."""
        for reason in SkipReason:
            instance = _create_routine_and_instance(session)

            result = HabitInstanceService.skip_habit_instance(
                habit_instance_id=instance.id,
                skip_reason=reason,
                session=session,
            )

            assert result.not_done_substatus == NotDoneSubstatus.SKIPPED_JUSTIFIED, (
                f"Reason {reason.value} deve criar JUSTIFIED"
            )
            assert result.skip_reason == reason

    def test_br_skip_004_undo_clears_all_skip_fields(self, session: Session):
        """BR-SKIP-004: reset_to_pending limpa todos os campos de skip."""
        instance = _create_routine_and_instance(session)

        # Skip
        HabitInstanceService.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.HEALTH,
            skip_note="Nota para limpar",
            session=session,
        )

        # Undo
        session.refresh(instance)
        instance.reset_to_pending()
        session.add(instance)
        session.commit()
        session.refresh(instance)

        assert instance.status == Status.PENDING
        assert instance.not_done_substatus is None
        assert instance.skip_reason is None
        assert instance.skip_note is None
        assert instance.done_substatus is None
        assert instance.completion_percentage is None

    def test_br_skip_004_skip_after_done_overrides(self, session: Session):
        """BR-SKIP-004: skip após done sobrescreve status corretamente."""
        instance = _create_routine_and_instance(session)

        # Primeiro: mark_completed
        HabitInstanceService.mark_completed(
            habit_instance_id=instance.id,
            done_substatus=DoneSubstatus.FULL,
            session=session,
        )
        session.refresh(instance)
        assert instance.status == Status.DONE

        # Undo
        instance.reset_to_pending()
        session.add(instance)
        session.commit()

        # Agora: skip
        result = HabitInstanceService.skip_habit_instance(
            habit_instance_id=instance.id,
            skip_reason=SkipReason.WORK,
            session=session,
        )

        assert result.status == Status.NOT_DONE
        assert result.skip_reason == SkipReason.WORK
        assert result.done_substatus is None
