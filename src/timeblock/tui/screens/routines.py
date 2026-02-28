"""RoutinesScreen - Grade semanal de hábitos por rotina."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Static

# =============================================================================
# Utilitários puros (sem dependência de Textual)
# =============================================================================

DAY_LABELS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

MONTHS_PT = [
    "",
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def calculate_visible_days(terminal_width: int) -> int:
    """Calcula dias visíveis baseado na largura do terminal.

    BR-TUI-011-R10: Responsividade.
    >= 120 cols: 7 dias
    80-119 cols: 5 dias
    < 80 cols: 3 dias
    """
    if terminal_width >= 120:
        return 7
    if terminal_width >= 80:
        return 5
    return 3


def detect_conflicts(habits: list[dict[str, Any]]) -> list[tuple[int, int]]:
    """Detecta pares de hábitos com sobreposição temporal.

    BR-TUI-011-R08: Conflitos exibidos lado a lado, nunca bloqueados.
    Retorna lista de tuplas (id_a, id_b) para cada par conflitante.
    """
    conflicts: list[tuple[int, int]] = []
    for i, a in enumerate(habits):
        for b in habits[i + 1 :]:
            if a["start"] < b["end"] and b["start"] < a["end"]:
                conflicts.append((a["id"], b["id"]))
    return conflicts


# =============================================================================
# RoutineBlock - Representação de um hábito na grade
# =============================================================================


@dataclass
class RoutineBlock:
    """Bloco visual de um hábito na grade semanal.

    BR-TUI-011-R03: Blocos proporcionais (30min = 1 linha).
    """

    habit_name: str
    start: str
    end: str
    color: str = "#CBA6F7"
    habit_id: int = 0

    @property
    def duration_minutes(self) -> int:
        """Duração em minutos."""
        sh, sm = map(int, self.start.split(":"))
        eh, em = map(int, self.end.split(":"))
        return (eh * 60 + em) - (sh * 60 + sm)

    @property
    def height(self) -> int:
        """Altura em linhas (30min = 1 linha, mínimo 1)."""
        return max(1, math.ceil(self.duration_minutes / 30))


# =============================================================================
# RoutinesScreen - Widget principal
# =============================================================================


class RoutinesScreen(Static, can_focus=True):
    """Tela de Rotinas com grade semanal e painel de detalhes.

    BR-TUI-011: Grade semanal com hábitos posicionados por recorrência.
    """

    DEFAULT_CSS = """
    RoutinesScreen {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(
        self,
        routines: list[dict[str, Any]] | None = None,
        habits: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._routines = routines or []
        self._habits = habits if habits is not None else []
        self._selected_habit: dict[str, Any] | None = None
        self._data_loaded = False
        self.focused_day: int = 0
        self.focused_block: int = 0
        self.current_week_offset: int = 0

    def compose(self):
        """Compõe layout da tela de rotinas."""
        with Vertical():
            yield Static(self.get_header_text(), id="routines-header")
            if self._habits:
                with Horizontal():
                    yield Static(self._render_grid(), id="routines-grid")
                    yield Static(self._render_detail_panel(), id="routines-detail")
            else:
                yield Static(self.get_empty_message(), id="routines-empty")

    # =========================================================================
    # BR-TUI-011-R04: Navegação na grade
    # =========================================================================

    def on_key(self, event: Key) -> None:
        """Processa teclas de navegação na grade."""
        key = event.key
        if key == "right":
            if self.focused_day < 6:
                self.focused_day += 1
            event.prevent_default()
        elif key == "left":
            if self.focused_day > 0:
                self.focused_day -= 1
            event.prevent_default()
        elif key == "down":
            self.focused_block += 1
            event.prevent_default()
        elif key == "up":
            if self.focused_block > 0:
                self.focused_block -= 1
            event.prevent_default()
        elif key == "right_square_bracket":
            self.current_week_offset += 1
            event.prevent_default()
        elif key == "left_square_bracket":
            self.current_week_offset -= 1
            event.prevent_default()
        elif key == "shift+t" or key == "T":
            self.current_week_offset = 0
            self.focused_day = 0
            event.prevent_default()

    # =========================================================================
    # BR-TUI-011-R01: Header com lista de rotinas
    # =========================================================================

    def get_header_text(self) -> str:
        """Retorna texto do header com rotinas e indicador de ativa."""
        if not self._routines:
            return "[Nenhuma rotina] - Crie com: timeblock routine add"

        parts = []
        for r in self._routines:
            name = r["name"]
            count = r.get("habit_count", 0)
            if r.get("is_active"):
                parts.append(f"\u25b8 {name} ({count})")
            else:
                parts.append(f"  {name} ({count})")
        return "  ".join(parts)

    # =========================================================================
    # BR-TUI-011-R02: Grade semanal 7 colunas
    # =========================================================================

    def get_day_columns(self) -> list[int]:
        """Retorna lista de 7 identificadores de coluna."""
        return list(range(7))

    def get_day_labels(self) -> list[str]:
        """Retorna labels dos dias (Seg-Dom)."""
        return DAY_LABELS.copy()

    def get_time_ruler(self) -> list[str]:
        """Retorna lista de horários da régua vertical (06:00-22:00)."""
        return [f"{h:02d}:00" for h in range(6, 23)]

    def get_week_period(self) -> str:
        """Retorna string do período da semana atual.

        BR-TUI-011-R02: Ex: '17-23 Fev 2026'.
        """
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday += timedelta(weeks=self.current_week_offset)
        sunday = monday + timedelta(days=6)

        if monday.month == sunday.month:
            return f"{monday.day}-{sunday.day} {MONTHS_PT[monday.month]} {monday.year}"
        return (
            f"{monday.day} {MONTHS_PT[monday.month]}-"
            f"{sunday.day} {MONTHS_PT[sunday.month]} {sunday.year}"
        )

    # =========================================================================
    # BR-TUI-011-R05: Painel de detalhes
    # =========================================================================

    def select_habit(
        self,
        habit_id: int,
        name: str,
        start: str = "",
        end: str = "",
    ) -> None:
        """Seleciona hábito para exibição no painel de detalhes."""
        duration = ""
        if start and end:
            sh, sm = map(int, start.split(":"))
            eh, em = map(int, end.split(":"))
            mins = (eh * 60 + em) - (sh * 60 + sm)
            duration = f"{mins}min"

        self._selected_habit = {
            "id": habit_id,
            "name": name,
            "start": start,
            "end": end,
            "duration": duration,
        }

    def get_detail_panel(self) -> dict[str, Any]:
        """Retorna dados do painel de detalhes do hábito selecionado."""
        if self._selected_habit:
            return self._selected_habit
        return {}

    # =========================================================================
    # BR-TUI-011-R09: Rotina vazia
    # =========================================================================

    def get_empty_message(self) -> str:
        """Mensagem quando rotina não possui hábitos."""
        return "Nenhum hábito. Pressione [n] para criar"

    def get_rendered_blocks(self) -> list[RoutineBlock]:
        """Retorna blocos renderizados na grade."""
        return [
            RoutineBlock(
                habit_name=h.get("name", ""),
                start=h.get("start", ""),
                end=h.get("end", ""),
                color=h.get("color", "#CBA6F7"),
                habit_id=h.get("id", 0),
            )
            for h in self._habits
        ]

    # =========================================================================
    # BR-TUI-011-R11: Refresh
    # =========================================================================

    def on_focus(self) -> None:
        """Recarrega dados ao receber foco."""
        self._data_loaded = True

    # =========================================================================
    # Rendering helpers (internos)
    # =========================================================================

    def _render_grid(self) -> str:
        """Renderiza grade temporal (placeholder)."""
        period = self.get_week_period()
        labels = "  ".join(self.get_day_labels())
        return f"{period}\n{labels}"

    def _render_detail_panel(self) -> str:
        """Renderiza painel de detalhes (placeholder)."""
        if self._selected_habit:
            return str(self._selected_habit.get("name", ""))
        return "[Selecione um hábito]"
