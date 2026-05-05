"""Funções puras de renderização do HeaderBar (Humble Object).

Lógica de formatação extraída de HeaderBar para permitir
testes unitários sem instanciar widgets Textual.

Referências:
    - HUMBLE; FARLEY, 2010, p. 179 (Humble Object Pattern)
    - BR-TUI-035: Conteúdo interno do HeaderBar
    - ADR-052: Redesign do conteúdo interno do HeaderBar
"""

import re

from timeblock.tui.colors import C_INFO, C_SUCCESS


def build_habits_progress(done: int, total: int) -> str:
    """Formata progresso semanal de hábitos (BR-TUI-035 regras 1-5).

    Args:
        done: instâncias DONE na semana corrente.
        total: total esperado (hábitos ativos x dias transcorridos).

    Returns:
        Markup Rich formatado. Ex: `Hábitos 42/70 ▪▪▪▪▪▪░░░░ 60%`
    """
    if total <= 0:
        return "[dim]Hábitos --/--[/dim]"

    pct = min(100, round(done * 100 / total))
    filled = round(pct / 10)
    bar = "▪" * filled + "░" * (10 - filled)
    color = C_SUCCESS if pct >= 90 else C_INFO

    return f"Hábitos {done}/{total} [{color}]{bar}[/{color}] {pct}%"


def build_tasks_progress(completed: int, total: int) -> str:
    """Formata progresso de tarefas do dia (BR-TUI-035 regras 6-10).

    Args:
        completed: tarefas concluídas hoje.
        total: total de tarefas com deadline hoje ou pendentes sem deadline.

    Returns:
        Markup Rich formatado. Ex: `Tarefas 3/5 ▪▪▪░░ 60%`
    """
    if total <= 0:
        return "[dim]Sem tarefas[/dim]"

    pct = min(100, round(completed * 100 / total))
    filled = round(pct * 5 / 100)
    bar = "▪" * filled + "░" * (5 - filled)
    color = C_SUCCESS if pct >= 90 else C_INFO

    return f"Tarefas {completed}/{total} [{color}]{bar}[/{color}] {pct}%"


def build_next_item(name: str | None, minutes_until: int | None) -> str:
    """Formata próximo item pendente (BR-TUI-035 regras 11-17).

    Args:
        name: nome do hábito ou tarefa. None se sem próximo.
        minutes_until: minutos até o início. None se sem próximo.

    Returns:
        Markup Rich formatado. Ex: `Próximo: Gym em 1h15`
    """
    if name is None or minutes_until is None:
        return "[dim]Sem próximos hoje[/dim]"

    if minutes_until < 60:
        countdown = f"em {minutes_until}min"
    else:
        hours = minutes_until // 60
        mins = minutes_until % 60
        countdown = f"em {hours}h{mins:02d}" if mins > 0 else f"em {hours}h"

    return f"Próximo: {name} {countdown}"


def truncate_next_name(name: str, max_width: int) -> str:
    """Trunca nome do próximo item com reticências (BR-TUI-035 regra 16).

    Args:
        name: nome original.
        max_width: largura máxima em caracteres.

    Returns:
        Nome truncado ou original se cabe.
    """
    if len(name) <= max_width:
        return name
    return name[: max(1, max_width - 1)] + "\u2026"


def _plain_len(text: str) -> int:
    """Calcula comprimento visível ignorando markup Rich."""
    return len(re.sub(r"\[.*?\]", "", text))


def build_header_content(
    habits: str,
    tasks: str,
    next_item: str,
    available_width: int,
) -> str:
    """Monta conteúdo interno do HeaderBar (BR-TUI-035 regras 18-24).

    Aplica colapso responsivo:
    - < 80 colunas: seção 3 (Próximo) colapsa.
    - < 60 colunas: seção 2 (Tarefas) também colapsa.

    Args:
        habits: saída de build_habits_progress.
        tasks: saída de build_tasks_progress.
        next_item: saída de build_next_item.
        available_width: largura interna disponível em colunas.

    Returns:
        Markup Rich com as seções separadas por │ dim.
    """
    separator = "  [dim]│[/dim]  "

    if available_width < 60:
        sections = [habits]
    elif available_width < 80:
        sections = [habits, tasks]
    else:
        sections = [habits, tasks, next_item]

    content = separator.join(sections)

    content_len = _plain_len(content)
    pad = max(0, available_width - content_len - 2)

    return f" {content}{' ' * pad} "
