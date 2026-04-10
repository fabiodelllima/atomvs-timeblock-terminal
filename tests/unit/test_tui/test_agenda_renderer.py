"""Testes de caracterização para agenda_renderer.build_agenda_content.

Estes testes documentam o comportamento ATUAL do renderer (DT-074, issue #42).
Não são testes de validação de regra — são testes de caracterização no sentido
de Feathers (2004, cap. 13): codificam o que o código faz hoje para que
mudanças futuras sejam intencionais e visíveis.

Os assertivos abaixo representam o estado pré-fix do issue #34. Quando o fix
for aplicado na MR 2, estes testes vão falhar (RED) e serão atualizados para
refletir o novo comportamento esperado.

Cobertura atual:
    - Régua vertical │ na coluna de horas (a remover no #34)
    - Barra accent ▌ na linha do título (a remover no #34)
    - Ordem ícone/título no role start (a inverter no #34)

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
    """Caracteriza a régua vertical \u2502 na coluna de horas (a remover no #34)."""

    def test_hours_column_contains_vertical_ruler_on_label_lines(self) -> None:
        """Linhas com label de hora terminam com '[dim]\u2502[/dim]'.

        Estado atual (pré-fix #34): toda linha de hours_out termina com a
        régua vertical \u2502 envolvida em tag dim. Esta é a régua que o
        usuário vê separando a coluna de horas dos blocos.
        """
        instances = [_make_pending_instance("Foco", 600, 660)]  # 10:00-11:00

        hours_lines, _, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        ruler_lines = [line for line in hours_lines if "\u2502" in line]
        assert len(ruler_lines) > 0, "Esperado encontrar régua \u2502 em hours_out no estado atual"
        assert all("[dim]\u2502[/dim]" in line for line in ruler_lines), (
            "Régua deve estar envolvida em tag dim"
        )

    def test_hours_column_contains_vertical_ruler_on_blank_lines(self) -> None:
        """Linhas sem label de hora (15min/45min) também têm a régua.

        O renderer atual mantém a régua em todas as linhas para continuidade
        visual, não só nas linhas de :00 e :30.
        """
        instances = [_make_pending_instance("Foco", 600, 660)]

        hours_lines, _, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        # Linhas em branco (sem label) começam com 9 espaços antes da régua
        blank_with_ruler = [line for line in hours_lines if line.startswith("         [dim]\u2502")]
        assert len(blank_with_ruler) > 0, "Esperado linhas em branco com régua no estado atual"


class TestAgendaRendererCharacterizationAccentBar:
    """Caracteriza a barra accent \u258c no role start (a remover no #34)."""

    def test_pending_block_title_line_has_accent_bar(self) -> None:
        """Linha do título de bloco pending começa com \u258c colorido.

        Estado atual: role 'start' renderiza
            [color]\u258c[/color][C_TEXT]nome[/C_TEXT] [dim]\u00b7[/dim] [color]icon[/color]
        A barra \u258c (left half block) é o primeiro caractere da linha
        e é o que o #34 vai remover.
        """
        instances = [_make_pending_instance("Foco", 600, 660)]

        _, blocks_lines, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        title_line = next((line for line in blocks_lines if "Foco" in line), None)
        assert title_line is not None, "Linha de título não encontrada"
        # C_INFO = #89B4FA é a cor de pending
        assert "[#89B4FA]\u258c[/#89B4FA]" in title_line, (
            "Esperado \u258c colorido com C_INFO no início do título pending"
        )

    def test_running_block_title_line_has_bold_accent_bar(self) -> None:
        """Para running, a barra accent é bold (C_ACCENT = #CBA6F7)."""
        instances = [_make_running_instance("Atomvs TUI", 600, 750)]

        _, blocks_lines, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        title_line = next((line for line in blocks_lines if "Atomvs TUI" in line), None)
        assert title_line is not None
        assert "[bold #CBA6F7]\u258c[/bold #CBA6F7]" in title_line, (
            "Esperado \u258c bold com C_ACCENT no título de running"
        )


class TestAgendaRendererCharacterizationIconOrder:
    """Caracteriza a ordem título-antes-de-ícone (a inverter no #34)."""

    def test_title_appears_before_icon_in_pending_block(self) -> None:
        """No estado atual, o título vem antes do ícone separados por ' \u00b7 '.

        Layout atual:  \u258c<nome> \u00b7 <icon>
        Layout futuro: <icon> \u00b7 <nome>     (após fix #34)

        Este teste assegura a ordem ATUAL para detectarmos a inversão.
        """
        instances = [_make_pending_instance("Foco", 600, 660)]

        _, blocks_lines, _ = build_agenda_content(instances, now=FIXED_NOW_OUTSIDE)

        title_line = next((line for line in blocks_lines if "Foco" in line), None)
        assert title_line is not None

        # Limpa marcações Rich para obter texto visual aproximado
        import re

        clean = re.sub(r"\[/?[^\]]+\]", "", title_line)
        # No estado atual: ...Foco \u00b7 \u25cb...
        idx_name = clean.find("Foco")
        idx_dot = clean.find("\u00b7", idx_name)
        idx_icon = clean.find("\u25cb", idx_dot)  # \u25cb = ○ (pending icon)

        assert idx_name >= 0, "Nome não encontrado na linha limpa"
        assert idx_dot > idx_name, "Esperado separador \u00b7 após o nome"
        assert idx_icon > idx_dot, "Esperado ícone \u25cb após o separador"
