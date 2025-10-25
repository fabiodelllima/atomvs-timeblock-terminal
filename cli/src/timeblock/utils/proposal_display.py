"""Helper para exibição de propostas de reordenamento."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from typing import Optional
from datetime import datetime

from timeblock.services.event_reordering_models import (
    ReorderingProposal,
    ConflictSeverity
)


def display_proposal(proposal: Optional[ReorderingProposal]) -> None:
    """
    Exibe proposta de reordenamento formatada.
    
    Args:
        proposal: Proposta a exibir (None = sem conflitos)
    """
    if not proposal:
        return
        
    console = Console()
    
    # Header
    console.print("\n[yellow]⚠ CONFLITO DE AGENDA DETECTADO[/yellow]\n")
    
    # Tabela de conflitos
    table = Table(title="Eventos em Conflito")
    table.add_column("Evento", style="cyan")
    table.add_column("Horário Original", style="white")
    table.add_column("Horário Proposto", style="green")
    table.add_column("Severidade", style="yellow")
    
    severity_symbols = {
        ConflictSeverity.MINOR: "✓",
        ConflictSeverity.MODERATE: "!",
        ConflictSeverity.MAJOR: "✗"
    }
    
    for adjustment in proposal.adjustments:
        symbol = severity_symbols.get(adjustment.conflict.severity, "?")
        
        table.add_row(
            adjustment.event_name,
            f"{_format_time(adjustment.original_start)} → {_format_time(adjustment.original_end)}",
            f"{_format_time(adjustment.proposed_start)} → {_format_time(adjustment.proposed_end)}",
            f"{symbol} {adjustment.conflict.severity.value}"
        )
    
    console.print(table)
    
    # Estatísticas
    stats = Panel(
        f"[bold]Total:[/bold] {len(proposal.adjustments)} eventos\n"
        f"[bold]Janela:[/bold] {_format_time(proposal.time_window_start)} - {_format_time(proposal.time_window_end)}",
        title="Resumo",
        border_style="blue"
    )
    console.print(stats)


def confirm_apply_proposal() -> bool:
    """
    Pergunta se usuário quer aplicar proposta.
    
    Returns:
        True se usuário aceitar
    """
    return Confirm.ask(
        "\n[bold]Aplicar reordenamento automático?[/bold]",
        default=False
    )


def _format_time(dt: datetime) -> str:
    """Formata datetime para exibição (HH:MM)."""
    return dt.strftime("%H:%M")
