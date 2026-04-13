"""StatusBar - Footer contextual com keybindings por panel (BR-TUI-007, BR-TUI-034).

Layout: [rotina ativa] | [keybindings do panel focado] | [timer + hora]
O centro atualiza dinamicamente conforme o panel que recebe foco.

BR-TUI-034: hints exclusivamente no footer global, formato `[tecla] descrição`
com tecla em C_INFO e descrição em C_SUBTEXT1.
"""

import re

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from timeblock.tui.colors import C_INFO, C_SUBTEXT1
from timeblock.utils.logger import get_logger

logger = get_logger(__name__)

# BR-TUI-034 regras 9-12: mapa contextual de keybindings por panel
PANEL_KEYBINDINGS: dict[str, str] = {
    "agenda-content": "[↑↓] navegar",
    "panel-habits": "[j/k] navegar  [v] concluir  [s] skip  [t] timer",
    "panel-tasks": "[j/k] navegar  [v] concluir  [s] adiar  [c] cancelar",
    "panel-timer": "[space] pausar/continuar  [s] parar  [c] cancelar",
    "panel-metrics": "[f] período",
}

DEFAULT_KEYBINDINGS = "[Tab] navegar  [?] ajuda  [Ctrl+Q] sair"

# BR-TUI-034 regra 3: parser do formato `[tecla] descrição`
_HINT_PATTERN = re.compile(r"\[([^\]]+)\]([^\[]*)")


def _format_hint(hint: str) -> str:
    """Converte `[q] sair  [j/k] navegar` em markup Rich colorido.

    BR-TUI-034 regras 6-8: teclas (com colchetes literais) recebem C_INFO,
    descrições recebem C_SUBTEXT1. Sem `[dim]` envolvendo o todo.

    Args:
        hint: string no formato `[<tecla>] <descrição>` repetível.

    Returns:
        Markup Rich pronto para render. String vazia se hint vazio.
        Se o hint não contém colchetes (formato legado/inesperado),
        retorna o texto cru sem colorir.
    """
    if not hint:
        return ""
    parts: list[str] = []
    for match in _HINT_PATTERN.finditer(hint):
        key, desc = match.group(1), match.group(2).strip()
        parts.append(f"[{C_INFO}]({key})[/{C_INFO}] [{C_SUBTEXT1}]{desc}[/{C_SUBTEXT1}]")
    return " [dim]\u00b7[/dim] ".join(parts) if parts else hint


class StatusBar(Widget):
    """Footer persistente com rotina, keybindings contextuais e timer+hora."""

    CLOCK_INTERVAL: int = 60
    TIMER_INTERVAL: int = 1

    routine_name: reactive[str] = reactive("")
    timer_elapsed: reactive[str] = reactive("")
    timer_status: reactive[str] = reactive("")
    focused_panel: reactive[str] = reactive("")

    def __init__(self) -> None:
        super().__init__(id="status-bar")

    def compose(self):
        """Compõe as três seções do footer."""
        yield Static(id="status-left")
        yield Static(id="status-center")
        yield Static(id="status-right")

    def on_mount(self) -> None:
        """Inicia timers de atualização."""
        self._update_all()
        self.set_interval(self.CLOCK_INTERVAL, self._update_clock)

    # =========================================================================
    # Section builders
    # =========================================================================

    def _build_left_section(self) -> str:
        """Rotina ativa ou placeholder."""
        if self.routine_name:
            return f" [bold]{self.routine_name}[/bold]"
        return " [dim][Sem rotina][/dim]"

    def _build_center_section(self) -> str:
        """Keybindings contextuais do panel focado (BR-TUI-034, DT-066)."""
        hint = getattr(self, "_context_hint", "")
        if not hint:
            panel_id = self.focused_panel
            hint = PANEL_KEYBINDINGS.get(panel_id, DEFAULT_KEYBINDINGS) or DEFAULT_KEYBINDINGS
        return _format_hint(hint)

    def _build_right_section(self) -> str:
        """Timer elapsed."""
        if self.timer_elapsed and self.timer_status:
            icon = "▶" if self.timer_status == "running" else "⏸"
            color = "#CBA6F7" if self.timer_status == "running" else "#F9E2AF"
            return f"[{color}]{icon} {self.timer_elapsed}[/{color}] "
        return ""

    # =========================================================================
    # Updates
    # =========================================================================

    def _update_all(self) -> None:
        """Atualiza as três seções."""
        try:
            self.query_one("#status-left", Static).update(self._build_left_section())
            self.query_one("#status-center", Static).update(self._build_center_section())
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            logger.debug("Ignorado: %s", "Exception", exc_info=True)

    def _update_clock(self) -> None:
        """Atualiza seção direita a cada minuto."""
        try:
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            logger.debug("Ignorado: %s", "Exception", exc_info=True)

    def update_focused_panel(self, panel_id: str, context_hint: str = "") -> None:
        """Chamado pelo app quando foco muda entre panels (DT-066)."""
        self._context_hint = context_hint
        self.focused_panel = panel_id

    # =========================================================================
    # Watchers
    # =========================================================================

    def watch_routine_name(self, _value: str) -> None:
        """Reage à mudança de rotina."""
        try:
            self.query_one("#status-left", Static).update(self._build_left_section())
        except Exception:
            logger.debug("Ignorado: %s", "Exception", exc_info=True)

    def watch_focused_panel(self, _value: str) -> None:
        """Reage à mudança de panel focado."""
        try:
            self.query_one("#status-center", Static).update(self._build_center_section())
        except Exception:
            logger.debug("Ignorado: %s", "Exception", exc_info=True)

    def watch_timer_elapsed(self, _value: str) -> None:
        """Reage à mudança de timer."""
        try:
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            logger.debug("Ignorado: %s", "Exception", exc_info=True)

    def watch_timer_status(self, _value: str) -> None:
        """Reage à mudança de status do timer."""
        try:
            self.query_one("#status-right", Static).update(self._build_right_section())
        except Exception:
            logger.debug("Ignorado: %s", "Exception", exc_info=True)
