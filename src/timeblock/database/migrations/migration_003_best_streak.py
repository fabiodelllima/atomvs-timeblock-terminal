"""Migração 003: best_streak persistido (BR-TUI-033-R3).

Adiciona campo best_streak à tabela routines para persistir
o maior streak já atingido, evitando perda ao calcular
em janela temporal de 30 dias.

Referências:
    - ADR-047: Design do MetricsPanel
    - BR-TUI-033-R3: best_streak persiste o maior valor
"""

from sqlalchemy import text
from sqlmodel import Session


def upgrade(session: Session) -> None:
    """Aplica migração: adiciona best_streak ao routines."""
    conn = session.connection()

    result = conn.execute(text("PRAGMA table_info(routines)"))
    columns = {row[1] for row in result}

    if "best_streak" not in columns:
        conn.execute(text("ALTER TABLE routines ADD COLUMN best_streak INTEGER DEFAULT 0"))

    session.commit()


def downgrade(session: Session) -> None:
    """Reverte migração (SQLite não suporta DROP COLUMN < 3.35)."""
    pass
