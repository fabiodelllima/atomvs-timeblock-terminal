"""
Integration tests - TaskService + EventReorderingService.

Testa integração entre TaskService e EventReorderingService,
validando atualizações de tasks, detecção de conflitos e propostas.

Referências:
    - ADR-019: Test Naming Convention
    - RTM: Requirements Traceability Matrix
    - Sprint 2.2: Task + EventReordering integration

TECHNICAL DEBT:
    Testes usam get_engine_context() que conecta ao banco de produção.
    Devem ser refatorados para usar fixtures isoladas (integration_session).

    Issue: Refatorar para usar fixtures em vez de get_engine_context()
"""

import pytest


class TestBRTaskReordering:
    """
    Integration: TaskService + EventReorderingService (BR-TASK-REORDER-*).

    Valida atualização de tasks com detecção automática de conflitos
    e geração de propostas de reorganização.

    BRs cobertas:
    - BR-REORDER-001: Detecção de conflito (sobreposição temporal)
    - BR-REORDER-002: Escopo temporal (mesmo dia)
    - BR-REORDER-003: Apresentação de conflitos
    - BR-REORDER-004: Conflitos não bloqueiam
    - BR-REORDER-005: Persistência de conflitos (calculados dinamicamente)
    - BR-REORDER-006: Algoritmo de reordenamento (futuro)
    """

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_001_update_without_time_change(self) -> None:
        """
        Integration: Atualização sem mudança de horário não dispara reordering.

        DADO: Task existente com horário definido
        QUANDO: Usuário atualiza apenas título/descrição
        ENTÃO: Campos são atualizados
        E: Nenhuma proposta é gerada

        Referências:
            - BR-REORDER-001: Detecção de conflito
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_002_update_without_conflicts(self) -> None:
        """
        Integration: Mudança de horário sem conflitos não gera proposta.

        DADO: Task existente
        QUANDO: Usuário muda horário para slot livre
        ENTÃO: Horário é atualizado
        E: Nenhum conflito é detectado

        Referências:
            - BR-REORDER-002: Escopo temporal
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_003_update_with_task_conflict(self) -> None:
        """
        Integration: Mudança causando conflito com outra task gera proposta.

        DADO: Duas tasks em horários diferentes
        QUANDO: Usuário move task1 para horário de task2
        ENTÃO: Horário é atualizado
        E: Conflito é detectado

        Referências:
            - BR-REORDER-003: Apresentação de conflitos
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_004_update_conflicts_with_habit(self) -> None:
        """
        Integration: Task conflitando com HabitInstance gera proposta.

        DADO: HabitInstance em horário definido
        QUANDO: Usuário move task para mesmo horário
        ENTÃO: Conflito é detectado

        Referências:
            - BR-REORDER-004: Conflitos não bloqueiam
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_005_update_nonexistent(self) -> None:
        """
        Integration: Atualização de task inexistente retorna (None, None).

        DADO: ID 99999 que não existe
        QUANDO: Usuário tenta atualizar
        ENTÃO: Retorna (None, None)
        E: Sistema não trava

        Referências:
            - BR-REORDER-005: Persistência de conflitos
        """
        pass

    @pytest.mark.skip(reason="Refatorar: usar fixtures em vez de get_engine_context()")
    def test_br_reorder_006_update_same_time(self) -> None:
        """
        Integration: Atualização para mesmo horário não dispara reordering.

        DADO: Task com horário definido
        QUANDO: Usuário "atualiza" para mesmo horário
        ENTÃO: Horário permanece igual
        E: Nenhuma proposta é gerada

        Referências:
            - BR-REORDER-006: Algoritmo de reordenamento
        """
        pass
