"""Testes de caracterização para TasksPanel._order_tasks.

Estes testes documentam o comportamento ATUAL do método _order_tasks
(DT-074, issue #42). São testes de caracterização no sentido de Feathers
(2004, cap. 13): codificam o que o código faz hoje para que o gap entre
a BR-TUI-003-R20 e a implementação seja visível e mensurável.

Estado documentado pela BR-TUI-003-R20 (br-tui.md, linha 545):
    1. Grupo 1 (topo):  overdue,   por data ascendente
    2. Grupo 2:         pending,   por proximidade ascendente
    3. Grupo 3 (final): completed, por data de conclusão descendente
    4. Grupo 4 (final): cancelled, por data descendente

Estado real do _order_tasks (tasks_panel.py):
    Ordena APENAS por status, sem considerar tempo dentro de cada grupo.
    A ordenação por proximidade existe parcialmente no loader.load_tasks
    via key=lambda t: (0 if status==overdue else 1, t["days"]), mas em
    granularidade de DIAS — tasks no mesmo dia em horários diferentes
    ficam empatadas e o desempate cai na ordem natural da query, que
    NÃO ordena por scheduled_datetime (task_service.list_pending_tasks
    não tem .order_by).

Os 4 testes nomeados na BR-TUI-003-R20 nunca foram escritos:
    - test_br_tui_003_r20_overdue_first
    - test_br_tui_003_r20_pending_by_proximity
    - test_br_tui_003_r20_done_after_pending
    - test_br_tui_003_r20_cancelled_last

A MR 2 desta sessão (issue #42 a criar) vai implementá-los corretamente
e estes testes de caracterização serão atualizados ou substituídos.

Estratégia de instanciação:
    TasksPanel herda de FocusablePanel (Textual Widget). Instanciar via
    __init__ exige App rodando. Como _order_tasks só lê self._tasks e
    escreve self._ordered, usamos object.__new__ para criar uma instância
    sem invocar __init__ e atribuímos os atributos manualmente.

Referências:
    - FEATHERS, M. Working Effectively with Legacy Code, 2004, cap. 13
    - BR-TUI-003-R20 em docs/reference/business-rules/br-tui.md
    - DT-074 (issue #42 no GitLab)
"""

from timeblock.tui.widgets.tasks_panel import TasksPanel


def _make_panel_with_tasks(tasks: list[dict]) -> TasksPanel:
    """Cria TasksPanel sem invocar __init__ e injeta tasks.

    Evita dependência de App Textual. Suficiente porque _order_tasks
    é puro sobre self._tasks/self._ordered.
    """
    panel = object.__new__(TasksPanel)
    panel._tasks = tasks
    panel._ordered = []
    return panel


def _make_task(
    task_id: int,
    name: str,
    status: str,
    days: int,
    time: str = "--:--",
) -> dict:
    """Cria dict no formato que loader._build_task_dict produz hoje.

    Campos: id, name, proximity, date, time, status, days.
    Apenas os relevantes para _order_tasks são significativos
    (status e days). Outros existem para realismo da fixture.
    """
    return {
        "id": task_id,
        "name": name,
        "proximity": "Hoje" if days == 0 else f"{days}d",
        "date": "10/04",
        "time": time,
        "status": status,
        "days": days,
    }


class TestOrderTasksCharacterizationStatusGrouping:
    """Caracteriza o agrupamento por status (parcialmente correto)."""

    def test_overdue_comes_before_pending(self) -> None:
        """Estado atual: overdue antes de pending. Coerente com R20 grupo 1-2."""
        tasks = [
            _make_task(1, "Pendente", "pending", days=1),
            _make_task(2, "Atrasada", "overdue", days=-2),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        assert [t["id"] for t in panel._ordered] == [2, 1]

    def test_completed_and_cancelled_at_end(self) -> None:
        """Estado atual: completed e cancelled vão para o final.

        Coerente com R20 grupos 3-4. Ordem entre completed e cancelled
        no estado atual: completed antes de cancelled (pelo dict order).
        """
        tasks = [
            _make_task(1, "Cancelada", "cancelled", days=0),
            _make_task(2, "Pendente", "pending", days=1),
            _make_task(3, "Concluída", "completed", days=0),
            _make_task(4, "Atrasada", "overdue", days=-1),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        statuses = [t["status"] for t in panel._ordered]
        assert statuses == ["overdue", "pending", "completed", "cancelled"]


class TestOrderTasksCharacterizationTimeOrderingBug:
    """Documenta o BUG da ausência de ordenação por tempo intra-grupo."""

    def test_pending_tasks_same_day_keep_insertion_order_not_time(self) -> None:
        """BUG: pendings no mesmo dia não são ordenadas por horário.

        Three pendings com days=0 mas horários diferentes. A R20 exige
        ordenação por proximidade ascendente (08:00 antes de 14:00 antes
        de 20:00). O _order_tasks atual ignora tempo e preserva ordem
        de inserção (sorted estável + chave constante por status).

        Entrada: [20:00, 08:00, 14:00]
        Esperado pela R20: [08:00, 14:00, 20:00]
        Estado atual:      [20:00, 08:00, 14:00]  (ordem de inserção)
        """
        tasks = [
            _make_task(1, "Tarde", "pending", days=0, time="20:00"),
            _make_task(2, "Manhã", "pending", days=0, time="08:00"),
            _make_task(3, "Tarde-meio", "pending", days=0, time="14:00"),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        # Caracterização do bug: ordem de inserção é preservada
        assert [t["id"] for t in panel._ordered] == [1, 2, 3]
        # E NÃO a ordem cronológica esperada pela R20:
        assert [t["id"] for t in panel._ordered] != [2, 3, 1]

    def test_overdue_tasks_keep_insertion_order_not_severity(self) -> None:
        """BUG: overdues não são ordenadas por gravidade do atraso.

        A R20 exige overdue por data ascendente (mais atrasada primeiro).
        Estado atual ignora 'days' negativo e preserva ordem de inserção.

        Entrada: [days=-1, days=-7, days=-3]
        Esperado pela R20: [days=-7, days=-3, days=-1]
        Estado atual:      [days=-1, days=-7, days=-3]
        """
        tasks = [
            _make_task(1, "Ontem", "overdue", days=-1),
            _make_task(2, "Semana passada", "overdue", days=-7),
            _make_task(3, "Três dias atrás", "overdue", days=-3),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        assert [t["id"] for t in panel._ordered] == [1, 2, 3]
        assert [t["id"] for t in panel._ordered] != [2, 3, 1]
