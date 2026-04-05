"""Conexão e operações de banco de dados."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlmodel import SQLModel, create_engine


def get_db_path() -> str:
    """Retorna caminho do banco de dados via XDG Base Directory.

    Prioridade:
    1. TIMEBLOCK_DB_PATH (env override)
    2. ~/.local/share/atomvs/atomvs.db (XDG default)

    Cria diretório se não existir.
    """
    db_path = os.getenv("TIMEBLOCK_DB_PATH")
    if db_path is None:
        xdg_data_home = os.getenv("XDG_DATA_HOME")
        if xdg_data_home:
            data_dir = Path(xdg_data_home) / "atomvs"
        else:
            data_dir = Path.home() / ".local" / "share" / "atomvs"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = str(data_dir / "atomvs.db")
    return db_path


def get_engine():
    """Retorna engine SQLite com foreign keys habilitadas."""
    db_path = get_db_path()
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
        """Habilita foreign keys no SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


@contextmanager
def get_engine_context():
    """Retorna engine SQLite com cleanup automático."""
    engine = get_engine()
    try:
        yield engine
    finally:
        engine.dispose()


def create_db_and_tables():
    """Cria tabelas do banco de dados.

    Importa todos os modelos para registrar no SQLModel.metadata
    antes de criar as tabelas.
    """
    from timeblock.models import (  # noqa: F401  # pyright: ignore[reportUnusedImport]
        Habit,
        HabitInstance,
        Routine,
        Tag,
        Task,
        TimeLog,
    )

    with get_engine_context() as engine:
        SQLModel.metadata.create_all(engine)
    return engine
