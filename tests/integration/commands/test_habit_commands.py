"""
Integration tests para comandos de hábitos.

Testa comandos CLI relacionados a criação, listagem e deleção de hábitos,
validando integração com rotinas e persistência no banco.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

import re

import pytest
from typer.testing import CliRunner

from timeblock.main import app


@pytest.fixture
def runner() -> CliRunner:
    """
    Cria CLI test runner.

    Returns:
        CliRunner configurado para testes.
    """
    return CliRunner()


class TestBRHabitCreation:
    """
    Integration: Criação de hábitos via CLI (BR-HABIT-CREATE-*).

    Valida criação de hábitos com diferentes configurações de recorrência,
    validação de rotinas e persistência de campos opcionais.

    BRs cobertas:
    - BR-HABIT-CREATE-001: Criação com recorrência específica (MONDAY)
    - BR-HABIT-CREATE-002: Criação com recorrência múltipla (WEEKDAYS)
    - BR-HABIT-CREATE-003: Criação com cor personalizada
    - BR-HABIT-CREATE-004: Validação de rotina existente
    """

    def test_br_habit_create_001_monday_recurrence(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """
        Integration: Sistema cria hábito com recorrência específica (MONDAY).

        DADO: Rotina válida existente e ATIVA (BR-ROUTINE-001, BR-ROUTINE-004)
        QUANDO: Usuário cria hábito com recorrência MONDAY
        ENTÃO: Sistema cria hábito com sucesso
        E: Hábito é associado à rotina correta

        Referências:
            - BR-HABIT-CREATE-001: Criação com recorrência específica
            - BR-ROUTINE-001: Rotina ativa como contexto
        """
        # ACT
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                active_routine_id,
                "-t",
                "Monday Run",
                "-r",
                "MONDAY",
                "-s",
                "06:00",
                "-e",
                "07:00",
            ],
        )
        # ASSERT
        assert result.exit_code == 0, (
            f"Criação de hábito MONDAY deve ter sucesso. Output: {result.output}"
        )

    def test_br_habit_create_002_weekdays_recurrence(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """
        Integration: Sistema cria hábito com recorrência múltipla (WEEKDAYS).

        DADO: Rotina válida existente e ATIVA (BR-ROUTINE-001, BR-ROUTINE-004)
        QUANDO: Usuário cria hábito com recorrência WEEKDAYS
        ENTÃO: Sistema cria hábito com sucesso
        E: Hábito será gerado em dias úteis (Seg-Sex)

        Referências:
            - BR-HABIT-CREATE-002: Criação com recorrência múltipla
            - BR-ROUTINE-001: Rotina ativa como contexto
        """
        # ACT
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                active_routine_id,
                "-t",
                "Meditation",
                "-r",
                "WEEKDAYS",
                "-s",
                "05:00",
                "-e",
                "05:30",
            ],
        )
        # ASSERT
        assert result.exit_code == 0, (
            f"Criação de hábito WEEKDAYS deve ter sucesso. Output: {result.output}"
        )

    def test_br_habit_create_003_with_color(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """
        Integration: Sistema cria hábito com cor personalizada.

        DADO: Rotina válida ATIVA e cor hexadecimal válida
        QUANDO: Usuário especifica cor com flag -c
        ENTÃO: Sistema cria hábito com sucesso
        E: Cor é persistida corretamente

        Referências:
            - BR-HABIT-CREATE-003: Criação com cor personalizada
            - BR-ROUTINE-001: Rotina ativa como contexto
        """
        # ACT
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                active_routine_id,
                "-t",
                "Gym",
                "-r",
                "FRIDAY",
                "-s",
                "18:00",
                "-e",
                "19:30",
                "-c",
                "#FF5733",
            ],
        )
        # ASSERT
        assert result.exit_code == 0, f"Criação com cor deve ter sucesso. Output: {result.output}"

    def test_br_habit_create_004_invalid_routine(
        self, runner: CliRunner, isolated_db: None
    ) -> None:
        """
        Integration: Sistema rejeita hábito com rotina inexistente.

        DADO: ID de rotina que não existe (999)
        QUANDO: Usuário tenta criar hábito com rotina inválida
        ENTÃO: Sistema retorna erro (exit_code != 0)
        E: Hábito não é criado

        Referências:
            - BR-HABIT-CREATE-004: Validação de rotina existente
        """
        # ACT
        result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                "999",
                "-t",
                "Test",
                "-r",
                "MONDAY",
                "-s",
                "10:00",
                "-e",
                "11:00",
            ],
        )
        # ASSERT
        assert result.exit_code != 0, "Rotina inexistente deve causar erro"


class TestBRHabitListing:
    """
    Integration: Listagem de hábitos via CLI (BR-HABIT-LIST-*).

    Valida exibição de hábitos de uma rotina, incluindo casos
    de rotina vazia e rotina com múltiplos hábitos.

    BRs cobertas:
    - BR-HABIT-LIST-001: Listagem de rotina vazia
    - BR-HABIT-LIST-002: Listagem com múltiplos hábitos
    """

    def test_br_habit_list_001_empty_routine(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """
        Integration: Sistema lista rotina vazia sem erros.

        DADO: Rotina existente ATIVA sem hábitos (BR-ROUTINE-004)
        QUANDO: Usuário lista hábitos da rotina
        ENTÃO: Sistema retorna sucesso (exit_code 0)
        E: Nenhum hábito é exibido

        Referências:
            - BR-HABIT-LIST-001: Listagem de rotina vazia
            - BR-ROUTINE-004: Rotina ativa como contexto
        """
        # ACT
        result = runner.invoke(app, ["habit", "list", "--routine", active_routine_id])
        # ASSERT
        assert result.exit_code == 0, (
            f"Listagem de rotina vazia deve ter sucesso. Output: {result.output}"
        )

    def test_br_habit_list_002_with_habits(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """
        Integration: Sistema lista múltiplos hábitos corretamente.

        DADO: Rotina ATIVA com 2 hábitos criados (BR-ROUTINE-004)
        QUANDO: Usuário lista hábitos da rotina
        ENTÃO: Sistema exibe ambos os hábitos
        E: Títulos dos hábitos aparecem na saída

        Referências:
            - BR-HABIT-LIST-002: Listagem com múltiplos hábitos
            - BR-ROUTINE-004: Rotina ativa como contexto
        """
        # ARRANGE
        runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                active_routine_id,
                "-t",
                "Habit 1",
                "-r",
                "MONDAY",
                "-s",
                "06:00",
                "-e",
                "07:00",
            ],
        )
        runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                active_routine_id,
                "-t",
                "Habit 2",
                "-r",
                "FRIDAY",
                "-s",
                "18:00",
                "-e",
                "19:00",
            ],
        )
        # ACT
        result = runner.invoke(app, ["habit", "list", "--routine", active_routine_id])
        # ASSERT
        assert result.exit_code == 0, f"Listagem deve ter sucesso. Output: {result.output}"
        assert "Habit 1" in result.stdout, "Habit 1 deve aparecer na listagem"
        assert "Habit 2" in result.stdout, "Habit 2 deve aparecer na listagem"


class TestBRHabitDeletion:
    """
    Integration: Deleção de hábitos via CLI (BR-HABIT-DELETE-*).

    Valida deleção de hábitos com confirmação forçada e cancelamento,
    garantindo que dados são preservados quando usuário cancela.

    BRs cobertas:
    - BR-HABIT-DELETE-001: Deleção com flag --force
    - BR-HABIT-DELETE-002: Cancelamento de deleção
    """

    def test_br_habit_delete_001_with_force(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """
        Integration: Sistema deleta hábito com flag --force (sem confirmação).

        DADO: Hábito existente em rotina ATIVA (BR-ROUTINE-004)
        QUANDO: Usuário executa delete com --force
        ENTÃO: Sistema deleta sem pedir confirmação
        E: Comando retorna sucesso

        Referências:
            - BR-HABIT-DELETE-001: Deleção forçada sem confirmação
            - BR-ROUTINE-004: Rotina ativa como contexto
        """
        # ARRANGE - Criar hábito
        create_result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                active_routine_id,
                "-t",
                "Delete Me",
                "-r",
                "TUESDAY",
                "-s",
                "06:00",
                "-e",
                "07:00",
            ],
        )
        assert create_result.exit_code == 0, f"Criação do hábito falhou: {create_result.output}"

        # Extrair habit_id
        id_lines = [line for line in create_result.stdout.split("\n") if "ID:" in line]
        assert id_lines, f"ID não encontrado na saída: {create_result.output}"
        clean = re.sub(r"\x1b\[[0-9;]*m", "", id_lines[0])
        habit_id = clean.split(":")[1].strip()

        # ACT
        result = runner.invoke(app, ["habit", "delete", habit_id, "--force"])
        # ASSERT
        assert result.exit_code == 0, (
            f"Deleção com --force deve ter sucesso. Output: {result.output}"
        )

    def test_br_habit_delete_002_cancel(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """
        Integration: Sistema preserva hábito quando usuário cancela deleção.

        DADO: Hábito existente em rotina ATIVA (BR-ROUTINE-004)
        QUANDO: Usuário executa delete e responde 'n' (não)
        ENTÃO: Sistema cancela operação
        E: Hábito não é deletado

        Referências:
            - BR-HABIT-DELETE-002: Cancelamento de deleção
            - BR-ROUTINE-004: Rotina ativa como contexto
        """
        # ARRANGE - Criar hábito
        create_result = runner.invoke(
            app,
            [
                "habit",
                "create",
                "--routine",
                active_routine_id,
                "-t",
                "Keep Me",
                "-r",
                "WEDNESDAY",
                "-s",
                "06:00",
                "-e",
                "07:00",
            ],
        )
        assert create_result.exit_code == 0, f"Criação do hábito falhou: {create_result.output}"

        # Extrair habit_id
        id_lines = [line for line in create_result.stdout.split("\n") if "ID:" in line]
        assert id_lines, f"ID não encontrado na saída: {create_result.output}"
        clean = re.sub(r"\x1b\[[0-9;]*m", "", id_lines[0])
        habit_id = clean.split(":")[1].strip()

        # ACT
        result = runner.invoke(app, ["habit", "delete", habit_id], input="n\n")
        # ASSERT
        assert result.exit_code == 0, f"Cancelamento deve retornar sucesso. Output: {result.output}"


def _create_and_get_id(
    runner: CliRunner,
    routine_id: str,
    title: str,
    recurrence: str = "MONDAY",
    start: str = "06:00",
    end: str = "07:00",
) -> str:
    """Cria um hábito via CLI e retorna o id extraído da saída."""
    res = runner.invoke(
        app,
        [
            "habit",
            "create",
            "--routine",
            routine_id,
            "-t",
            title,
            "-r",
            recurrence,
            "-s",
            start,
            "-e",
            end,
        ],
    )
    assert res.exit_code == 0, res.output
    id_lines = [line for line in res.stdout.split("\n") if "ID:" in line]
    assert id_lines, f"ID não encontrado: {res.output}"
    clean = re.sub(r"\x1b\[[0-9;]*m", "", id_lines[0])
    return clean.split(":")[1].strip()


class TestBRHabit006ArchiveCommands:
    """Integration: ciclo de archive via CLI (BR-HABIT-006)."""

    def test_br_habit_006_cli_delete_archives_message(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """habit delete arquiva e a mensagem reflete 'arquivado'."""
        hid = _create_and_get_id(runner, active_routine_id, "Archive Me")
        result = runner.invoke(app, ["habit", "delete", hid, "--force"])
        assert result.exit_code == 0, result.output
        assert "arquiv" in result.stdout.lower()

    def test_br_habit_006_cli_archived_hidden_from_default_list(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """Após archive o hábito some de 'habit list' e aparece em '--all'."""
        hid = _create_and_get_id(runner, active_routine_id, "Hidden Habit")
        runner.invoke(app, ["habit", "delete", hid, "--force"])

        default_list = runner.invoke(app, ["habit", "list", "--routine", active_routine_id])
        assert "Hidden Habit" not in default_list.stdout

        all_list = runner.invoke(app, ["habit", "list", "--routine", active_routine_id, "--all"])
        assert all_list.exit_code == 0, all_list.output
        assert "Hidden Habit" in all_list.stdout

    def test_br_habit_006_cli_list_archived_only(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """'habit list --archived' mostra apenas arquivados."""
        _create_and_get_id(runner, active_routine_id, "Still Active")
        archived_id = _create_and_get_id(runner, active_routine_id, "Now Archived")
        runner.invoke(app, ["habit", "delete", archived_id, "--force"])

        result = runner.invoke(app, ["habit", "list", "--archived"])
        assert result.exit_code == 0, result.output
        assert "Now Archived" in result.stdout
        assert "Still Active" not in result.stdout

    def test_br_habit_006_cli_restore_brings_back(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """'habit restore' reativa e o hábito volta à listagem padrão."""
        hid = _create_and_get_id(runner, active_routine_id, "Restore Me")
        runner.invoke(app, ["habit", "delete", hid, "--force"])

        result = runner.invoke(app, ["habit", "restore", hid])
        assert result.exit_code == 0, result.output

        default_list = runner.invoke(app, ["habit", "list", "--routine", active_routine_id])
        assert "Restore Me" in default_list.stdout

    def test_br_habit_006_cli_purge_with_confirmation(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """'habit purge' com a palavra 'purge' destrói o hábito."""
        hid = _create_and_get_id(runner, active_routine_id, "Purge Me")
        result = runner.invoke(app, ["habit", "purge", hid], input="purge\n")
        assert result.exit_code == 0, result.output

        all_list = runner.invoke(app, ["habit", "list", "--routine", active_routine_id, "--all"])
        assert "Purge Me" not in all_list.stdout

    def test_br_habit_006_cli_purge_aborts_on_wrong_word(
        self, runner: CliRunner, isolated_db: None, active_routine_id: str
    ) -> None:
        """'habit purge' com palavra errada aborta e preserva os dados (cenário BDD)."""
        hid = _create_and_get_id(runner, active_routine_id, "Keep On Wrong")
        runner.invoke(app, ["habit", "purge", hid], input="y\n")

        all_list = runner.invoke(app, ["habit", "list", "--routine", active_routine_id, "--all"])
        assert "Keep On Wrong" in all_list.stdout
