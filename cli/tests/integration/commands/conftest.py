"""Fixtures para testes de comandos CLI.

Referências:
    - ADR-026: Test Database Isolation Strategy
"""

import re
from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner

from timeblock.main import app


@pytest.fixture
def cli_runner() -> CliRunner:
    """Runner para comandos CLI."""
    return CliRunner()


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco de dados isolado para testes de integração CLI.

    Configura TIMEBLOCK_DB_PATH via env var, garantindo que todo o sistema
    use o banco temporário sem necessidade de monkeypatch de módulos.

    Args:
        tmp_path: Diretório temporário do pytest (cleanup automático)
        monkeypatch: Fixture para modificar environment

    Returns:
        Path do banco de dados de teste

    Referências:
        - ADR-026: Test Database Isolation Strategy
        - 12-Factor App: Config via environment
    """
    db_path = tmp_path / "test_cli.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path


@pytest.fixture
def routine_id(cli_runner: CliRunner, isolated_db: Path) -> str:
    """Cria rotina de teste e retorna seu ID.

    ATENÇÃO: Esta fixture NÃO garante que a rotina está ativa.
    Para testes que precisam de rotina ativa, use `active_routine_id`.

    Args:
        cli_runner: CLI runner fixture
        isolated_db: Banco de dados isolado

    Returns:
        ID da rotina criada como string.
    """
    result = cli_runner.invoke(app, ["routine", "create", "Test Routine"], input="y\n")
    id_lines = [line for line in result.stdout.split("\n") if "ID:" in line]
    clean = re.sub(r"\x1b\[[0-9;]*m", "", id_lines[0])
    return clean.split(":")[1].strip()


@pytest.fixture
def active_routine_id(cli_runner: CliRunner, isolated_db: Path) -> str:
    """Cria rotina de teste e GARANTE que está ativa.

    Valida:
        - BR-ROUTINE-001: Criar rotina não ativa automaticamente
        - BR-ROUTINE-004: Comandos habit precisam de rotina ativa

    Args:
        cli_runner: CLI runner fixture
        isolated_db: Banco de dados isolado

    Returns:
        ID da rotina ativa como string.
    """
    result = cli_runner.invoke(app, ["routine", "create", "Test Routine"])
    assert result.exit_code == 0, f"Criação de rotina falhou: {result.output}"

    id_lines = [line for line in result.stdout.split("\n") if "ID:" in line]
    assert id_lines, f"ID não encontrado na saída: {result.output}"

    clean = re.sub(r"\x1b\[[0-9;]*m", "", id_lines[0])
    routine_id = clean.split(":")[1].strip()

    result = cli_runner.invoke(app, ["routine", "activate", routine_id])
    assert result.exit_code == 0, f"Ativação de rotina falhou: {result.output}"

    return routine_id
