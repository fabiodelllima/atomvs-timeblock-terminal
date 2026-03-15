"""Testes unitários para HabitInstance.reset_to_pending() (BR-HABITINSTANCE-007).

Valida que undo centralizado limpa todos os campos de substatus,
skip e completion, preservando identidade da instância.

Referências:
    - BR-HABITINSTANCE-007: Undo com preservação de TimeLog
    - DT-035: Handler undo precisa limpar todos os campos
    - ADR-038 D1: Undo é transição válida
"""

from datetime import date, time

from timeblock.models.enums import (
    DoneSubstatus,
    NotDoneSubstatus,
    SkipReason,
    Status,
)
from timeblock.models.habit_instance import HabitInstance


class TestBRHabitinstance007ResetFromDone:
    """Reset de instância DONE limpa todos os campos de completion."""

    def test_br_habitinstance_007_reset_from_done_clears_all(self) -> None:
        """DADO instância DONE com substatus e completion,
        QUANDO reset_to_pending() é chamado,
        ENTÃO status=PENDING e todos os campos de substatus são None,
        E validate_status_consistency() passa sem erro.
        """
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.DONE,
            done_substatus=DoneSubstatus.FULL,
            completion_percentage=92,
        )

        instance.reset_to_pending()

        assert instance.status == Status.PENDING
        assert instance.done_substatus is None
        assert instance.not_done_substatus is None
        assert instance.skip_reason is None
        assert instance.skip_note is None
        assert instance.completion_percentage is None
        # Não deve levantar erro
        instance.validate_status_consistency()


class TestBRHabitinstance007ResetFromSkipped:
    """Reset de instância SKIPPED limpa skip_reason e skip_note."""

    def test_br_habitinstance_007_reset_from_skipped_clears_all(self) -> None:
        """DADO instância NOT_DONE/SKIPPED_JUSTIFIED com reason e note,
        QUANDO reset_to_pending() é chamado,
        ENTÃO todos os campos de skip são None,
        E validate_status_consistency() passa sem erro.
        """
        instance = HabitInstance(
            habit_id=1,
            date=date.today(),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.NOT_DONE,
            not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            skip_reason=SkipReason.HEALTH,
            skip_note="Gripe forte",
        )

        instance.reset_to_pending()

        assert instance.status == Status.PENDING
        assert instance.done_substatus is None
        assert instance.not_done_substatus is None
        assert instance.skip_reason is None
        assert instance.skip_note is None
        assert instance.completion_percentage is None
        instance.validate_status_consistency()


class TestBRHabitinstance007ResetPreservesIdentity:
    """Reset preserva campos de identidade da instância."""

    def test_br_habitinstance_007_reset_preserves_identity(self) -> None:
        """DADO instância DONE com campos de identidade preenchidos,
        QUANDO reset_to_pending() é chamado,
        ENTÃO habit_id, date, scheduled_start e scheduled_end permanecem inalterados.
        """
        target_date = date(2026, 3, 15)
        instance = HabitInstance(
            habit_id=42,
            date=target_date,
            scheduled_start=time(7, 30),
            scheduled_end=time(8, 30),
            status=Status.DONE,
            done_substatus=DoneSubstatus.PARTIAL,
            completion_percentage=75,
        )

        instance.reset_to_pending()

        assert instance.habit_id == 42
        assert instance.date == target_date
        assert instance.scheduled_start == time(7, 30)
        assert instance.scheduled_end == time(8, 30)
