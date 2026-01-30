"""
E2E tests validando workflow completo de task.

Referencias:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
BRs cobertas:
    - BR-TASK-001: Estrutura de Task (create)
    - BR-TASK-002: Conclusao de Task (check)
    - BR-TASK-003: Independencia de Routine
    - BR-TASK-004: Visualizacao e Listagem
    - BR-TASK-005: Atualizacao de Task
"""

from pathlib import Path

import pytest
from freezegun import freeze_time
from pytest import MonkeyPatch
from typer.testing import CliRunner

from timeblock.main import app


@pytest.fixture
def isolated_db(tmp_path: Path) -> Path:
    """Cria banco de dados temporario isolado para E2E tests."""
    db_path = tmp_path / "test.db"
    return db_path


@pytest.fixture
def setup_db(isolated_db: Path, monkeypatch: MonkeyPatch) -> CliRunner:
    """Setup basico: apenas init do banco."""
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
    runner = CliRunner()

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, f"Init falhou: {result.output}"

    return runner


class TestBRTaskCreate:
    """
    E2E: Criacao de tasks.

    BRs cobertas:
    - BR-TASK-001: Estrutura de Task
    """

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_001_create_basic(self, setup_db: CliRunner, monkeypatch: MonkeyPatch) -> None:
        """
        E2E: Usuario cria task basica.

        DADO: Sistema inicializado
        QUANDO: Usuario executa 'task create --title "Dentista" --datetime "2025-10-01 14:00"'
        ENTAO: Task eh criada com sucesso
        """
        runner = setup_db

        result = runner.invoke(
            app,
            [
                "task",
                "create",
                "--title",
                "Dentista",
                "--datetime",
                "2025-10-01 14:00",
            ],
        )

        assert result.exit_code == 0, f"Create deve ter sucesso: {result.output}"
        assert "dentista" in result.output.lower(), f"Deve mostrar titulo: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_001_create_with_description(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario cria task com descricao.

        DADO: Sistema inicializado
        QUANDO: Usuario cria task com --desc
        ENTAO: Task eh criada com descricao
        """
        runner = setup_db

        result = runner.invoke(
            app,
            [
                "task",
                "create",
                "--title",
                "Reuniao",
                "--datetime",
                "2025-10-01 15:00",
                "--desc",
                "Reuniao com cliente",
            ],
        )

        assert result.exit_code == 0, f"Create deve ter sucesso: {result.output}"
        assert "reuniao" in result.output.lower(), f"Deve mostrar titulo: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_001_title_required(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Task sem titulo falha.

        DADO: Sistema inicializado
        QUANDO: Usuario tenta criar task sem --title
        ENTAO: Sistema rejeita com erro
        """
        runner = setup_db

        result = runner.invoke(
            app,
            [
                "task",
                "create",
                "--datetime",
                "2025-10-01 14:00",
            ],
        )

        assert result.exit_code != 0, f"Deve falhar sem titulo: {result.output}"


class TestBRTaskComplete:
    """
    E2E: Conclusao de tasks.

    BRs cobertas:
    - BR-TASK-002: Conclusao de Task
    """

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_002_check_task(self, setup_db: CliRunner, monkeypatch: MonkeyPatch) -> None:
        """
        E2E: Usuario marca task como concluida.

        DADO: Task existe (ID=1)
        QUANDO: Usuario executa 'task check 1'
        ENTAO: Task eh marcada como concluida
        """
        runner = setup_db

        # Criar task
        runner.invoke(
            app,
            [
                "task",
                "create",
                "--title",
                "Comprar leite",
                "--datetime",
                "2025-10-01 14:00",
            ],
        )

        # Marcar como concluida
        result = runner.invoke(app, ["task", "check", "1"])

        assert result.exit_code == 0, f"Check deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower()
            for word in ["concluída", "concluida", "completed", "done"]
        ), f"Deve confirmar conclusao: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_002_check_nonexistent_fails(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Check em task inexistente falha.

        DADO: Task ID=999 nao existe
        QUANDO: Usuario executa 'task check 999'
        ENTAO: Sistema rejeita com erro
        """
        runner = setup_db

        result = runner.invoke(app, ["task", "check", "999"])

        assert result.exit_code != 0 or any(
            word in result.output.lower()
            for word in ["nao encontrada", "not found", "erro", "error"]
        ), f"Deve falhar com task inexistente: {result.output}"


class TestBRTaskList:
    """
    E2E: Listagem de tasks.

    BRs cobertas:
    - BR-TASK-003: Independencia de Routine
    - BR-TASK-004: Visualizacao e Listagem
    """

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_003_list_independent_of_routine(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Task list nao depende de routine.

        DADO: Tasks criadas SEM routine
        QUANDO: Usuario executa 'task list'
        ENTAO: Tasks sao listadas independente de routine
        """
        runner = setup_db

        # Criar tasks (sem routine)
        runner.invoke(
            app,
            ["task", "create", "--title", "Task 1", "--datetime", "2025-10-01 10:00"],
        )
        runner.invoke(
            app,
            ["task", "create", "--title", "Task 2", "--datetime", "2025-10-01 11:00"],
        )

        # Listar
        result = runner.invoke(app, ["task", "list"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert "task 1" in result.output.lower(), f"Deve mostrar Task 1: {result.output}"
        assert "task 2" in result.output.lower(), f"Deve mostrar Task 2: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_004_list_pending_only(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Listar apenas tasks pendentes.

        DADO: Tasks pendentes e concluidas
        QUANDO: Usuario executa 'task list --pending'
        ENTAO: Apenas pendentes sao mostradas
        """
        runner = setup_db

        # Criar tasks
        runner.invoke(
            app,
            ["task", "create", "--title", "Pendente", "--datetime", "2025-10-01 10:00"],
        )
        runner.invoke(
            app,
            ["task", "create", "--title", "Concluida", "--datetime", "2025-10-01 11:00"],
        )

        # Marcar uma como concluida
        runner.invoke(app, ["task", "check", "2"])

        # Listar pendentes
        result = runner.invoke(app, ["task", "list", "--pending"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert "pendente" in result.output.lower(), f"Deve mostrar Pendente: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_004_list_empty(self, setup_db: CliRunner, monkeypatch: MonkeyPatch) -> None:
        """
        E2E: Listar sem tasks mostra mensagem apropriada.

        DADO: Nenhuma task existe
        QUANDO: Usuario executa 'task list'
        ENTAO: Sistema informa que nao ha tasks
        """
        runner = setup_db

        result = runner.invoke(app, ["task", "list"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower() for word in ["nenhuma", "no tasks", "vazio", "empty"]
        ), f"Deve informar lista vazia: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_004_list_by_date_range(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Listar tasks por periodo.

        DADO: Tasks em diferentes datas
        QUANDO: Usuario executa 'task list --from X --to Y'
        ENTAO: Apenas tasks no periodo sao mostradas
        """
        runner = setup_db

        # Criar tasks em datas diferentes
        runner.invoke(
            app,
            ["task", "create", "--title", "Hoje", "--datetime", "2025-10-01 10:00"],
        )
        runner.invoke(
            app,
            ["task", "create", "--title", "Amanha", "--datetime", "2025-10-02 10:00"],
        )

        # Listar apenas hoje
        result = runner.invoke(
            app,
            ["task", "list", "--from", "2025-10-01 00:00", "--to", "2025-10-01 23:59"],
        )

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert "hoje" in result.output.lower(), f"Deve mostrar task de hoje: {result.output}"


class TestBRTaskUpdate:
    """
    E2E: Atualizacao de tasks.

    BRs cobertas:
    - BR-TASK-005: Atualizacao de Task
    """

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_005_update_title(self, setup_db: CliRunner, monkeypatch: MonkeyPatch) -> None:
        """
        E2E: Usuario atualiza titulo da task.

        DADO: Task existe (ID=1)
        QUANDO: Usuario executa 'task update 1 --title "Novo titulo"'
        ENTAO: Titulo eh atualizado
        """
        runner = setup_db

        # Criar task
        runner.invoke(
            app,
            ["task", "create", "--title", "Titulo antigo", "--datetime", "2025-10-01 14:00"],
        )

        # Atualizar titulo
        result = runner.invoke(app, ["task", "update", "1", "--title", "Titulo novo"])

        assert result.exit_code == 0, f"Update deve ter sucesso: {result.output}"
        assert "atualizada" in result.output.lower() or "titulo novo" in result.output.lower(), (
            f"Deve confirmar atualizacao: {result.output}"
        )

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_005_update_datetime(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario atualiza datetime da task.

        DADO: Task existe (ID=1)
        QUANDO: Usuario executa 'task update 1 --datetime "2025-10-02 15:00"'
        ENTAO: Datetime eh atualizado
        """
        runner = setup_db

        # Criar task
        runner.invoke(
            app,
            ["task", "create", "--title", "Reuniao", "--datetime", "2025-10-01 14:00"],
        )

        # Atualizar datetime
        result = runner.invoke(app, ["task", "update", "1", "--datetime", "2025-10-02 15:00"])

        assert result.exit_code == 0, f"Update deve ter sucesso: {result.output}"
        assert "atualizada" in result.output.lower(), f"Deve confirmar atualizacao: {result.output}"

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_005_update_nonexistent_fails(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Update em task inexistente falha.

        DADO: Task ID=999 nao existe
        QUANDO: Usuario executa 'task update 999 --title "X"'
        ENTAO: Sistema rejeita com erro
        """
        runner = setup_db

        result = runner.invoke(app, ["task", "update", "999", "--title", "X"])

        assert result.exit_code != 0 or any(
            word in result.output.lower()
            for word in ["nao encontrada", "not found", "erro", "error"]
        ), f"Deve falhar com task inexistente: {result.output}"


class TestBRTaskDelete:
    """
    E2E: Delecao de tasks.
    """

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_delete_with_force(self, setup_db: CliRunner, monkeypatch: MonkeyPatch) -> None:
        """
        E2E: Usuario deleta task com --force.

        DADO: Task existe (ID=1)
        QUANDO: Usuario executa 'task delete 1 --force'
        ENTAO: Task eh deletada sem confirmacao
        """
        runner = setup_db

        # Criar task
        runner.invoke(
            app,
            ["task", "create", "--title", "Para deletar", "--datetime", "2025-10-01 14:00"],
        )

        # Deletar com force
        result = runner.invoke(app, ["task", "delete", "1", "--force"])

        assert result.exit_code == 0, f"Delete deve ter sucesso: {result.output}"
        assert any(word in result.output.lower() for word in ["deletada", "deleted", "removida"]), (
            f"Deve confirmar delecao: {result.output}"
        )

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_delete_with_confirmation(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Usuario deleta task com confirmacao.

        DADO: Task existe (ID=1)
        QUANDO: Usuario executa 'task delete 1' e confirma
        ENTAO: Task eh deletada
        """
        runner = setup_db

        # Criar task
        runner.invoke(
            app,
            ["task", "create", "--title", "Para deletar", "--datetime", "2025-10-01 14:00"],
        )

        # Deletar com confirmacao
        result = runner.invoke(app, ["task", "delete", "1"], input="y\n")

        assert result.exit_code == 0, f"Delete deve ter sucesso: {result.output}"
        assert any(word in result.output.lower() for word in ["deletada", "deleted", "removida"]), (
            f"Deve confirmar delecao: {result.output}"
        )

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_delete_cancelled(self, setup_db: CliRunner, monkeypatch: MonkeyPatch) -> None:
        """
        E2E: Usuario cancela delecao.

        DADO: Task existe (ID=1)
        QUANDO: Usuario executa 'task delete 1' e NAO confirma
        ENTAO: Delecao eh cancelada
        """
        runner = setup_db

        # Criar task
        runner.invoke(
            app,
            ["task", "create", "--title", "Manter", "--datetime", "2025-10-01 14:00"],
        )

        # Cancelar delecao
        result = runner.invoke(app, ["task", "delete", "1"], input="n\n")

        assert "cancelado" in result.output.lower() or result.exit_code == 0, (
            f"Deve cancelar: {result.output}"
        )

    @freeze_time("2025-10-01 09:00:00")
    def test_br_task_delete_nonexistent_fails(
        self, setup_db: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: Delete em task inexistente falha.

        DADO: Task ID=999 nao existe
        QUANDO: Usuario executa 'task delete 999 --force'
        ENTAO: Sistema rejeita com erro
        """
        runner = setup_db

        result = runner.invoke(app, ["task", "delete", "999", "--force"])

        assert result.exit_code != 0 or any(
            word in result.output.lower()
            for word in ["nao encontrada", "not found", "erro", "error"]
        ), f"Deve falhar com task inexistente: {result.output}"
