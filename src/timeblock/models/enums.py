"""Enumerações compartilhadas entre modelos."""

from enum import StrEnum


class Status(StrEnum):
    """Status principal (PENDING/DONE/NOT_DONE)."""

    PENDING = "pending"
    DONE = "done"
    NOT_DONE = "not_done"


class DoneSubstatus(StrEnum):
    """Substatus para eventos DONE."""

    FULL = "full"  # 90-110%
    OVERDONE = "overdone"  # 110-150%
    EXCESSIVE = "excessive"  # >150%
    PARTIAL = "partial"  # <90%


class NotDoneSubstatus(StrEnum):
    """Substatus para eventos NOT_DONE."""

    SKIPPED_JUSTIFIED = "skipped_justified"
    SKIPPED_UNJUSTIFIED = "skipped_unjustified"
    IGNORED = "ignored"


class SkipReason(StrEnum):
    """Categorias de justificativa para skip."""

    HEALTH = "saude"
    WORK = "trabalho"
    FAMILY = "familia"
    TRAVEL = "viagem"
    WEATHER = "clima"
    LACK_RESOURCES = "falta_recursos"
    EMERGENCY = "emergencia"
    OTHER = "outro"


class TimerStatus(StrEnum):
    """Status do timer (BR-TIMER-002).

    Estados:
        - RUNNING: Timer contando tempo
        - PAUSED: Timer pausado temporariamente
        - DONE: Timer finalizado com stop (sessão salva)
        - CANCELLED: Timer resetado (zera o timer)
    """

    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    CANCELLED = "cancelled"
