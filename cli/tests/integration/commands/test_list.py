"""
Integration tests para command list.

Testa listagem de tasks via CLI, validando exibição
correta de dados e comportamento com banco vazio.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta

import pytest
from sqlmodel import SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typer.testing import CliRunner

from src.timeblock.main import app


@pytest.fixture(scope="function")
def isolated_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """
    Cria banco de dados isolado em memória para cada teste.

    Args:
        monkeypatch: Fixture para modificar funções

    Yields:
        None (engine é mockado via monkeypatch)

    Nota:
        Usa SQLite in-memory com StaticPool para permitir
        múltiplas conexões no mesmo banco durante teste.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @contextmanager
    def mock_engine_context():
        try:
            yield engine
        finally:
            pass

    monkeypatch.setattr("src.timeblock.database.get_engine_context", mock_engine_context)
    monkeypatch.setattr("src.timeblock.commands.list.get_engine_context", mock_engine_context)

    SQLModel.metadata.create_all(engine)

    yield

    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def runner() -> CliRunner:
    """Fixture para CliRunner."""
    return CliRunner()


class TestBRTaskDeletion:
    """
    Integration: Deleção de tasks via CLI (BR-TASK-CMD-DELETE-*).

    Valida deleção com flag --force, com confirmação,
    cancelamento e tratamento de IDs inválidos.

    BRs cobertas:
    - BR-TASK-CMD-DELETE-001: Deleta com --force
    - BR-TASK-CMD-DELETE-002: Deleta com confirmação
    - BR-TASK-CMD-DELETE-003: Cancela deleção
    - BR-TASK-CMD-DELETE-004: Rejeita ID inválido
    """

    def test_br_task_cmd_delete_001_with_force(self, runner: CliRunner, isolated_db: None) -> None:
        """
        Integration: Sistema deleta task com --force.

        DADO: Task existente
        QUANDO: Usuário executa delete com --force
        ENTÃO: Deleta sem pedir confirmação

        Referências:
            - BR-TASK-CMD-DELETE-001: Deleta com force
        """
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Delete Me", "-D", dt])
        id_line = next(line for line in create_result.stdout.split("\n") if "ID:" in line)
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "delete", task_id, "--force"])

        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_br_task_cmd_delete_002_with_confirmation(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema deleta task com confirmação 'y'.

        DADO: Task existente
        QUANDO: Usuário responde 'y' na confirmação
        ENTÃO: Task é deletada

        Referências:
            - BR-TASK-CMD-DELETE-002: Deleta com confirmação
        """
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Delete Confirm", "-D", dt])
        id_line = next(line for line in create_result.stdout.split("\n") if "ID:" in line)
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "delete", task_id], input="y\n")

        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_br_task_cmd_delete_003_cancel(self, runner: CliRunner, isolated_db: None) -> None:
        """
        Integration: Sistema preserva task quando usuário cancela.

        DADO: Task existente
        QUANDO: Usuário responde 'n' na confirmação
        ENTÃO: Task não é deletada

        Referências:
            - BR-TASK-CMD-DELETE-003: Cancela deleção
        """
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = runner.invoke(app, ["task", "create", "-t", "Keep Me", "-D", dt])
        id_line = next(line for line in create_result.stdout.split("\n") if "ID:" in line)
        task_id = id_line.split(":")[1].strip()

        result = runner.invoke(app, ["task", "delete", task_id], input="n\n")

        assert result.exit_code == 0
        assert "Cancelado" in result.stdout

    def test_br_task_cmd_delete_004_invalid_id(self, runner: CliRunner, isolated_db: None) -> None:
        """
        Integration: Sistema rejeita ID inválido.

        DADO: ID 999 que não existe
        QUANDO: Usuário tenta deletar
        ENTÃO: Erro (exit_code 1)

        Referências:
            - BR-TASK-CMD-DELETE-004: Rejeita ID inválido
        """
        result = runner.invoke(app, ["task", "delete", "999", "--force"])

        assert result.exit_code == 1
