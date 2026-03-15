"""Migração 002: Task Lifecycle (BR-TASK-007..010).

Adiciona novos campos ao Task:
- original_scheduled_datetime
- cancelled_datetime
- postponement_count

Referências:
    - ADR-036: Task Lifecycle Evolution
    - BR-TASK-007: Cancel task
    - BR-TASK-008: Reopen task
    - BR-TASK-009: Postponement tracking
    - BR-TASK-010: Derived status
"""

from sqlalchemy import text
from sqlmodel import Session


def upgrade(session: Session) -> None:
    """Aplica migração: adiciona colunas de lifecycle ao Task.

    Args:
        session: Sessão do banco de dados
    """
    conn = session.connection()

    # Verificar se coluna já existe (idempotente)
    result = conn.execute(text("PRAGMA table_info(tasks)"))
    columns = {row[1] for row in result}

    if "original_scheduled_datetime" not in columns:
        conn.execute(text("ALTER TABLE tasks ADD COLUMN original_scheduled_datetime DATETIME"))

    if "cancelled_datetime" not in columns:
        conn.execute(text("ALTER TABLE tasks ADD COLUMN cancelled_datetime DATETIME"))

    if "postponement_count" not in columns:
        conn.execute(text("ALTER TABLE tasks ADD COLUMN postponement_count INTEGER DEFAULT 0"))

    # Backfill: original = scheduled onde ainda NULL
    conn.execute(
        text(
            "UPDATE tasks "
            "SET original_scheduled_datetime = scheduled_datetime "
            "WHERE original_scheduled_datetime IS NULL"
        )
    )

    session.commit()


def downgrade(session: Session) -> None:
    """Reverte migração (SQLite não suporta DROP COLUMN < 3.35)."""
    pass
