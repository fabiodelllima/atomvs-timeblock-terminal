"""
Integration tests para command list.

Testa listagem de tasks via CLI, validando exibição
correta de dados e comportamento com banco vazio.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix

Nota:
    Usa fixture `isolated_db` do conftest.py que configura
    DATABASE_PATH via env var (sem monkeypatch de módulos).
"""

from datetime import datetime, timedelta
from pathlib import Path

from typer.testing import CliRunner

from timeblock.main import app

# Usa fixtures do conftest.py:
# - isolated_db: configura TIMEBLOCK_DB_PATH via env var
# - cli_runner: CliRunner instance


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

    def test_br_task_cmd_delete_001_with_force(
        self, cli_runner: CliRunner, isolated_db: Path
    ) -> None:
        """
        Integration: Sistema deleta task com --force.

        DADO: Task existente
        QUANDO: Usuário executa delete com --force
        ENTÃO: Deleta sem pedir confirmação

        Referências:
            - BR-TASK-CMD-DELETE-001: Deleta com force
        """
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = cli_runner.invoke(app, ["task", "create", "-t", "Delete Me", "-D", dt])
        id_line = next(line for line in create_result.stdout.split("\n") if "ID:" in line)
        task_id = id_line.split(":")[1].strip()

        result = cli_runner.invoke(app, ["task", "delete", task_id, "--force"])

        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_br_task_cmd_delete_002_with_confirmation(
        self, cli_runner: CliRunner, isolated_db: Path
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
        create_result = cli_runner.invoke(app, ["task", "create", "-t", "Delete Confirm", "-D", dt])
        id_line = next(line for line in create_result.stdout.split("\n") if "ID:" in line)
        task_id = id_line.split(":")[1].strip()

        result = cli_runner.invoke(app, ["task", "delete", task_id], input="y\n")

        assert result.exit_code == 0
        assert "Tarefa deletada" in result.stdout

    def test_br_task_cmd_delete_003_cancel(self, cli_runner: CliRunner, isolated_db: Path) -> None:
        """
        Integration: Sistema preserva task quando usuário cancela.

        DADO: Task existente
        QUANDO: Usuário responde 'n' na confirmação
        ENTÃO: Task não é deletada

        Referências:
            - BR-TASK-CMD-DELETE-003: Cancela deleção
        """
        dt = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
        create_result = cli_runner.invoke(app, ["task", "create", "-t", "Keep Me", "-D", dt])
        id_line = next(line for line in create_result.stdout.split("\n") if "ID:" in line)
        task_id = id_line.split(":")[1].strip()

        result = cli_runner.invoke(app, ["task", "delete", task_id], input="n\n")

        assert result.exit_code == 0
        assert "Cancelado" in result.stdout

    def test_br_task_cmd_delete_004_invalid_id(
        self, cli_runner: CliRunner, isolated_db: Path
    ) -> None:
        """
        Integration: Sistema rejeita ID inválido.

        DADO: ID 999 que não existe
        QUANDO: Usuário tenta deletar
        ENTÃO: Erro (exit_code 1)

        Referências:
            - BR-TASK-CMD-DELETE-004: Rejeita ID inválido
        """
        result = cli_runner.invoke(app, ["task", "delete", "999", "--force"])

        assert result.exit_code == 1
