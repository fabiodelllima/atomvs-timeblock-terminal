"""Entry point do TimeBlock Organizer CLI/TUI."""

import sys

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


def launch_tui() -> bool:
    """Importa e executa a TUI. Raises ImportError se textual não instalado."""
    from timeblock.tui.app import TimeBlockApp

    TimeBlockApp().run()
    return True


def main():
    """Entry point unificado: sem args abre TUI, com args executa CLI."""
    if len(sys.argv) <= 1:
        try:
            launch_tui()
        except ImportError:
            print("[WARN] TUI requer 'textual'.")
            print("       Instale: pip install atomvs-timeblock-terminal[tui]")
            print("       Uso CLI: timeblock --help")
    else:
        app()


if __name__ == "__main__":
    main()
