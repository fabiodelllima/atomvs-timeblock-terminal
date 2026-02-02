"""Service para gerenciar tags."""

from sqlmodel import Session, select

from timeblock.models import Tag


class TagService:
    """Gerencia operações de tags."""

    def __init__(self, session: Session) -> None:
        """Inicializa service com session."""
        self.session = session

    def _validate_name(self, name: str) -> str:
        """Valida e normaliza nome da tag.

        Business Rules:
            - BR-TAG-001: name 1-50 chars, único (case-insensitive)
        """
        name = name.strip()
        if not name:
            raise ValueError("Nome da tag não pode ser vazio")
        if len(name) > 50:
            raise ValueError("Nome da tag não pode ter mais de 50 caracteres")

        # Unicidade case-insensitive
        existing = self.session.exec(select(Tag).where(Tag.name == name)).first()
        if existing:
            raise ValueError(f"Tag '{name}' já existe")

        return name

    def create_tag(self, name: str, color: str = "#fbd75b") -> Tag:
        """Cria tag com nome obrigatório e cor padrão amarelo.

        Business Rules:
            - BR-TAG-001: color obrigatório com default amarelo
            - BR-TAG-001: name 1-50 chars, único
        """
        name = self._validate_name(name)
        tag = Tag(name=name, color=color)
        self.session.add(tag)
        self.session.flush()
        self.session.refresh(tag)
        return tag

    def get_tag(self, tag_id: int) -> Tag:
        """Busca tag por ID."""
        tag = self.session.get(Tag, tag_id)
        if not tag:
            raise ValueError(f"Tag {tag_id} não encontrada")
        return tag

    def list_tags(self) -> list[Tag]:
        """Lista todas as tags."""
        statement = select(Tag).order_by(Tag.name)
        return list(self.session.exec(statement).all())

    def update_tag(self, tag_id: int, **kwargs: str) -> Tag:
        """Atualiza tag.

        Business Rules:
            - BR-TAG-001: validação de name se fornecido
        """
        tag = self.session.get(Tag, tag_id)
        if not tag:
            raise ValueError(f"Tag {tag_id} não encontrada")

        if "name" in kwargs:
            new_name = kwargs["name"].strip()
            if not new_name:
                raise ValueError("Nome da tag não pode ser vazio")
            if len(new_name) > 50:
                raise ValueError("Nome da tag não pode ter mais de 50 caracteres")
            # Unicidade: ignorar a própria tag
            existing = self.session.exec(select(Tag).where(Tag.name == new_name)).first()
            if existing and existing.id != tag_id:
                raise ValueError(f"Tag '{new_name}' já existe")
            kwargs["name"] = new_name

        for key, value in kwargs.items():
            setattr(tag, key, value)

        self.session.add(tag)
        self.session.flush()
        self.session.refresh(tag)
        return tag

    def delete_tag(self, tag_id: int) -> None:
        """Deleta tag."""
        tag = self.session.get(Tag, tag_id)
        if not tag:
            raise ValueError(f"Tag {tag_id} não encontrada")

        self.session.delete(tag)
