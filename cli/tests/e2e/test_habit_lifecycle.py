"""
E2E tests validando regras de negócio completas.

Este arquivo testa workflows end-to-end envolvendo múltiplas BRs.
Cada teste valida um fluxo completo de usuário.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
"""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.timeblock.main import app


@pytest.fixture
def isolated_db(tmp_path: Path) -> Path:
    """
    Cria banco de dados temporário isolado para E2E tests.
    
    Returns:
        Path para banco de dados temporário.
    """
    db_path = tmp_path / "test.db"
    return db_path


class TestBRHabitWorkflow:
    """
    E2E: Workflow completo de hábitos (BR-HABIT-001, BR-HABIT-002, BR-HABIT-003).
    
    Valida fluxo end-to-end: Criar → Gerar → Completar → Visualizar
    
    BRs cobertas:
    - BR-HABIT-001: Criação de hábitos
    - BR-HABIT-002: Geração de instâncias
    - BR-HABIT-003: Completar hábito
    """

    def test_br_habit_complete_daily_workflow(self, isolated_db: Path) -> None:
        """
        E2E: Usuário cria hábito diário, gera instâncias e marca completo.
        
        DADO: Sistema inicializado e limpo
        QUANDO: Usuário executa workflow completo de hábito diário
        ENTÃO: Sistema permite criar, gerar, completar e visualizar hábito
        E: Feedback visual de conclusão é exibido
        
        Referências:
            - BR-HABIT-001: Criação de hábitos em rotinas
            - BR-HABIT-002: Geração de instâncias de hábitos
            - BR-HABIT-003: Completar instância de hábito
        """
        runner = CliRunner()

        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0, "Sistema deve inicializar com sucesso"

        result = runner.invoke(app, [
            "habit", "create", "Meditação",
            "--start", "06:00",
            "--duration", "20",
            "--recurrence", "EVERYDAY"
        ])
        assert result.exit_code == 0, "Criação de hábito deve ter sucesso"
        assert "criado" in result.output.lower(), "Feedback de criação deve aparecer"

        result = runner.invoke(app, ["schedule", "generate", "--days", "7"])
        assert result.exit_code == 0, "Geração deve ter sucesso"
        assert "7" in result.output, "Deve gerar 7 instâncias (uma por dia)"

        result = runner.invoke(app, ["list", "today"])
        assert result.exit_code == 0, "Listagem deve ter sucesso"
        assert "Meditação" in result.output, "Hábito criado deve aparecer"
        assert "06:00" in result.output, "Horário deve estar correto"

        result = runner.invoke(app, ["habit", "complete", "1"])
        assert result.exit_code == 0, "Completar hábito deve ter sucesso"

        result = runner.invoke(app, ["list", "today"])
        assert result.exit_code == 0, "Listagem pós-conclusão deve ter sucesso"
        assert (
            "✓" in result.output
            or "COMPLETED" in result.output
            or "completo" in result.output.lower()
        ), "Deve mostrar indicador visual de conclusão"


class TestBREventConflictWorkflow:
    """
    E2E: Workflow de detecção e resolução de conflitos (BR-EVENT-001, BR-EVENT-002).
    
    Valida fluxo end-to-end: Criar conflito → Detectar → Propor solução
    
    BRs cobertas:
    - BR-EVENT-001: Detecção de conflitos de horário
    - BR-EVENT-002: Proposta de reorganização
    """

    def test_br_event_conflict_detection_and_resolution(self, isolated_db: Path) -> None:
        """
        E2E: Sistema detecta conflito de horários e propõe reorganização.
        
        DADO: Dois hábitos com horários sobrepostos
        QUANDO: Usuário ajusta horário causando conflito
        ENTÃO: Sistema detecta conflito e avisa usuário
        E: Sistema propõe solução de reorganização
        
        Referências:
            - BR-EVENT-001: Detecção de conflitos de horário
            - BR-EVENT-002: Proposta de reorganização automática
        """
        runner = CliRunner()
        runner.invoke(app, ["init"])

        runner.invoke(app, [
            "habit", "create", "Exercício",
            "--start", "09:00",
            "--duration", "60"
        ])

        runner.invoke(app, [
            "habit", "create", "Leitura",
            "--start", "09:30",
            "--duration", "60"
        ])

        runner.invoke(app, ["schedule", "generate", "--days", "1"])

        result = runner.invoke(app, [
            "habit", "adjust", "1",
            "--start", "09:00"
        ])

        assert (
            "conflito" in result.output.lower()
            or "overlap" in result.output.lower()
        ), "Sistema deve avisar sobre conflito detectado"

        assert (
            "proposta" in result.output.lower()
            or "reordering" in result.output.lower()
        ), "Sistema deve propor reorganização"
