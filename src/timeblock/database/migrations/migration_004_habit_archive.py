"""Migração 004: Archive Lifecycle para Habit (BR-HABIT-005/006).

Adiciona a coluna archived_at à tabela habits para suportar soft delete
(archive) preservando HabitInstance e TimeLog associados.

Referências:
    - ADR-057: Archive Lifecycle para Habit
    - BR-HABIT-005: Deleção de Habit (semântica de archive)
    - BR-HABIT-006: Archive Lifecycle
"""

from sqlalchemy import text
from sqlmodel import Session


def upgrade(session: Session) -> None:
    """Aplica migração: adiciona archived_at ao habits."""
    conn = session.connection()

    result = conn.execute(text("PRAGMA table_info(habits)"))
    columns = {row[1] for row in result}

    if "archived_at" not in columns:
        conn.execute(text("ALTER TABLE habits ADD COLUMN archived_at DATETIME"))

    session.commit()


def downgrade(session: Session) -> None:
    """Reverte migração (SQLite não suporta DROP COLUMN < 3.35)."""
    pass
