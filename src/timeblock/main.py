"""Entry point do ATOMVS Time Planner CLI/TUI."""

import sys
from types import TracebackType

import typer

from timeblock.commands import (
    demo,
    habit,
    init,
    reschedule,
    routine,
    tag,
    task,
    timer,
)
from timeblock.utils.logger import configure_logging, get_logger

app = typer.Typer(
    name="timeblock",
    help="TimeBlock Planner - Gerenciador de tempo via CLI",
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
app.add_typer(demo.app, name="demo")


@app.command()
def version():
    """Display version information."""
    typer.echo("TimeBlock v0.1.0")
    typer.echo("CLI para gerenciamento de tempo e hábitos")


def _install_global_excepthook() -> None:
    """Instala handler global para exceções não capturadas.

    Garante que qualquer exceção que escape de todos os try/except
    seja registrada no log antes de terminar o processo. Preserva
    o comportamento padrão (traceback no stderr) após logar.
    """
    original_hook = sys.excepthook
    crash_logger = get_logger("timeblock.crash")

    def _hook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        if not issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            crash_logger.critical(
                "Exceção não capturada: %s: %s",
                exc_type.__name__,
                exc_value,
                exc_info=(exc_type, exc_value, exc_tb),
            )
        original_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook


def launch_tui() -> bool:
    """Importa e executa a TUI. Raises ImportError se textual não instalado."""
    from timeblock.database.migrations.runner import run_pending_migrations

    tui_logger = get_logger(__name__)

    try:
        count = run_pending_migrations()
        if count > 0:
            tui_logger.info("Migrations aplicadas no startup: %d", count)
    except Exception:
        tui_logger.exception("Falha ao executar migrations no startup")

    from timeblock.tui.app import TimeBlockApp

    TimeBlockApp().run()
    return True


def main():
    """Entry point unificado: sem args abre TUI, com args executa CLI."""
    if len(sys.argv) <= 1:
        configure_logging(console=False)
        _install_global_excepthook()
        try:
            launch_tui()
        except ImportError:
            print("[WARN] TUI requer 'textual'.")
            print("       Instale: pip install atomvs-timeblock-terminal[tui]")
            print("       Uso CLI: timeblock --help")
    else:
        configure_logging(console=True)
        _install_global_excepthook()
        app()


if __name__ == "__main__":
    main()
