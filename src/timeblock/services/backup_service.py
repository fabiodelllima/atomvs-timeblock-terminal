"""BackupService - Backup automático do banco de dados (BR-DATA-001).

Cria cópia timestamped do SQLite no startup e shutdown da TUI.
Mantém as N cópias mais recentes e remove as antigas.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from timeblock.database.engine import get_db_path
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)

MAX_BACKUPS = 50
BACKUP_DIR_NAME = "backups"


def get_backup_dir() -> Path:
    """Retorna diretório de backups via XDG Base Directory (BR-DATA-001).

    Prioridade:
    1. $XDG_DATA_HOME/atomvs/backups
    2. ~/.local/share/atomvs/backups (fallback XDG padrão)

    Desacoplado de get_db_path para garantir que backups nunca caiam
    em paths relativos ao workspace (regressão #47).
    """
    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        data_dir = Path(xdg_data_home) / "atomvs"
    else:
        data_dir = Path.home() / ".local" / "share" / "atomvs"

    backup_dir = data_dir / BACKUP_DIR_NAME
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def create_backup(label: str = "") -> Path | None:
    """Cria backup do banco com timestamp.

    Args:
        label: Sufixo opcional (ex: 'startup', 'shutdown').

    Returns:
        Path do backup criado ou None se banco não existe.
    """
    db_path = Path(get_db_path())
    if not db_path.exists():
        return None

    backup_dir = get_backup_dir()
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = f"-{label}" if label else ""
    backup_name = f"timeblock-{timestamp}{suffix}.db"
    backup_path = backup_dir / backup_name

    shutil.copy2(db_path, backup_path)
    _cleanup_old_backups(backup_dir)
    logger.info("Backup criado: %s", backup_path)
    return backup_path


def _cleanup_old_backups(backup_dir: Path) -> None:
    """Remove backups antigos mantendo apenas MAX_BACKUPS."""
    backups = sorted(backup_dir.glob("timeblock-*.db"), key=lambda p: p.stat().st_mtime)
    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        oldest.unlink()


def list_backups() -> list[Path]:
    """Lista backups existentes ordenados por data (mais recente primeiro)."""
    backup_dir = get_backup_dir()
    backup_dir.mkdir(exist_ok=True)
    return sorted(backup_dir.glob("timeblock-*.db"), key=lambda p: p.stat().st_mtime, reverse=True)


def restore_backup(backup_path: Path) -> bool:
    logger.info("Restaurando backup: %s", backup_path)
    """Restaura banco a partir de um backup.

    Args:
        backup_path: Caminho do backup a restaurar.

    Returns:
        True se restaurou com sucesso.
    """
    db_path = Path(get_db_path())
    if not backup_path.exists():
        return False

    # Backup de segurança antes de restaurar
    create_backup(label="pre-restore")
    shutil.copy2(backup_path, db_path)
    return True
