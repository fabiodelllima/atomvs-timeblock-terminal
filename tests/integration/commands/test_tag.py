"""Testes de integração para comandos de tag.

Valida comandos CLI de tag via CliRunner.

BRs validadas:
- BR-TAG-001: Estrutura de Tag (name opcional, color obrigatório com default)
- BR-TAG-002: Associação com Eventos
"""

from pathlib import Path

import pytest
from sqlmodel import SQLModel, create_engine
from typer.testing import CliRunner

from timeblock.commands.tag import app

runner = CliRunner()


@pytest.fixture
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Banco de dados isolado para testes de comando tag."""
    db_path = tmp_path / "test_tag.db"
    monkeypatch.setenv("TIMEBLOCK_DB_PATH", str(db_path))

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    engine.dispose()

    return db_path


class TestBRTag001Structure:
    """Testes para BR-TAG-001: Estrutura de Tag."""

    def test_br_tag_001_create_with_name(self, isolated_db):
        """BR-TAG-001: Cria tag com nome."""
        result = runner.invoke(app, ["create", "Trabalho"])
        assert result.exit_code == 0
        assert "criada" in result.output.lower()
        assert "Trabalho" in result.output

    def test_br_tag_001_color_has_default(self, isolated_db):
        """BR-TAG-001: Color tem default amarelo (#fbd75b)."""
        result = runner.invoke(app, ["create", "Test"])
        assert result.exit_code == 0
        assert "#fbd75b" in result.output.lower()

    def test_br_tag_001_color_customizable(self, isolated_db):
        """BR-TAG-001: Color pode ser customizado."""
        result = runner.invoke(app, ["create", "Saúde", "--color", "#00FF00"])
        assert result.exit_code == 0
        assert "#00FF00" in result.output

    def test_br_tag_001_name_must_be_unique(self, isolated_db):
        """BR-TAG-001: Nome deve ser único (se fornecido)."""
        runner.invoke(app, ["create", "Trabalho"])
        result = runner.invoke(app, ["create", "Trabalho"])
        assert result.exit_code == 1
        assert "erro" in result.output.lower()


class TestTagCRUDOperations:
    """Testes para operações CRUD de Tag."""

    def test_list_tags_empty(self, isolated_db):
        """Lista vazia exibe mensagem apropriada."""
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "nenhuma" in result.output.lower()

    def test_list_tags_shows_all(self, isolated_db):
        """Lista exibe todas as tags criadas."""
        runner.invoke(app, ["create", "Trabalho"])
        runner.invoke(app, ["create", "Pessoal"])

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Trabalho" in result.output
        assert "Pessoal" in result.output

    def test_update_tag_name(self, isolated_db):
        """Atualiza nome da tag."""
        runner.invoke(app, ["create", "Trabalho"])

        result = runner.invoke(app, ["update", "1", "--name", "Trabalho Remoto"])
        assert result.exit_code == 0
        assert "atualizada" in result.output.lower()

    def test_update_tag_color(self, isolated_db):
        """Atualiza cor da tag."""
        runner.invoke(app, ["create", "Trabalho"])

        result = runner.invoke(app, ["update", "1", "--color", "#FF0000"])
        assert result.exit_code == 0
        assert "atualizada" in result.output.lower()

    def test_update_without_changes_warns(self, isolated_db):
        """Update sem alterações exibe aviso."""
        runner.invoke(app, ["create", "Trabalho"])

        result = runner.invoke(app, ["update", "1"])
        assert result.exit_code == 0
        assert "nenhuma" in result.output.lower()

    def test_update_nonexistent_fails(self, isolated_db):
        """Update de tag inexistente falha."""
        result = runner.invoke(app, ["update", "999", "--name", "Novo"])
        assert result.exit_code == 1
        assert "erro" in result.output.lower()

    def test_delete_tag_with_force(self, isolated_db):
        """Deleta tag com --force."""
        runner.invoke(app, ["create", "Trabalho"])

        result = runner.invoke(app, ["delete", "1", "--force"])
        assert result.exit_code == 0
        assert "deletada" in result.output.lower()

    def test_delete_nonexistent_fails(self, isolated_db):
        """Delete de tag inexistente falha."""
        result = runner.invoke(app, ["delete", "999", "--force"])
        assert result.exit_code == 1
        assert "erro" in result.output.lower()

    def test_delete_removes_from_list(self, isolated_db):
        """Tag deletada não aparece mais na lista."""
        runner.invoke(app, ["create", "Trabalho"])
        runner.invoke(app, ["delete", "1", "--force"])

        result = runner.invoke(app, ["list"])
        assert "Trabalho" not in result.output
