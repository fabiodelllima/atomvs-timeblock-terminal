"""Cores semânticas Catppuccin Mocha (color-system.md, ADR-021).

Constantes de cor, backgrounds e funções de mapeamento status → cor/ícone/label.
Single source of truth para toda a camada TUI.
"""

# =========================================================================
# Foreground colors (Catppuccin Mocha)
# =========================================================================
C_SUCCESS = "#A6E3A1"  # Green: done/full, completed
C_BELOW = "#F5E0DC"  # Rosewater: done/partial (<90%)
C_ABOVE = "#F2CDCD"  # Flamingo: done/overdone (110-150%)
C_OVERLIMIT = "#FAB387"  # Peach: done/excessive (>150%)
C_WARNING = "#F9E2AF"  # Yellow: paused, skip justified, hoje
C_ERROR = "#F38BA8"  # Red: NOT_DONE, skip unjustified, overdue
C_PASSIVE = "#EBA0AC"  # Maroon: ignored (omissão passiva)
C_INFO = "#89B4FA"  # Blue: rescheduled, links
C_ACCENT = "#CBA6F7"  # Mauve: running, timer, foco ativo
C_MUTED = "#6C7086"  # Overlay0: pending, cancelled, futuro
C_TEXT = "#CDD6F4"  # Text primary
C_SUBTEXT1 = "#BAC2DE"  # Subtext1: tasks 1-2 semanas
C_SUBTEXT0 = "#A6ADC8"  # Subtext0: tasks 2+ semanas
C_SURFACE = "#45475A"  # Surface borders

# =========================================================================
# Background colors (status a 15% sobre Base #1E1E2E)
# =========================================================================
BG_SUCCESS = "#323B3F"
BG_BELOW = "#3E3B48"
BG_ABOVE = "#3D3845"
BG_OVERLIMIT = "#3F343B"
BG_WARNING = "#3E3B41"
BG_ERROR = "#3D2E40"
BG_PASSIVE = "#3C3140"
BG_ACCENT = "#37324C"
BG_MUTED = "#292A3B"


def status_color(status: str, substatus: str | None = None) -> str:
    """Retorna cor hex para status/substatus conforme color-system.md."""
    if status == "done":
        return {
            "partial": C_BELOW,
            "overdone": C_ABOVE,
            "excessive": C_OVERLIMIT,
        }.get(substatus or "", C_SUCCESS)
    if status == "not_done":
        return {
            "justified": C_WARNING,
            "unjustified": C_ERROR,
            "ignored": C_PASSIVE,
        }.get(substatus or "", C_ERROR)
    if status == "running":
        return C_ACCENT
    if status == "paused":
        return C_WARNING
    return C_MUTED  # pending


def status_bg(status: str, substatus: str | None = None) -> str:
    """Retorna cor de background para fills na agenda."""
    if status == "done":
        return {
            "partial": BG_BELOW,
            "overdone": BG_ABOVE,
            "excessive": BG_OVERLIMIT,
        }.get(substatus or "", BG_SUCCESS)
    if status == "not_done":
        return {
            "justified": BG_WARNING,
            "unjustified": BG_ERROR,
            "ignored": BG_PASSIVE,
        }.get(substatus or "", BG_ERROR)
    if status == "running":
        return BG_ACCENT
    if status == "paused":
        return BG_WARNING
    return BG_MUTED


def status_icon(status: str, substatus: str | None = None) -> str:
    """Retorna ícone para status/substatus conforme color-system.md."""
    if status == "done":
        return {
            "partial": "✓~",
            "overdone": "✓+",
            "excessive": "✓!",
        }.get(substatus or "", "✓")
    if status == "not_done":
        return {
            "justified": "!",
            "unjustified": "✗!",
            "ignored": "✗?",
        }.get(substatus or "", "✗")
    if status == "running":
        return "▶"
    if status == "paused":
        return "⏸"
    return "·"  # pending


def status_label(status: str, substatus: str | None = None) -> str:
    """Retorna label textual para a agenda."""
    if status == "done":
        return {
            "partial": "partial",
            "overdone": "overdone",
            "excessive": "excessive",
        }.get(substatus or "", "done")
    if status == "not_done":
        return {
            "justified": "justified",
            "unjustified": "unjustified",
            "ignored": "ignored",
        }.get(substatus or "", "skip")
    if status == "running":
        return "running"
    if status == "paused":
        return "paused"
    return "pending"


def fill_char(status: str, substatus: str | None = None) -> str:
    """Retorna caractere de preenchimento do bloco na agenda."""
    if status == "running":
        return "▓"
    if status == "paused":
        return "▒"
    if status == "not_done":
        return "┄"
    return "░"  # done, pending


def fill_color(status: str, substatus: str | None = None) -> str:
    """Cor do preenchimento (mais escura que borda/título para contraste)."""
    if status == "running":
        return "#8B6EAC"  # Mauve escuro (~60% do #CBA6F7)
    if status == "paused":
        return "#B8A050"  # Yellow escuro (~60% do #F9E2AF)
    return status_color(status, substatus)


def status_bg_color(status: str, substatus: str | None = None) -> str:
    """Retorna cor de background (15% opacidade) para fills da agenda."""
    return status_bg(status, substatus)


def is_bold_status(status: str) -> bool:
    """Somente running e paused usam bold (color-system.md)."""
    return status in ("running", "paused")


def task_proximity_color(days: int | None) -> str:
    """Retorna cor de proximidade para tasks (heat de 7 faixas)."""
    if days is None:
        return C_MUTED
    if days <= 0:
        return C_WARNING
    if days == 1:
        return C_OVERLIMIT
    if days <= 3:
        return C_ABOVE
    if days <= 7:
        return C_BELOW
    if days <= 14:
        return C_SUBTEXT1
    if days <= 28:
        return C_SUBTEXT0
    return C_MUTED
