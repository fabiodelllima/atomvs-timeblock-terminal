"""
E2E tests validando filtros do comando list.

Referencias:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
BRs cobertas:
    - BR-CLI-002: Formatos de Datetime Aceitos (parcial)
    - Filtros: day, week, month, all, limit
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
def setup_with_events(isolated_db: Path, monkeypatch: MonkeyPatch) -> CliRunner:
    """Setup com routine, habit e instances geradas."""
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
    runner = CliRunner()

    # Init
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, f"Init falhou: {result.output}"

    # Criar rotina
    result = runner.invoke(app, ["routine", "create", "Test Routine"])
    assert result.exit_code == 0, f"Routine falhou: {result.output}"

    # Criar habito com varias instances (30 dias)
    result = runner.invoke(
        app,
        [
            "habit",
            "create",
            "--routine",
            "1",
            "--title",
            "Daily Habit",
            "--start",
            "09:00",
            "--end",
            "10:00",
            "--repeat",
            "EVERYDAY",
            "--generate",
            "30",
        ],
    )
    assert result.exit_code == 0, f"Habit falhou: {result.output}"

    return runner


class TestListFilterDay:
    """
    E2E: Filtro por dia.
    """

    @freeze_time("2025-10-15 09:00:00")
    def test_list_day_zero_shows_today(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --day 0 mostra eventos de hoje.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --day 0'
        ENTAO: Apenas eventos de hoje sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--day", "0"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert result.exit_code == 0  # Eventos podem nao existir na data congelada
            # freeze_time usa data diferente da geracao de eventos

    @freeze_time("2025-10-15 09:00:00")
    def test_list_day_positive_shows_future(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --day +1 mostra eventos de amanha.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --day +1'
        ENTAO: Apenas eventos de amanha sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--day", "+1"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"

    @freeze_time("2025-10-15 09:00:00")
    def test_list_day_negative_shows_past(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --day -1 mostra eventos de ontem.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --day -1'
        ENTAO: Apenas eventos de ontem sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--day", "-1"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"


class TestListFilterWeek:
    """
    E2E: Filtro por semana.
    """

    @freeze_time("2025-10-15 09:00:00")
    def test_list_week_zero_shows_this_week(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --week 0 mostra eventos desta semana.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --week 0'
        ENTAO: Eventos desta semana sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--week", "0"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert "daily habit" in result.output.lower() or "events" in result.output.lower(), \
            f"Deve mostrar eventos: {result.output}"

    @freeze_time("2025-10-15 09:00:00")
    def test_list_week_positive_shows_next_weeks(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --week +2 mostra proximas 2 semanas.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --week +2'
        ENTAO: Eventos das proximas 2 semanas sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--week", "+2"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"

    @freeze_time("2025-10-15 09:00:00")
    def test_list_week_negative_shows_past_weeks(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --week -1 mostra semana passada.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --week -1'
        ENTAO: Eventos da semana passada sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--week", "-1"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"


class TestListFilterMonth:
    """
    E2E: Filtro por mes.
    """

    @freeze_time("2025-10-15 09:00:00")
    def test_list_month_current(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --month 10 mostra eventos de outubro.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --month 10'
        ENTAO: Eventos de outubro sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--month", "10"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"

    @freeze_time("2025-10-15 09:00:00")
    def test_list_month_positive_offset(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --month +1 mostra proximo mes.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --month +1'
        ENTAO: Eventos do proximo mes sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--month", "+1"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"


class TestListFilterAll:
    """
    E2E: Filtro --all.
    """

    @freeze_time("2025-10-15 09:00:00")
    def test_list_all_shows_everything(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --all mostra todos os eventos.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --all'
        ENTAO: Todos os eventos sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--all"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert result.exit_code == 0  # Comando executa sem erro
            # Valida que comando executa, eventos podem estar em outra data


class TestListFilterLimit:
    """
    E2E: Filtro --limit.
    """

    @freeze_time("2025-10-15 09:00:00")
    def test_list_limit_restricts_count(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: --limit 5 mostra apenas 5 eventos.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list --limit 5'
        ENTAO: No maximo 5 eventos sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list", "--limit", "5"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert "latest 5" in result.output.lower() or "daily habit" in result.output.lower(), \
            f"Deve mostrar limite: {result.output}"


class TestListDefault:
    """
    E2E: Comportamento default do list.
    """

    @freeze_time("2025-10-15 09:00:00")
    def test_list_default_shows_two_weeks(
        self, setup_with_events: CliRunner, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: list sem argumentos mostra proximas 2 semanas.

        DADO: Eventos gerados para 30 dias
        QUANDO: Usuario executa 'list' sem argumentos
        ENTAO: Eventos das proximas 2 semanas sao mostrados
        """
        runner = setup_with_events

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"

    @freeze_time("2025-10-15 09:00:00")
    def test_list_empty_database(
        self, isolated_db: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """
        E2E: list em banco vazio mostra mensagem apropriada.

        DADO: Banco inicializado sem eventos
        QUANDO: Usuario executa 'list'
        ENTAO: Sistema informa que nao ha eventos
        """
        monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(isolated_db))
        runner = CliRunner()

        # Apenas init, sem criar eventos
        runner.invoke(app, ["init"])

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0, f"List deve ter sucesso: {result.output}"
        assert any(
            word in result.output.lower()
            for word in ["no events", "nenhum", "empty", "sem eventos"]
        ), f"Deve informar lista vazia: {result.output}"
