"""Comandos para gerenciar tags."""

import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import Session

from timeblock.database import get_engine_context
from timeblock.services.tag_service import TagService

app = typer.Typer(help="Gerenciar tags")
console = Console()


@app.command("create")
def create_tag(
    name: str = typer.Argument(None, help="Nome da tag (opcional)"),
    color: str = typer.Option("#fbd75b", "--color", "-c", help="Cor da tag"),
):
    """Cria tag para categorização."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            service = TagService(session)
            tag = service.create_tag(name=name, color=color)
            session.commit()

            console.print("\n✓ Tag criada!\n", style="bold green")
            console.print(f"ID: {tag.id}")
            if tag.name:
                console.print(f"Nome: [bold]{tag.name}[/bold]")
            console.print(f"Cor: {tag.color}\n")

    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("list")
def list_tags():
    """Lista todas as tags."""
    with get_engine_context() as engine, Session(engine) as session:
        service = TagService(session)
        tags = service.list_tags()

    if not tags:
        console.print("Nenhuma tag encontrada.", style="yellow")
        return

    table = Table(title="Tags")
    table.add_column("ID", style="cyan")
    table.add_column("Nome", style="white")
    table.add_column("Cor", style="yellow")

    for t in tags:
        table.add_row(str(t.id), t.name or "—", t.color)

    console.print()
    console.print(table)
    console.print()


@app.command("update")
def update_tag(
    tag_id: int = typer.Argument(..., help="ID da tag"),
    name: str = typer.Option(None, "--name", "-n", help="Novo nome"),
    color: str = typer.Option(None, "--color", "-c", help="Nova cor"),
):
    """Atualiza tag."""
    try:
        updates = {}
        if name is not None:
            updates["name"] = name
        if color:
            updates["color"] = color

        if not updates:
            console.print("Nenhuma atualização especificada.", style="yellow")
            return

        with get_engine_context() as engine, Session(engine) as session:
            service = TagService(session)
            tag = service.update_tag(tag_id, **updates)
            session.commit()
            console.print(f"✓ Tag {tag.id} atualizada", style="green")

    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)


@app.command("delete")
def delete_tag(
    tag_id: int = typer.Argument(..., help="ID da tag"),
    force: bool = typer.Option(False, "--force", "-f", help="Não pedir confirmação"),
):
    """Deleta tag."""
    try:
        with get_engine_context() as engine, Session(engine) as session:
            service = TagService(session)
            tag = service.get_tag(tag_id)

            if not force:
                name_display = f"[bold]{tag.name}[/bold]" if tag.name else f"ID {tag_id}"
                console.print(f"\nDeletar tag {name_display}?")
                if not typer.confirm("Confirma?", default=False):
                    console.print("Cancelado.", style="yellow")
                    return

            service.delete_tag(tag_id)
            session.commit()
            console.print("✓ Tag deletada", style="green")

    except ValueError as e:
        console.print(f"✗ Erro: {e}", style="red")
        raise typer.Exit(1)
