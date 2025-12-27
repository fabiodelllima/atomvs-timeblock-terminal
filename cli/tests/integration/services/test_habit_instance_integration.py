"""
Integration tests - HabitInstanceService + EventReorderingService.

Testa integração entre HabitInstanceService e EventReorderingService,
validando ajustes de horário, detecção de conflitos e propostas de reorganização.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
    - Sprint 2.4: HabitInstance + EventReordering integration

TECHNICAL DEBT:
    Testes usam get_engine_context() que conecta ao banco de produção.
    Devem ser refatorados para usar fixtures isoladas (integration_session).

    Issue: Refatorar para usar fixtures em vez de get_engine_context()
"""

import pytest


class TestBRHabitInstanceReordering:
    """
    Integration: HabitInstanceService + EventReorderingService (BR-HABIT-REORDER-*).

    Valida ajuste de horários de instâncias de hábitos com detecção
    automática de conflitos e geração de propostas de reorganização.

    BRs cobertas:
    - BR-REORDER-001: Detecção de conflito (sobreposição temporal)
    - BR-REORDER-002: Escopo temporal (mesmo dia)
    - BR-REORDER-003: Apresentação de conflitos
    - BR-REORDER-004: Conflitos não bloqueiam
    - BR-REORDER-005: Persistência de conflitos (calculados dinamicamente)
    """

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_001_adjust_without_time_change(self) -> None:
        """
        Integration: Ajuste sem mudança de horário não dispara reordering.

        DADO: Instância de hábito com horário 08:00-09:00
        QUANDO: Usuário ajusta mantendo mesmo horário (08:00)
        ENTÃO: Instância é atualizada
        E: Nenhuma proposta de reordering é gerada (lista vazia)

        Referências:
            - BR-REORDER-001: Detecção de conflito
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_002_adjust_without_conflicts(self) -> None:
        """
        Integration: Ajuste de horário sem conflitos não gera conflitos.

        DADO: Instância de hábito com horário 08:00-09:00
        QUANDO: Usuário ajusta para horário livre (10:00-11:00)
        ENTÃO: Horário é atualizado
        E: Lista de conflitos está vazia

        Referências:
            - BR-REORDER-002: Escopo temporal
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_003_adjust_with_task_conflict(self) -> None:
        """
        Integration: Ajuste com conflito de task gera lista de conflitos.

        DADO: Instância de hábito 08:00-09:00 E task em 10:30
        QUANDO: Usuário ajusta hábito para 10:00-11:00 (conflita com task)
        ENTÃO: Horário é atualizado
        E: Lista de conflitos contém os eventos conflitantes

        Referências:
            - BR-REORDER-003: Apresentação de conflitos
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_004_adjust_nonexistent(self) -> None:
        """
        Integration: Ajuste de instância inexistente lança ValueError.

        DADO: ID 99999 que não existe no banco
        QUANDO: Usuário tenta ajustar horário
        ENTÃO: ValueError é lançada
        E: Sistema não retorna valores inválidos

        Referências:
            - BR-REORDER-004: Conflitos não bloqueiam
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_005_mark_completed(self) -> None:
        """
        Integration: Marcar instância como completa atualiza status.

        DADO: Instância de hábito pendente
        QUANDO: Usuário marca como completo
        ENTÃO: Status é atualizado para DONE
        E: Instância é persistida no banco

        Referências:
            - BR-REORDER-005: Persistência de conflitos
        """
        pass
