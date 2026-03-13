"""Sistema de logging estruturado para ATOMVS TimeBlock.

Formato dual: texto legível no console (stderr), JSON Lines no arquivo.
Caminhos seguem XDG Base Directory Specification.

Uso:
    # No entrypoint (uma vez):
    from timeblock.utils.logger import configure_logging
    configure_logging()

    # Em qualquer módulo:
    from timeblock.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Operação concluída", extra={"habit_id": 42})

Variáveis de ambiente:
    ATOMVS_LOG_LEVEL: nível mínimo (default: INFO)
    ATOMVS_LOG_FILE: caminho absoluto do arquivo (override do XDG)
    ATOMVS_LOG_CONSOLE: "1" habilita console em qualquer modo (default: só CLI)

Referências:
    - DT-022: Logging estruturado
    - XDG Base Directory Specification (freedesktop.org)
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter  # type: ignore[import-not-found]

_configured: bool = False

# Formato legível para console (stderr)
_CONSOLE_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
_CONSOLE_DATE_FORMAT = "%H:%M:%S"

# Campos incluídos no JSON Lines (arquivo)
_JSON_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"


def _get_log_dir() -> Path:
    """Retorna diretório de logs seguindo XDG Base Directory.

    Prioridade:
        1. $ATOMVS_LOG_FILE (usa diretório pai)
        2. $XDG_DATA_HOME/atomvs/logs
        3. ~/.local/share/atomvs/logs
    """
    env_file = os.environ.get("ATOMVS_LOG_FILE")
    if env_file:
        return Path(env_file).parent

    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data) / "atomvs" / "logs"

    return Path.home() / ".local" / "share" / "atomvs" / "logs"


def _get_log_file() -> Path:
    """Retorna caminho completo do arquivo de log."""
    env_file = os.environ.get("ATOMVS_LOG_FILE")
    if env_file:
        return Path(env_file)

    return _get_log_dir() / "atomvs.jsonl"


def configure_logging(
    *,
    level: str | None = None,
    console: bool | None = None,
    log_file: bool = True,
    max_bytes: int = 10_000_000,
    backup_count: int = 5,
) -> None:
    """Configura logging global do ATOMVS. Idempotente.

    Args:
        level: nível mínimo (env ATOMVS_LOG_LEVEL ou "INFO")
        console: habilita handler stderr (default: True para CLI, False para TUI)
        log_file: habilita handler JSON Lines em arquivo
        max_bytes: tamanho máximo antes de rotação (10MB)
        backup_count: backups mantidos na rotação (5)
    """
    global _configured
    if _configured:
        return
    _configured = True

    resolved_level = (level or os.environ.get("ATOMVS_LOG_LEVEL", "INFO")).upper()

    # Console: variável de ambiente tem prioridade, depois parâmetro
    env_console = os.environ.get("ATOMVS_LOG_CONSOLE")
    if env_console is not None:
        resolved_console = env_console == "1"
    elif console is not None:
        resolved_console = console
    else:
        resolved_console = True

    root = logging.getLogger("timeblock")
    root.setLevel(getattr(logging, resolved_level, logging.INFO))
    root.handlers.clear()

    # Handler console: texto legível no stderr
    if resolved_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(getattr(logging, resolved_level, logging.INFO))
        console_handler.setFormatter(
            logging.Formatter(fmt=_CONSOLE_FORMAT, datefmt=_CONSOLE_DATE_FORMAT)
        )
        root.addHandler(console_handler)

    # Handler arquivo: JSON Lines com rotação
    if log_file:
        file_path = _get_log_file()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JsonFormatter(fmt=_JSON_FORMAT, json_ensure_ascii=False))
        root.addHandler(file_handler)

    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Obtém logger filho do namespace timeblock.

    Se configure_logging() ainda não foi chamado, configura
    com defaults (console only, nível INFO). Isso garante
    compatibilidade com código que chama get_logger diretamente.

    Args:
        name: nome do módulo (geralmente __name__)

    Returns:
        Logger configurado no namespace timeblock.
    """
    if not _configured:
        configure_logging(log_file=False)

    return logging.getLogger(name)


def disable_logging() -> None:
    """Desabilita todos os logs (útil para testes)."""
    logging.disable(logging.CRITICAL)


def enable_logging() -> None:
    """Reabilita logs após disable_logging()."""
    logging.disable(logging.NOTSET)


def _reset_for_testing() -> None:
    """Reseta estado interno para testes. NÃO usar em produção."""
    global _configured
    _configured = False
    root = logging.getLogger("timeblock")
    root.handlers.clear()
