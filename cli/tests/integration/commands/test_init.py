"""Integration tests para comando init.

Testa inicialização do banco de dados, incluindo criação inicial,
recriação com confirmação e tratamento de erros.

Referências:
    - ADR-019: Test Naming Convention
    - ADR-026: Test Database Isolation Strategy
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from timeblock.main import app


@pytest.fixture
def empty_db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco de dados vazio (sem tabelas) para testar comando init.
    
    Diferente de isolated_db, esta fixture NÃO cria as tabelas,
    permitindo testar o comando init que faz exatamente isso.
    
    Args:
        tmp_path: Diretório temporário do pytest
        monkeypatch: Fixture para modificar environment
    
    Returns:
        Path onde o banco será criado (arquivo não existe ainda)
    """
    db_path = tmp_path / "test_init.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))
    return db_path


class TestBRSystemInitialization:
    """Integration: Inicialização do sistema (BR-SYSTEM-INIT-*).

    Valida criação, recriação e tratamento de erros do banco de dados
    durante inicialização do sistema.

    BRs cobertas:
    - BR-SYSTEM-INIT-001: Criação inicial do banco
    - BR-SYSTEM-INIT-002: Recriação com confirmação do usuário
    - BR-SYSTEM-INIT-003: Cancelamento de recriação
    - BR-SYSTEM-INIT-004: Tratamento de erros de criação
    """

    def test_br_system_init_001_creates_database(
        self, cli_runner: CliRunner, empty_db_path: Path
    ) -> None:
        """Integration: Sistema cria banco de dados quando não existe.

        DADO: Banco de dados não existe
        QUANDO: Usuário executa comando init
        ENTÃO: Sistema cria arquivo de banco com sucesso
        E: Mensagem de inicialização é exibida
        E: Arquivo do banco existe no filesystem

        Referências:
            - BR-SYSTEM-INIT-001: Criação inicial do banco
        """
        # ASSERT PRE-CONDITION
        assert not empty_db_path.exists(), "Banco não deve existir antes do init"
        # ACT
        result = cli_runner.invoke(app, ["init"])
        # ASSERT
        assert result.exit_code == 0, f"Inicialização deve ter sucesso: {result.output}"
        assert "initialized" in result.output.lower(), "Mensagem deve confirmar inicialização"
        assert empty_db_path.exists(), "Arquivo do banco deve existir"

    def test_br_system_init_002_recreate_with_confirmation(
        self, cli_runner: CliRunner, empty_db_path: Path
    ) -> None:
        """Integration: Sistema recria banco quando usuário confirma.

        DADO: Banco de dados já existe
        QUANDO: Usuário executa init e responde 'y' (sim)
        ENTÃO: Sistema recria banco com sucesso
        E: Mensagem de inicialização é exibida

        Referências:
            - BR-SYSTEM-INIT-002: Recriação com confirmação
        """
        # ARRANGE - Primeira inicialização
        cli_runner.invoke(app, ["init"])
        assert empty_db_path.exists(), "Banco deve existir após primeiro init"
        # ACT - Segunda inicialização com confirmação
        result = cli_runner.invoke(app, ["init"], input="y\n")
        # ASSERT
        assert result.exit_code == 0, "Recriação deve ter sucesso"
        assert "initialized" in result.output.lower(), "Mensagem deve confirmar reinicialização"

    def test_br_system_init_003_cancel_recreation(
        self, cli_runner: CliRunner, empty_db_path: Path
    ) -> None:
        """Integration: Sistema cancela recriação quando usuário recusa.

        DADO: Banco de dados já existe
        QUANDO: Usuário executa init e responde 'n' (não)
        ENTÃO: Sistema cancela operação
        E: Banco existente é preservado
        E: Mensagem de cancelamento é exibida

        Referências:
            - BR-SYSTEM-INIT-003: Cancelamento de recriação
        """
        # ARRANGE - Primeira inicialização
        cli_runner.invoke(app, ["init"])
        # ACT - Segunda inicialização com cancelamento
        result = cli_runner.invoke(app, ["init"], input="n\n")
        # ASSERT
        assert result.exit_code == 0 or result.exit_code == 1, "Cancelamento retorna 0 ou 1"
        assert "aborted" in result.output.lower() or "cancelled" in result.output.lower(), (
            "Mensagem deve indicar cancelamento"
        )

    def test_br_system_init_004_handles_database_error(
        self, cli_runner: CliRunner, empty_db_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Integration: Sistema trata erros de criação graciosamente.

        DADO: Função create_db_and_tables lança exceção
        QUANDO: Usuário executa comando init
        ENTÃO: Sistema retorna exit_code 1 (erro)
        E: Mensagem de erro é exibida
        E: Sistema não trava (exceção tratada)

        Referências:
            - BR-SYSTEM-INIT-004: Tratamento de erros de criação
        """
        # ARRANGE - Mock para simular erro
        def mock_create_error() -> None:
            raise Exception("Simulated database error")

        monkeypatch.setattr("timeblock.commands.init.create_db_and_tables", mock_create_error)
        # ACT
        result = cli_runner.invoke(app, ["init"])
        # ASSERT
        assert result.exit_code == 1, f"Erro deve retornar exit_code 1: {result.output}"
        assert "error" in result.output.lower(), f"Mensagem deve indicar erro: {result.output}"
