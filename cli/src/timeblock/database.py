"""Database connection and operations."""
import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine


def get_db_path() -> str:
    """Get database path from environment or default."""
    db_path = os.getenv("TIMEBLOCK_DB_PATH")
    if db_path is None:
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = str(data_dir / "timeblock.db")
    return db_path


def get_engine():
    """Get SQLite engine."""
    db_path = get_db_path()
    return create_engine(f"sqlite:///{db_path}", echo=False)


def create_db_and_tables():
    """Create database tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    return engine
