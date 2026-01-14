"""Teste para propriedade is_overdue de HabitInstance.

BR validada: BR-HABITINSTANCE-004 (Timeout Automático)
"""

from datetime import date, time

from freezegun import freeze_time

from src.timeblock.models import HabitInstance, Status


class TestHabitInstanceOverdue:
    """
    REGRA DE NEGÓCIO BR-HABITINSTANCE-004: Propriedade is_overdue

    A propriedade is_overdue deve retornar True quando:
    1. Status é PENDING
    2. Hora atual > scheduled_start

    Deve retornar False para qualquer outro status.
    """

    def test_overdue_when_planned_and_past_time(self) -> None:
        """
        CENÁRIO: HabitInstance planejado com horário passado
        DADO: Uma instância com status PENDING para às 8h
        QUANDO: São 9h do mesmo dia
        ENTÃO: is_overdue deve ser True
        """
        instance = HabitInstance(
            id=1,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.PENDING,
        )

        with freeze_time("2025-10-25 09:00:00"):
            result = instance.is_overdue

        assert result is True, "Instância PENDING após horário deve ser overdue"

    def test_not_overdue_when_planned_and_future_time(self) -> None:
        """
        CENÁRIO: HabitInstance planejado com horário futuro
        DADO: Uma instância com status PENDING para às 14h
        QUANDO: São 9h do mesmo dia
        ENTÃO: is_overdue deve ser False
        """
        instance = HabitInstance(
            id=2,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(14, 0),
            scheduled_end=time(15, 0),
            status=Status.PENDING,
        )

        with freeze_time("2025-10-25 09:00:00"):
            result = instance.is_overdue

        assert result is False, "Instância PENDING no futuro não é overdue"

    def test_not_overdue_when_completed(self) -> None:
        """
        CENÁRIO: HabitInstance completado
        DADO: Uma instância com status DONE
        QUANDO: Qualquer horário
        ENTÃO: is_overdue deve ser False
        """
        instance = HabitInstance(
            id=4,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.DONE,
        )

        with freeze_time("2025-10-25 20:00:00"):
            result = instance.is_overdue

        assert result is False, "DONE nunca é overdue"

    def test_not_overdue_when_skipped(self) -> None:
        """
        CENÁRIO: HabitInstance pulado
        DADO: Uma instância com status NOT_DONE
        QUANDO: Qualquer horário
        ENTÃO: is_overdue deve ser False
        """
        instance = HabitInstance(
            id=5,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(8, 0),
            scheduled_end=time(9, 0),
            status=Status.NOT_DONE,
        )

        with freeze_time("2025-10-25 20:00:00"):
            result = instance.is_overdue

        assert result is False, "NOT_DONE nunca é overdue"

    def test_overdue_one_minute_after(self) -> None:
        """
        CENÁRIO: Um minuto após o horário
        DADO: Uma instância PENDING para às 14:00
        QUANDO: São 14:01
        ENTÃO: is_overdue deve ser True
        """
        instance = HabitInstance(
            id=6,
            habit_id=1,
            date=date(2025, 10, 25),
            scheduled_start=time(14, 0),
            scheduled_end=time(15, 0),
            status=Status.PENDING,
        )

        with freeze_time("2025-10-25 14:01:00"):
            result = instance.is_overdue

        assert result is True, "1 minuto após já é overdue"
