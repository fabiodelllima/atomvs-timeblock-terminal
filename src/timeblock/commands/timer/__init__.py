"""Comandos para gerenciar timer de tracking."""

import typer

from .commands import (
    cancel_timer,
    pause_timer,
    resume_timer,
    start_timer,
    stop_timer,
    timer_status,
)

app = typer.Typer(help="Gerenciar timer de tracking")

app.command("start")(start_timer)
app.command("pause")(pause_timer)
app.command("resume")(resume_timer)
app.command("stop")(stop_timer)
app.command("cancel")(cancel_timer)
app.command("status")(timer_status)

__all__ = ["app"]
