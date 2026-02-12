"""Testes para TagService - operações CRUD.

BRs validadas:
- BR-TAG-001: Estrutura de Tag (name, color, unicidade)
"""

import pytest
from sqlmodel import Session

from timeblock.services.tag_service import TagService


class TestCreateTag:
    """Testes para create_tag. Validates BR-TAG-001."""

    def test_create_tag_success(self, session: Session) -> None:
        """Cria tag com sucesso."""
        service = TagService(session)
        tag = service.create_tag("Trabalho")

        assert tag.id is not None
        assert tag.name == "Trabalho"
        assert tag.color == "#fbd75b"  # Default amarelo

    def test_create_tag_with_custom_color(self, session: Session) -> None:
        """Cria tag com cor customizada."""
        service = TagService(session)
        tag = service.create_tag("Saúde", color="#00FF00")

        assert tag.color == "#00FF00"

    def test_create_tag_strips_whitespace(self, session: Session) -> None:
        """Remove espaços do nome."""
        service = TagService(session)
        tag = service.create_tag("  Urgente  ")

        assert tag.name == "Urgente"

    def test_create_tag_with_empty_name(self, session: Session) -> None:
        """Rejeita nome vazio."""
        service = TagService(session)

        with pytest.raises(ValueError, match="não pode ser vazio"):
            service.create_tag("   ")

    def test_create_tag_with_long_name(self, session: Session) -> None:
        """Rejeita nome com mais de 50 caracteres."""
        service = TagService(session)
        long_name = "a" * 51

        with pytest.raises(ValueError, match="não pode ter mais de 50 caracteres"):
            service.create_tag(long_name)

    def test_create_tag_with_max_length_name(self, session: Session) -> None:
        """Aceita nome com exatamente 50 caracteres."""
        service = TagService(session)
        max_name = "a" * 50
        tag = service.create_tag(max_name)

        assert tag.name == max_name
        assert len(tag.name) == 50

    def test_create_tag_duplicate_name(self, session: Session) -> None:
        """Rejeita nome duplicado (case-insensitive)."""
        service = TagService(session)
        service.create_tag("Projeto")
        session.commit()

        with pytest.raises(ValueError, match="já existe"):
            service.create_tag("Projeto")


class TestGetTag:
    """Testes para get_tag."""

    def test_get_tag_found(self, session: Session) -> None:
        """Busca tag existente."""
        service = TagService(session)
        created = service.create_tag("Pessoal")
        session.commit()

        found = service.get_tag(created.id)

        assert found.id == created.id
        assert found.name == "Pessoal"

    def test_get_tag_not_found(self, session: Session) -> None:
        """Rejeita busca de tag inexistente."""
        service = TagService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.get_tag(9999)


class TestListTags:
    """Testes para list_tags."""

    def test_list_tags_empty(self, session: Session) -> None:
        """Lista vazia quando não há tags."""
        service = TagService(session)
        tags = service.list_tags()

        assert tags == []

    def test_list_tags_with_data(self, session: Session) -> None:
        """Lista todas as tags."""
        service = TagService(session)
        service.create_tag("Trabalho")
        service.create_tag("Pessoal")
        service.create_tag("Estudo")
        session.commit()

        tags = service.list_tags()

        assert len(tags) == 3

    def test_list_tags_sorted_by_name(self, session: Session) -> None:
        """Lista tags ordenadas alfabeticamente."""
        service = TagService(session)
        service.create_tag("Zebra")
        service.create_tag("Alpha")
        service.create_tag("Beta")
        session.commit()

        tags = service.list_tags()

        assert tags[0].name == "Alpha"
        assert tags[1].name == "Beta"
        assert tags[2].name == "Zebra"


class TestUpdateTag:
    """Testes para update_tag."""

    def test_update_tag_name(self, session: Session) -> None:
        """Atualiza nome da tag."""
        service = TagService(session)
        tag = service.create_tag("Antigo")
        session.commit()

        updated = service.update_tag(tag.id, name="Novo")

        assert updated.name == "Novo"

    def test_update_tag_color(self, session: Session) -> None:
        """Atualiza cor da tag."""
        service = TagService(session)
        tag = service.create_tag("Teste")
        session.commit()

        updated = service.update_tag(tag.id, color="#FF0000")

        assert updated.color == "#FF0000"

    def test_update_tag_multiple_fields(self, session: Session) -> None:
        """Atualiza múltiplos campos."""
        service = TagService(session)
        tag = service.create_tag("Original")
        session.commit()

        updated = service.update_tag(tag.id, name="Modificado", color="#00FF00")

        assert updated.name == "Modificado"
        assert updated.color == "#00FF00"

    def test_update_tag_not_found(self, session: Session) -> None:
        """Rejeita atualização de tag inexistente."""
        service = TagService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.update_tag(9999, name="Teste")

    def test_update_tag_with_empty_name(self, session: Session) -> None:
        """Rejeita nome vazio na atualização."""
        service = TagService(session)
        tag = service.create_tag("Original")
        session.commit()

        with pytest.raises(ValueError, match="não pode ser vazio"):
            service.update_tag(tag.id, name="   ")

    def test_update_tag_with_long_name(self, session: Session) -> None:
        """Rejeita nome longo na atualização."""
        service = TagService(session)
        tag = service.create_tag("Original")
        session.commit()

        with pytest.raises(ValueError, match="não pode ter mais de 50 caracteres"):
            service.update_tag(tag.id, name="a" * 51)

    def test_update_tag_duplicate_name(self, session: Session) -> None:
        """Rejeita nome duplicado na atualização."""
        service = TagService(session)
        service.create_tag("Existente")
        tag2 = service.create_tag("Outra")
        session.commit()

        with pytest.raises(ValueError, match="já existe"):
            service.update_tag(tag2.id, name="Existente")

    def test_update_tag_same_name(self, session: Session) -> None:
        """Permite atualizar mantendo o mesmo nome."""
        service = TagService(session)
        tag = service.create_tag("Teste")
        session.commit()

        # Atualizar cor mantendo nome
        updated = service.update_tag(tag.id, name="Teste", color="#FF0000")

        assert updated.name == "Teste"
        assert updated.color == "#FF0000"

    def test_update_tag_strips_whitespace(self, session: Session) -> None:
        """Remove espaços do nome na atualização."""
        service = TagService(session)
        tag = service.create_tag("Original")
        session.commit()

        updated = service.update_tag(tag.id, name="  Modificado  ")

        assert updated.name == "Modificado"


class TestDeleteTag:
    """Testes para delete_tag."""

    def test_delete_tag_success(self, session: Session) -> None:
        """Deleta tag com sucesso."""
        service = TagService(session)
        tag = service.create_tag("Temporária")
        tag_id = tag.id
        session.commit()

        service.delete_tag(tag_id)
        session.commit()

        # Verificar que foi deletada
        with pytest.raises(ValueError, match="não encontrada"):
            service.get_tag(tag_id)

    def test_delete_tag_not_found(self, session: Session) -> None:
        """Rejeita deleção de tag inexistente."""
        service = TagService(session)

        with pytest.raises(ValueError, match="não encontrada"):
            service.delete_tag(9999)
