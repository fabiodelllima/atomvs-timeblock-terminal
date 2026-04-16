"""Testes de caracterização para agenda_renderer.build_agenda_content.

Estes testes documentam o comportamento ATUAL do renderer (DT-074, issue #42).
Não são testes de validação de regra — são testes de caracterização no sentido
de Feathers (2004, cap. 13): codificam o que o código faz hoje para que
mudanças futuras sejam intencionais e visíveis.

Cobertura atual (pós-v1.7.2):
    - Ausência de régua vertical │ na coluna de horas (#34 aplicado)
    - Ausência de barra accent ▌ na linha do título (#34, #40 aplicados)
    - Ícone antes do título no role start (#40 aplicado)
    - Prefixo · dim nas linhas de corpo (novo formato v1.7.2)

Cobertura futura (TODO no escopo do DT-074):
    - R10: linha do end_minutes ainda colorida
    - R12: title de bloco consecutivo substitui body do anterior
    - assign_columns: sobreposição com mais de 2 eventos no mesmo slot
    - compute_agenda_range: padding e clamps (já coberto por test_agenda_range)
    - Truncamento de nome longo com elipse \u2026

Referências:
    - FEATHERS, M. Working Effectively with Legacy Code, 2004, cap. 13
    - HUMBLE, J.; FARLEY, D. Continuous Delivery, 2010, p. 179
    - BR-TUI-032 (renderização de blocos contínuos)
    - DT-074 (issue #42 no GitLab)
"""

import re
from datetime import datetime

from timeblock.tui.widgets.agenda_renderer import build_agenda_content

# Constante: hora fixa fora de qualquer bloco para evitar marcação de "agora"
# nos testes que não dependem dela. 04:00 está antes do range default 05:00.
FIXED_NOW_OUTSIDE = datetime(2026, 4, 10, 4, 0, 0)


def _make_pending_instance(
    name: str,
    start_minutes: int,
    end_minutes: int,
) -> dict:
    """Cria um dict de instância pending com os campos mínimos esperados.

    Os campos seguem o contrato implícito que build_agenda_content consome:
    name, start_minutes, end_minutes, status, substatus.
    """
    return {
        "name": name,
        "start_minutes": start_minutes,
        "end_minutes": end_minutes,
        "status": "pending",
        "substatus": None,
    }


def _make_running_instance(
    name: str,
    start_minutes: int,
    end_minutes: int,
) -> dict:
    """Cria um dict de instância running (caso bold do renderer)."""
    return {
        "name": name,
        "start_minutes": start_minutes,
        "end_minutes": end_minutes,
        "status": "running",
        "substatus": None,
    }


class TestAgendaRendererCharacterizationRuler:
    """Caracteriza a AUSÊNCIA de régua vertical \u2502 na coluna de horas (pós-#34)."""

    def test_hours_column_has_no_vertical_ruler(self) -> None:
        """Pós-v1.7.2: régua vertical \u2502 foi removida da coluna de horas.

        Nenhuma linha de hours_out deve conter o caractere \u2502.
        Se este teste falhar, algo reintroduziu a régua.
        """
        instances = [_make_pending_instance("Foco", 600, 660)]  # 10:00-11:00

        hours_lines, _, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        ruler_lines = [line for line in hours_lines if "\u2502" in line]
        assert len(ruler_lines) == 0, (
            f"Régua \u2502 encontrada em {len(ruler_lines)} linhas — deveria ter sido removida (#34)"
        )


class TestAgendaRendererCharacterizationTitleFormat:
    """Caracteriza o formato da linha de título pós-v1.7.2."""

    def test_pending_block_title_has_icon_before_name(self) -> None:
        """Pós-v1.7.2: formato é `{ícone} {nome}` sem accent bar.

        O ícone de pending (\u25cb) aparece antes do nome, separados por espaço.
        Não há accent bar \u258c.
        """
        instances = [_make_pending_instance("Foco", 600, 660)]

        _, blocks_lines, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        title_line = next((line for line in blocks_lines if "Foco" in line), None)
        assert title_line is not None, "Linha de título não encontrada"

        # Sem accent bar
        assert "\u258c" not in title_line, "Accent bar \u258c deveria ter sido removida (#34)"

        # Ícone de pending presente
        assert "\u25cb" in title_line, "Ícone de pending \u25cb ausente"

        # C_TEXT para o nome
        assert "#CDD6F4" in title_line, "C_TEXT ausente — título deveria ser branco"

        # Ícone antes do nome na string limpa
        clean = re.sub(r"\[/?[^\]]+\]", "", title_line)
        idx_icon = clean.find("\u25cb")
        idx_name = clean.find("Foco")
        assert idx_icon < idx_name, "Ícone deveria aparecer antes do nome (pós-#40)"

    def test_running_block_title_has_bold_icon_before_name(self) -> None:
        """Para running, ícone e nome são bold. Sem accent bar."""
        instances = [_make_running_instance("Atomvs TUI", 600, 750)]

        _, blocks_lines, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        title_line = next((line for line in blocks_lines if "Atomvs TUI" in line), None)
        assert title_line is not None

        # Sem accent bar
        assert "\u258c" not in title_line, "Accent bar \u258c deveria ter sido removida"

        # Bold com C_ACCENT para running
        assert "bold #CBA6F7" in title_line, "Esperado bold C_ACCENT no título running"

        # Ícone ▶ presente
        assert "\u25b6" in title_line, "Ícone \u25b6 de running ausente"


class TestAgendaRendererCharacterizationBody:
    """Caracteriza o formato das linhas de corpo pós-v1.7.2."""

    def test_body_line_has_dot_prefix_and_fill(self) -> None:
        """Pós-v1.7.2: corpo é `· {fill}` com · em dim e fill na cor do status.

        Não há accent bar \u258c. O prefixo é \u00b7 (ponto medial) em [dim].
        """
        instances = [_make_pending_instance("Foco", 600, 660)]

        _, blocks_lines, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        # Linhas de corpo: não contêm "Foco" (título) mas contêm fill
        body_lines = [line for line in blocks_lines if "\u2591" in line and "Foco" not in line]
        assert len(body_lines) > 0, "Nenhuma linha de corpo encontrada"

        for line in body_lines:
            assert "\u258c" not in line, "Accent bar \u258c deveria ter sido removida do corpo"
            assert "[dim]\u00b7[/dim]" in line, "Prefixo \u00b7 dim ausente no corpo"
            assert "\u2591" in line, "Fill char \u2591 ausente no corpo"
