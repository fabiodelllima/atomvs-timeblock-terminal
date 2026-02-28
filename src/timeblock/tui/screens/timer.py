"""TimerScreen - Tela de timer com display live (BR-TUI-006).

Exibe contagem em tempo real com atualização a cada segundo.
Suporta start, pause, resume, stop e cancel via keybindings.
"""

from typing import ClassVar

from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class TimerScreen(Widget):
    """Tela de Timer com display live."""

    TIMER_INTERVAL: ClassVar[int] = 1

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("s", "start_timer", "Start", show=True),
        Binding("p", "pause_resume", "Pause/Resume", show=True),
        Binding("enter", "stop_timer", "Stop", show=True),
        Binding("c", "cancel_timer", "Cancel", show=True),
    ]

    timer_state: reactive[str] = reactive("idle")
    current_habit: reactive[str] = reactive("")
    elapsed_seconds: reactive[int] = reactive(0)
    _timelog_id: int | None = None
    _expected_minutes: int = 0

    def compose(self):
        """Compõe layout do TimerScreen."""
        yield Vertical(
            Static(id="timer-header"),
            Static(id="timer-display"),
            Static(id="timer-status"),
            Static(id="timer-actions"),
            id="timer-content",
        )

    def on_mount(self) -> None:
        """Inicia timer de atualização."""
        self.set_interval(self.TIMER_INTERVAL, self._tick)
        self._refresh_display()

    def _tick(self) -> None:
        """Incrementa elapsed a cada segundo (apenas quando running)."""
        if self.timer_state == "running":
            self.elapsed_seconds += 1

    @staticmethod
    def _format_elapsed(seconds: int) -> str:
        """Formata segundos como HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _build_timer_display(self) -> str:
        """Constrói texto principal do display."""
        if self.timer_state == "idle":
            return "[dim]Nenhum timer ativo[/dim]\n\nPressione [bold]s[/bold] para iniciar"

        elapsed_str = self._format_elapsed(self.elapsed_seconds)
        state_label = "RUNNING" if self.timer_state == "running" else "PAUSADO"

        if self.timer_state == "paused":
            state_display = f"[bold yellow]{state_label}[/bold yellow]"
        else:
            state_display = f"[bold green]{state_label}[/bold green]"

        return f"[bold]{self.current_habit}[/bold]\n\n  {elapsed_str}\n\n  {state_display}"

    def _build_session_summary(
        self,
        habit_name: str,
        elapsed_seconds: int,
        expected_minutes: int,
    ) -> str:
        """Constrói resumo da sessão finalizada."""
        elapsed_min = elapsed_seconds / 60
        completion = round((elapsed_min / expected_minutes) * 100, 2) if expected_minutes > 0 else 0

        # Determina substatus
        if completion >= 150:
            substatus = "EXCESSIVE"
        elif completion >= 110:
            substatus = "OVERDONE"
        elif completion >= 90:
            substatus = "FULL"
        else:
            substatus = "PARTIAL"

        elapsed_str = self._format_elapsed(elapsed_seconds)

        return (
            f"╔{'═' * 40}╗\n"
            f"║  [bold]{habit_name}[/bold]\n"
            f"╠{'═' * 40}╣\n"
            f"║  Tempo: {elapsed_str} ({elapsed_min:.0f}min)\n"
            f"║  Completion: {completion}%\n"
            f"║  Status: DONE ({substatus})\n"
            f"╚{'═' * 40}╝"
        )

    def _get_status_bar_data(self) -> dict[str, str]:
        """Retorna dados para atualizar StatusBar."""
        if self.timer_state in ("running", "paused"):
            return {
                "habit": self.current_habit,
                "elapsed": self._format_elapsed(self.elapsed_seconds),
            }
        return {"habit": "", "elapsed": ""}

    def _refresh_display(self) -> None:
        """Atualiza widgets visuais."""
        try:
            self.query_one("#timer-display", Static).update(self._build_timer_display())

            # Atualiza header com contexto
            header_text = (
                "[bold]Timer[/bold]"
                if self.timer_state == "idle"
                else f"[bold]Timer[/bold] - {self.current_habit}"
            )
            self.query_one("#timer-header", Static).update(header_text)

            # Atualiza ações disponíveis
            if self.timer_state == "idle":
                actions = "[dim]s[/dim] Start"
            elif self.timer_state == "running":
                actions = "[dim]p[/dim] Pause  [dim]enter[/dim] Stop  [dim]c[/dim] Cancel"
            else:  # paused
                actions = "[dim]p[/dim] Resume  [dim]enter[/dim] Stop  [dim]c[/dim] Cancel"
            self.query_one("#timer-actions", Static).update(actions)
        except Exception:
            pass

    def _update_status_bar(self) -> None:
        """Propaga estado do timer para StatusBar global."""
        try:
            status_bar = self.app.query_one("#status-bar")
            data = self._get_status_bar_data()
            status_bar.timer_habit = data["habit"]  # type: ignore[attr-defined]
            status_bar.timer_elapsed = data["elapsed"]  # type: ignore[attr-defined]
        except Exception:
            pass

    # ==================== Watchers ====================

    def watch_timer_state(self, _value: str) -> None:
        """Reage à mudança de estado."""
        self._refresh_display()
        self._update_status_bar()

    def watch_elapsed_seconds(self, _value: int) -> None:
        """Reage à incremento de elapsed."""
        self._refresh_display()
        self._update_status_bar()

    # ==================== Actions ====================

    def action_start_timer(self) -> None:
        """Inicia timer (placeholder - será conectado ao service)."""
        if self.timer_state != "idle":
            return
        # TODO: Conectar ao TimerService.start_timer() via BR-TUI-009
        self.current_habit = "Timer"
        self.elapsed_seconds = 0
        self.timer_state = "running"

    def action_pause_resume(self) -> None:
        """Alterna entre pause e resume."""
        if self.timer_state == "running":
            # TODO: Conectar ao TimerService.pause_timer()
            self.timer_state = "paused"
        elif self.timer_state == "paused":
            # TODO: Conectar ao TimerService.resume_timer()
            self.timer_state = "running"

    def action_stop_timer(self) -> None:
        """Para timer e exibe resumo."""
        if self.timer_state not in ("running", "paused"):
            return
        # TODO: Conectar ao TimerService.stop_timer()
        summary = self._build_session_summary(
            habit_name=self.current_habit,
            elapsed_seconds=self.elapsed_seconds,
            expected_minutes=self._expected_minutes,
        )
        try:
            self.query_one("#timer-display", Static).update(summary)
        except Exception:
            pass
        self.timer_state = "idle"
        self.current_habit = ""
        self.elapsed_seconds = 0

    def action_cancel_timer(self) -> None:
        """Cancela timer sem salvar (placeholder para confirmação)."""
        if self.timer_state not in ("running", "paused"):
            return
        # TODO: Adicionar dialog de confirmação
        # TODO: Conectar ao TimerService.reset_timer()
        self.timer_state = "idle"
        self.current_habit = ""
        self.elapsed_seconds = 0
