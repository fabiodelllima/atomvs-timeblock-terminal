"""Entry point do TimeBlock Organizer CLI."""

import typer

from timeblock.commands import (
    habit,
    init,
    reschedule,
    routine,
    tag,
    task,
    timer,
)

app = typer.Typer(
    name="timeblock",
    help="TimeBlock Organizer - Gerenciador de tempo via CLI",
    add_completion=False,
)

# Comandos base
app.command("init")(init.init)

# Comandos por recurso
app.add_typer(routine.app, name="routine")
app.add_typer(habit.app, name="habit")
app.add_typer(task.app, name="task")
app.add_typer(timer.app, name="timer")
app.add_typer(tag.app, name="tag")
app.add_typer(reschedule.app, name="reschedule")


@app.command()
def version():
    """Display version information."""
    typer.echo("TimeBlock v0.1.0")
    typer.echo("CLI para gerenciamento de tempo e hábitos")


if __name__ == "__main__":
    app()
