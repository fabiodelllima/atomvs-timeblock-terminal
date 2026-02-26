"""Funções de formatação e renderização para a TUI (BR-TUI-003).

Formata durações, gera slots de tempo, renderiza ASCII art do timer
e compõe estilos visuais dos blocos da agenda.
"""

from timeblock.tui.colors import (
    C_SURFACE,
    fill_char,
    is_bold_status,
    status_bg,
    status_color,
    status_icon,
    status_label,
)

# =========================================================================
# ASCII art digits (3 linhas, para timer card)
# =========================================================================
_DIGITS = {
    "0": ["█▀█", "█ █", "▀▀▀"],
    "1": [" ▄█", "  █", "  ▀"],
    "2": ["▀▀█", "█▀▀", "▀▀▀"],
    "3": ["▀▀█", " ▀█", "▀▀▀"],
    "4": ["█ █", "▀▀█", "  ▀"],
    "5": ["█▀▀", "▀▀█", "▀▀▀"],
    "6": ["█▀▀", "█▀█", "▀▀▀"],
    "7": ["▀▀█", "  █", "  ▀"],
    "8": ["█▀█", "█▀█", "▀▀▀"],
    "9": ["█▀█", "▀▀█", "▀▀▀"],
    ":": [" ", "·", " "],
}


def render_ascii_time(text: str) -> list[str]:
    """Renderiza string MM:SS como 3 linhas de ASCII art."""
    lines = ["", "", ""]
    for ch in text:
        d = _DIGITS.get(ch, [ch, ch, ch])
        for i in range(3):
            lines[i] += d[i] + " "
    return lines


def calculate_block_height(minutes: int) -> int:
    """Calcula altura proporcional do bloco (30min = 1 linha, mínimo 1)."""
    return max(1, minutes // 30)


def generate_time_slots(start: str, end: str) -> list[str]:
    """Gera slots de 30min entre start e end."""
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    slots: list[str] = []
    h, m = sh, sm
    while h < eh or (h == eh and m < em):
        slots.append(f"{h:02d}:{m:02d}")
        m += 30
        if m >= 60:
            m = 0
            h += 1
    return slots


def format_duration(minutes: int | None) -> str:
    """Formata duração para agenda: >= 60 como Xh ou XhYY, < 60 como Xm."""
    if not minutes:
        return ""
    if minutes >= 60:
        h = minutes // 60
        m = minutes % 60
        return f"{h}h{m:02d}" if m else f"{h}h"
    return f"{minutes}m"


def format_duration_card(minutes: int | None) -> str:
    """Formata duração para card hábitos: 01h30m / 00h30m (zero-padded)."""
    if not minutes:
        return ""
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}h{m:02d}m"


def spaced_title(left: str, right: str, width: int = 48) -> str:
    """Simula space-between no border_title."""
    gap = max(2, width - len(left) - len(right))
    return f"{left} [{C_SURFACE}]{'─' * (gap - 2)}[/{C_SURFACE}] {right}"


def block_style(status: str, substatus: str | None = None) -> tuple[str, str]:
    """Retorna fill e indicador para um bloco (compat com testes)."""
    color = status_color(status, substatus)
    bg = status_bg(status, substatus)
    icon = status_icon(status, substatus)
    label = status_label(status, substatus)
    fc = fill_char(status, substatus)
    bold = is_bold_status(status)
    fill = f"[{color} on {bg}]{fc * 31}[/{color} on {bg}]"
    if bold:
        indicator = f"[bold {color}]{icon} {label}[/bold {color}]"
    else:
        indicator = f"[{color}]{icon} {label}[/{color}]"
    return fill, indicator
