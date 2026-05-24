"""Testes do TasksPanel._order_tasks contra BR-TUI-003-R20.

A BR especifica quatro grupos com ordenação determinada:
    1. Grupo 1: overdue,   por sort_key ascendente  (mais atrasada primeiro)
    2. Grupo 2: pending,   por sort_key ascendente  (mais próxima primeiro)
    3. Grupo 3: completed, por sort_key descendente (mais recente primeiro)
    4. Grupo 4: cancelled, por sort_key descendente (mais recente primeiro)

Estratégia de instanciação:
    TasksPanel herda de FocusablePanel (Textual Widget). Instanciar via
    __init__ exige App rodando. Como _order_tasks só lê self._tasks e
    escreve self._ordered, usamos object.__new__ para criar uma instância
    sem invocar __init__ e atribuímos os atributos manualmente.

Referências:
    - BR-TUI-003-R20 em docs/reference/business-rules/br-tui.md
    - Issue #43 (fix de 3 camadas); MR !78 (caracterização original).
"""

from datetime import datetime, timedelta

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
    sort_key: datetime | None = None,
) -> dict:
    """Cria dict no formato que loader._build_task_dict produz hoje.

    Campos: id, name, proximity, date, time, status, days, sort_key.
    Apenas os relevantes para _order_tasks são significativos
    (status, days, sort_key). Outros existem para realismo da fixture.

    sort_key é opcional. Os smoke tests de agrupamento não precisam dele
    (caem no fallback e a ordem intra-bucket é estável). Os testes da
    BR-TUI-003-R20 sempre passam sort_key explicitamente.
    """
    return {
        "id": task_id,
        "name": name,
        "proximity": "Hoje" if days == 0 else f"{days}d",
        "date": "10/04",
        "time": time,
        "status": status,
        "days": days,
        "sort_key": sort_key,
    }


class TestOrderTasksStatusGrouping:
    """Smoke tests de agrupamento por status (BR-TUI-003-R20, eixo bucket).

    Verifica que os quatro buckets aparecem na ordem certa
    (overdue, pending, completed, cancelled), independente da
    ordenação intra-grupo (essa é coberta por TestBRTUI003R20Ordering).
    """

    def test_overdue_comes_before_pending(self) -> None:
        """Overdue antes de pending (R20 grupos 1-2)."""
        tasks = [
            _make_task(1, "Pendente", "pending", days=1),
            _make_task(2, "Atrasada", "overdue", days=-2),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        assert [t["id"] for t in panel._ordered] == [2, 1]

    def test_completed_and_cancelled_at_end(self) -> None:
        """Completed e cancelled vão para o final (R20 grupos 3-4)."""
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


class TestBRTUI003R20Ordering:
    """Testes da BR-TUI-003-R20: ordenação esperada do TasksPanel.

    Estado-alvo. Estes testes falham contra a implementação atual
    (que ignora horário intra-grupo) e devem passar após o fix:

    1. Grupo 1: overdue,   ordem ascendente  por sort_key (mais atrasada primeiro)
    2. Grupo 2: pending,   ordem ascendente  por sort_key (mais próxima primeiro)
    3. Grupo 3: completed, ordem descendente por sort_key (mais recente primeiro)
    4. Grupo 4: cancelled, ordem descendente por sort_key (mais recente primeiro)
    """

    def test_br_tui_003_r20_overdue_first(self) -> None:
        """Overdue vem antes de pending; intra-grupo ordena por sort_key ascendente.

        Três overdues atrasadas em 1d, 7d e 3d. Esperado: 7d, 3d, 1d
        (mais atrasada primeiro). Mais uma pending para validar que o grupo
        overdue inteiro precede o grupo pending.
        """
        now = datetime(2026, 5, 24, 12, 0)
        tasks = [
            _make_task(
                1,
                "Pendente amanhã",
                "pending",
                days=1,
                sort_key=now + timedelta(days=1),
            ),
            _make_task(
                2,
                "Atrasada ontem",
                "overdue",
                days=-1,
                sort_key=now - timedelta(days=1),
            ),
            _make_task(
                3,
                "Atrasada semana",
                "overdue",
                days=-7,
                sort_key=now - timedelta(days=7),
            ),
            _make_task(
                4,
                "Atrasada 3d",
                "overdue",
                days=-3,
                sort_key=now - timedelta(days=3),
            ),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        # Overdues primeiro, da mais antiga (-7d) para a mais recente (-1d);
        # pending por último.
        assert [t["id"] for t in panel._ordered] == [3, 4, 2, 1]

    def test_br_tui_003_r20_pending_by_proximity(self) -> None:
        """Pendings no mesmo dia ordenam por horário ascendente.

        Três pendings em days=0 com horários 20:00, 08:00, 14:00. Esperado:
        08:00, 14:00, 20:00 (proximidade ascendente — mais próximo do
        início do dia primeiro).
        """
        base = datetime(2026, 5, 24)
        tasks = [
            _make_task(
                1,
                "Tarde",
                "pending",
                days=0,
                time="20:00",
                sort_key=base.replace(hour=20),
            ),
            _make_task(
                2,
                "Manhã",
                "pending",
                days=0,
                time="08:00",
                sort_key=base.replace(hour=8),
            ),
            _make_task(
                3,
                "Meio",
                "pending",
                days=0,
                time="14:00",
                sort_key=base.replace(hour=14),
            ),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        assert [t["id"] for t in panel._ordered] == [2, 3, 1]

    def test_br_tui_003_r20_done_after_pending(self) -> None:
        """Completed vem após pending; intra-grupo ordena por sort_key descendente.

        Pending + dois completed (concluídos há 1h e 12h). Esperado: pending
        primeiro, depois completed mais recente (1h), depois completed mais
        antigo (12h).
        """
        now = datetime(2026, 5, 24, 12, 0)
        tasks = [
            _make_task(
                1,
                "Concluída 12h",
                "completed",
                days=0,
                sort_key=now - timedelta(hours=12),
            ),
            _make_task(
                2,
                "Pendente",
                "pending",
                days=1,
                sort_key=now + timedelta(days=1),
            ),
            _make_task(
                3,
                "Concluída 1h",
                "completed",
                days=0,
                sort_key=now - timedelta(hours=1),
            ),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        assert [t["id"] for t in panel._ordered] == [2, 3, 1]

    def test_br_tui_003_r20_cancelled_last(self) -> None:
        """Cancelled vem por último; intra-grupo ordena por sort_key descendente.

        Pending + completed + duas cancelled (3h e 18h atrás). Esperado:
        pending, completed, cancelled-recente, cancelled-antiga.
        """
        now = datetime(2026, 5, 24, 12, 0)
        tasks = [
            _make_task(
                1,
                "Cancelada 18h",
                "cancelled",
                days=0,
                sort_key=now - timedelta(hours=18),
            ),
            _make_task(
                2,
                "Pendente",
                "pending",
                days=1,
                sort_key=now + timedelta(days=1),
            ),
            _make_task(
                3,
                "Concluída",
                "completed",
                days=0,
                sort_key=now - timedelta(hours=2),
            ),
            _make_task(
                4,
                "Cancelada 3h",
                "cancelled",
                days=0,
                sort_key=now - timedelta(hours=3),
            ),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        assert [t["id"] for t in panel._ordered] == [2, 3, 4, 1]


class TestOrderTasksFallbackBehavior:
    """Valida o fallback de _order_tasks quando sort_key está ausente.

    Cenário relevante: instâncias materializadas antes do fix da camada 2
    (#43) não têm sort_key. O _order_tasks deve degradar graciosamente —
    manter agrupamento por bucket e preservar ordem de inserção intra-
    bucket — em vez de levantar exceção ou produzir ordem arbitrária.
    """

    def test_fallback_preserves_insertion_order_within_bucket(self) -> None:
        """Sem sort_key, tasks no mesmo bucket mantêm ordem de inserção."""
        tasks = [
            _make_task(1, "Tarde", "pending", days=0, time="20:00"),
            _make_task(2, "Manhã", "pending", days=0, time="08:00"),
            _make_task(3, "Tarde-meio", "pending", days=0, time="14:00"),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        assert [t["id"] for t in panel._ordered] == [1, 2, 3]

    def test_fallback_pushes_keyless_tasks_after_keyed_within_same_bucket(
        self,
    ) -> None:
        """Tasks sem sort_key vão depois das com sort_key, mesmo bucket."""
        now = datetime(2026, 5, 24, 12, 0)
        tasks = [
            _make_task(1, "Sem chave", "pending", days=0, time="20:00"),
            _make_task(
                2,
                "Com chave manhã",
                "pending",
                days=0,
                time="08:00",
                sort_key=now.replace(hour=8),
            ),
            _make_task(
                3,
                "Com chave tarde",
                "pending",
                days=0,
                time="14:00",
                sort_key=now.replace(hour=14),
            ),
        ]
        panel = _make_panel_with_tasks(tasks)

        panel._order_tasks()

        # Com sort_key primeiro (ascendente), depois sem
        assert [t["id"] for t in panel._ordered] == [2, 3, 1]
