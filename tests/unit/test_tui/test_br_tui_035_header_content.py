"""Testes da BR-TUI-035 — Conteúdo interno do HeaderBar.

Valida as funções puras de header_renderer.py contra as
24 regras da BR-TUI-035 (br-tui.md).

Referências:
    - BR-TUI-035 em docs/reference/business-rules/br-tui.md
    - ADR-052 (Redesign do conteúdo interno do HeaderBar)
    - Issue #52
"""

import re

from timeblock.tui.widgets.header_renderer import (
    C_INFO,
    C_SUCCESS,
    build_habits_progress,
    build_header_content,
    build_next_item,
    build_tasks_progress,
    truncate_next_name,
)


def _strip_markup(text: str) -> str:
    """Remove tags Rich para inspeção de texto puro."""
    return re.sub(r"\[.*?\]", "", text)


class TestBRTUI035HabitsProgress:
    """Valida seção 1: progresso semanal de hábitos (regras 1-5)."""

    def test_br_tui_035_habits_progress_format(self) -> None:
        """Regras 1-3: formato `Hábitos X/Y ▪▪▪▪▪▪░░░░ ZZ%`."""
        result = build_habits_progress(42, 70)
        clean = _strip_markup(result)

        assert "Hábitos 42/70" in clean
        assert "60%" in clean
        # Barra: 6 preenchidos + 4 vazios = 10
        assert "▪▪▪▪▪▪░░░░" in clean

    def test_br_tui_035_habits_progress_color_success(self) -> None:
        """Regra 5: cor C_SUCCESS quando >= 90%."""
        result = build_habits_progress(9, 10)
        assert C_SUCCESS in result

    def test_br_tui_035_habits_progress_color_info(self) -> None:
        """Regra 5: cor C_INFO quando < 90%."""
        result = build_habits_progress(5, 10)
        assert C_INFO in result

    def test_br_tui_035_habits_progress_no_routine(self) -> None:
        """Regra 4: sem rotina ativa mostra dim placeholder."""
        result = build_habits_progress(0, 0)
        assert "[dim]" in result
        assert "Hábitos --/--" in _strip_markup(result)
        # Sem barra nem percentual
        assert "▪" not in result
        assert "░" not in result
        assert "%" not in _strip_markup(result)

    def test_br_tui_035_habits_progress_100_percent(self) -> None:
        """Barra cheia com 100%."""
        result = build_habits_progress(70, 70)
        clean = _strip_markup(result)
        assert "▪▪▪▪▪▪▪▪▪▪" in clean
        assert "100%" in clean
        assert C_SUCCESS in result

    def test_br_tui_035_habits_progress_0_percent(self) -> None:
        """Barra vazia com 0% (rotina existe mas nada feito)."""
        result = build_habits_progress(0, 70)
        clean = _strip_markup(result)
        assert "░░░░░░░░░░" in clean
        assert "0%" in clean


class TestBRTUI035TasksProgress:
    """Valida seção 2: progresso de tarefas do dia (regras 6-10)."""

    def test_br_tui_035_tasks_progress_format(self) -> None:
        """Regras 6-7: formato `Tarefas X/Y ▪▪▪░░ ZZ%`."""
        result = build_tasks_progress(3, 5)
        clean = _strip_markup(result)

        assert "Tarefas 3/5" in clean
        assert "60%" in clean
        assert "▪▪▪░░" in clean

    def test_br_tui_035_tasks_progress_no_tasks(self) -> None:
        """Regra 8: sem tarefas mostra dim placeholder."""
        result = build_tasks_progress(0, 0)
        assert "[dim]" in result
        assert "Sem tarefas" in _strip_markup(result)

    def test_br_tui_035_tasks_progress_all_done(self) -> None:
        """Regra 9: todas concluídas usa C_SUCCESS."""
        result = build_tasks_progress(5, 5)
        assert C_SUCCESS in result
        assert "▪▪▪▪▪" in _strip_markup(result)
        assert "100%" in _strip_markup(result)


class TestBRTUI035NextItem:
    """Valida seção 3: próximo item (regras 11-17)."""

    def test_br_tui_035_next_item_habit(self) -> None:
        """Regras 11-12: hábito próximo com countdown < 60min."""
        result = build_next_item("Gym", 25)
        assert "Próximo: Gym em 25min" in result

    def test_br_tui_035_next_item_task(self) -> None:
        """Regras 11-12: tarefa próxima com countdown >= 60min."""
        result = build_next_item("Relatório Q1", 75)
        assert "Próximo: Relatório Q1 em 1h15" in result

    def test_br_tui_035_next_item_exact_hour(self) -> None:
        """Countdown de hora exata sem minutos residuais."""
        result = build_next_item("Almoço", 120)
        assert "Próximo: Almoço em 2h" in result

    def test_br_tui_035_next_item_none(self) -> None:
        """Regra 17: sem próximos mostra dim placeholder."""
        result = build_next_item(None, None)
        assert "[dim]" in result
        assert "Sem próximos hoje" in _strip_markup(result)

    def test_br_tui_035_next_item_truncate(self) -> None:
        """Regra 16: nome longo truncado com reticências."""
        name = truncate_next_name("Relatório Trimestral de Vendas Q1", 15)
        assert name.endswith("\u2026")
        assert len(name) <= 15


class TestBRTUI035HeaderContent:
    """Valida layout e responsividade (regras 18-24)."""

    def test_br_tui_035_responsive_full(self) -> None:
        """Regra 18-19: todas as 3 seções em viewport >= 80."""
        habits = build_habits_progress(42, 70)
        tasks = build_tasks_progress(3, 5)
        next_item = build_next_item("Gym", 25)

        result = build_header_content(habits, tasks, next_item, 120)
        clean = _strip_markup(result)

        assert "Hábitos 42/70" in clean
        assert "Tarefas 3/5" in clean
        assert "Próximo: Gym" in clean
        # Separadores
        assert result.count("│") >= 2

    def test_br_tui_035_responsive_collapse_80(self) -> None:
        """Regra 20: viewport < 80 colapsa seção 3 (Próximo)."""
        habits = build_habits_progress(42, 70)
        tasks = build_tasks_progress(3, 5)
        next_item = build_next_item("Gym", 25)

        result = build_header_content(habits, tasks, next_item, 75)
        clean = _strip_markup(result)

        assert "Hábitos" in clean
        assert "Tarefas" in clean
        assert "Próximo" not in clean

    def test_br_tui_035_responsive_collapse_60(self) -> None:
        """Regra 21: viewport < 60 colapsa seções 2 e 3."""
        habits = build_habits_progress(42, 70)
        tasks = build_tasks_progress(3, 5)
        next_item = build_next_item("Gym", 25)

        result = build_header_content(habits, tasks, next_item, 55)
        clean = _strip_markup(result)

        assert "Hábitos" in clean
        assert "Tarefas" not in clean
        assert "Próximo" not in clean

    def test_br_tui_035_no_routine_name_in_content(self) -> None:
        """Regra 22: nome da rotina NÃO aparece no conteúdo interno."""
        habits = build_habits_progress(42, 70)
        tasks = build_tasks_progress(3, 5)
        next_item = build_next_item("Gym", 25)

        result = build_header_content(habits, tasks, next_item, 120)

        # Nenhuma das funções de render inclui nome de rotina
        assert "Rotina" not in _strip_markup(result)
        assert "Matinal" not in _strip_markup(result)

    def test_br_tui_035_no_timer_in_content(self) -> None:
        """Regra 23: timer NÃO aparece no conteúdo interno."""
        habits = build_habits_progress(42, 70)
        tasks = build_tasks_progress(3, 5)
        next_item = build_next_item("Gym", 25)

        result = build_header_content(habits, tasks, next_item, 120)
        clean = _strip_markup(result)

        assert "⏹" not in clean
        assert "--:--" not in clean
        assert "timer" not in clean.lower()
