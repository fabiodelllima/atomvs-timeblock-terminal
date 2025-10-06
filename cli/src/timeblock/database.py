"""Database connection and operations."""

import os
from pathlib import Path

from sqlmodel import SQLModel, create_engine

# Permitir override via variável de ambiente (para testes)
DB_PATH = (
    Path(os.getenv("TIMEBLOCK_DB_PATH", __file__)).parent.parent.parent
    / "data"
    / "timeblock.db"
)


def get_engine():
    """Retorna engine SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{DB_PATH}"
    return create_engine(sqlite_url, echo=False)


def create_db_and_tables():
    """Cria banco e tabelas."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    SQLModel.metadata.create_all(engine)
