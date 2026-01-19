"""Database migrations for v2.0.

Funções de migração de schema do banco de dados.

Referências:
    - ADR-026: Database path via engine.get_db_path() (SSOT)
"""

from pathlib import Path

from sqlmodel import SQLModel, create_engine

from timeblock.database.engine import get_db_path
from timeblock.models import Habit, HabitInstance, Routine, Task, TimeLog


def migrate_v2(db_path: Path | None = None) -> None:
    """Adiciona tabelas v2.0.

    Args:
        db_path: Caminho opcional do banco. Se não fornecido,
                 usa get_db_path() conforme ADR-026 (SSOT).
    """
    path = str(db_path) if db_path else get_db_path()
    engine = create_engine(f"sqlite:///{path}")

    # Nota: __table__ é atributo dinâmico do SQLModel/SQLAlchemy
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Routine.__table__,  # type: ignore[attr-defined]
            Habit.__table__,  # type: ignore[attr-defined]
            HabitInstance.__table__,  # type: ignore[attr-defined]
            Task.__table__,  # type: ignore[attr-defined]
            TimeLog.__table__,  # type: ignore[attr-defined]
        ],
    )

    print("[OK] Tabelas v2.0 criadas: Routine, Habit, HabitInstance, Task, TimeLog")


def migrate_events_to_tasks() -> int:
    """Migra Events existentes para Tasks (opcional)."""
    # TODO: Implementar em próxima fase
    return 0
