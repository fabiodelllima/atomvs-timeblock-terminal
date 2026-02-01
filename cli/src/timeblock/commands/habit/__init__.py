"""Comandos para gerenciar hábitos."""

import typer

from .actions import adjust_instance, skip_instance
from .atom import atom_app
from .crud import create_habit, delete_habit, list_habits, update_habit

app = typer.Typer(help="Gerenciar hábitos")

# Registrar comandos CRUD
app.command("create")(create_habit)
app.command("list")(list_habits)
app.command("update")(update_habit)
app.command("delete")(delete_habit)

# Registrar ações
app.command("adjust")(adjust_instance)
app.command("skip")(skip_instance)

# Registrar sub-app atom
app.add_typer(atom_app, name="atom")

__all__ = ["app"]
