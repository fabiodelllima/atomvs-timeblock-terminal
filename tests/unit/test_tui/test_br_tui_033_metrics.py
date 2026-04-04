"""Testes para BR-TUI-033 — MetricsPanel: streak, heatmap, completude.

BR-TUI-033-R2: Streak conta apenas dias com DONE (skip = não praticou).
BR-TUI-033-R4: Dois dias consecutivos sem DONE quebram streak (grace period).
BR-TUI-033-R5: best_streak persiste o maior streak já atingido.
BR-TUI-033-R8: Geração retroativa de instâncias PENDING para dias sem registro.

Referências:
    - ADR-047: Design do MetricsPanel
    - CLEAR, James. Atomic Habits. 2018. ("Nunca quebre duas vezes")
"""

from datetime import date, datetime, time, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from timeblock.models.enums import NotDoneSubstatus, Status
from timeblock.models.habit import Recurrence

# =========================================================================
# Helpers
# =========================================================================


def _make_habit(
    *,
    habit_id: int = 1,
    routine_id: int = 1,
    recurrence: Recurrence = Recurrence.EVERYDAY,
    start: time = time(8, 0),
    end: time = time(9, 0),
) -> SimpleNamespace:
    """Cria objeto simulando Habit ORM."""
    return SimpleNamespace(
        id=habit_id,
        routine_id=routine_id,
        recurrence=recurrence,
        scheduled_start=start,
        scheduled_end=end,
    )


def _make_instance(
    *,
    inst_id: int = 1,
    habit_id: int = 1,
    inst_date: date | None = None,
    status: Status = Status.PENDING,
    not_done_substatus: NotDoneSubstatus | None = None,
) -> SimpleNamespace:
    """Cria objeto simulando HabitInstance ORM."""
    return SimpleNamespace(
        id=inst_id,
        habit_id=habit_id,
        date=inst_date or date.today(),
        status=status,
        not_done_substatus=not_done_substatus,
        scheduled_start=time(8, 0),
        scheduled_end=time(9, 0),
    )


def _make_routine(
    *,
    routine_id: int = 1,
    created_at: datetime | None = None,
) -> SimpleNamespace:
    """Cria objeto simulando Routine ORM."""
    return SimpleNamespace(
        id=routine_id,
        name="Rotina Teste",
        is_active=True,
        created_at=created_at or datetime.now() - timedelta(days=30),
    )


# =========================================================================
# BR-TUI-033-R8: Geração retroativa de instâncias
# =========================================================================


class TestBRTUI033R8RetroactiveInstances:
    """BR-TUI-033-R8: Dias sem instâncias recebem PENDING retroativo."""

    @patch("timeblock.tui.screens.dashboard.loader.HabitInstanceService")
    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_creates_pending_for_missing_days(self, mock_sa, mock_his):
        """Dias sem instância para hábito EVERYDAY geram PENDING retroativo."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        habit = _make_habit(habit_id=1, recurrence=Recurrence.EVERYDAY)
        routine = _make_routine(created_at=datetime.now() - timedelta(days=10))

        # Simula: instância existe apenas para hoje, faltam 6 dias anteriores
        added_instances = []

        def side_effect(fn):
            session = MagicMock()
            # RoutineService.get_active_routine
            routine_svc = MagicMock()
            routine_svc.get_active_routine.return_value = routine

            # select(Habit).where(routine_id)
            # select(HabitInstance) para datas existentes
            def exec_side(query):
                result = MagicMock()
                result.all.return_value = [habit]
                return result

            session.exec.side_effect = exec_side

            # Captura session.add() calls
            def add_side(obj):
                added_instances.append(obj)

            session.add.side_effect = add_side

            return fn(session), None

        mock_sa.side_effect = side_effect
        result = ensure_period_instances(routine_id=1, days=7)

        # Deve criar instâncias PENDING para os 6 dias faltantes
        assert result >= 1, "Deveria criar instâncias retroativas"

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_respects_recurrence_on_retroactive(self, mock_sa):
        """Hábito WEEKDAYS não gera instância retroativa em sábado/domingo."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        habit = _make_habit(habit_id=1, recurrence=Recurrence.WEEKDAYS)

        added_instances = []

        def side_effect(fn):
            session = MagicMock()

            def exec_side(query):
                result = MagicMock()
                result.all.return_value = [habit]
                return result

            session.exec.side_effect = exec_side

            def add_side(obj):
                added_instances.append(obj)

            session.add.side_effect = add_side
            return fn(session), None

        mock_sa.side_effect = side_effect
        ensure_period_instances(routine_id=1, days=7)

        # Verifica que nenhuma instância criada cai em fim de semana
        for inst in added_instances:
            weekday = inst.date.weekday()
            assert weekday < 5, (
                f"Instância criada em {inst.date} (weekday={weekday}) viola recurrence WEEKDAYS"
            )

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_no_duplicates_on_existing_dates(self, mock_sa):
        """Não cria instância retroativa se já existe uma para aquele dia/hábito."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        habit = _make_habit(habit_id=1, recurrence=Recurrence.EVERYDAY)

        def side_effect(fn):
            session = MagicMock()

            call_count = {"n": 0}

            def exec_side(query):
                call_count["n"] += 1
                result = MagicMock()
                if call_count["n"] == 1:
                    result.all.return_value = [habit]
                else:
                    # Retorna habit_ids existentes para cada data
                    result.all.return_value = [1]  # habit_id=1 já existe
                return result

            session.exec.side_effect = exec_side
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = ensure_period_instances(routine_id=1, days=2)

        assert result == 0, "Não deveria criar duplicatas"

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_respects_routine_created_at_boundary(self, mock_sa):
        """Não gera instâncias para datas anteriores ao created_at da rotina."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        # Rotina criada há 3 dias, pedindo 7 dias de retroativo
        routine = _make_routine(created_at=datetime.now() - timedelta(days=3))
        habit = _make_habit(habit_id=1, recurrence=Recurrence.EVERYDAY)

        added_instances = []

        def side_effect(fn):
            session = MagicMock()

            def exec_side(query):
                result = MagicMock()
                result.all.return_value = [habit]
                return result

            session.exec.side_effect = exec_side

            def add_side(obj):
                added_instances.append(obj)

            session.add.side_effect = add_side
            return fn(session), None

        mock_sa.side_effect = side_effect
        ensure_period_instances(routine_id=1, days=7)

        routine_start = routine.created_at.date()
        for inst in added_instances:
            assert inst.date >= routine_start, (
                f"Instância em {inst.date} anterior ao created_at da rotina ({routine_start})"
            )

    def test_br_tui_033_none_routine_returns_zero(self):
        """routine_id=None retorna 0 sem erros."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        result = ensure_period_instances(routine_id=None, days=7)
        assert result == 0


# =========================================================================
# BR-TUI-033-R2/R4/R5: Streak — skip quebra, grace period
# =========================================================================


class TestBRTUI033R2StreakCalculation:
    """BR-TUI-033-R2: Streak conta apenas dias com DONE praticado."""

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_streak_consecutive_done_days(self, mock_sa):
        """Streak = número de dias consecutivos com todos hábitos DONE."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        # 3 dias consecutivos com DONE
        instances = []
        for i in range(3):
            d = today - timedelta(days=i)
            instances.append(
                _make_instance(inst_id=i + 1, habit_id=1, inst_date=d, status=Status.DONE)
            )

        def side_effect(fn):
            session = MagicMock()

            call_count = {"n": 0}

            def exec_side(query):
                call_count["n"] += 1
                result = MagicMock()
                if call_count["n"] == 1:
                    # select(Habit)
                    result.all.return_value = [_make_habit()]
                else:
                    # select(HabitInstance) para 30 dias
                    result.all.return_value = instances
                return result

            session.exec.side_effect = exec_side
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        assert metrics["streak"] == 3

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_streak_skip_breaks_like_miss(self, mock_sa):
        """Skip (NOT_DONE/SKIPPED) quebra streak igual a ausência."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        instances = [
            # Hoje: DONE
            _make_instance(inst_id=1, habit_id=1, inst_date=today, status=Status.DONE),
            # Ontem: SKIPPED (NOT_DONE)
            _make_instance(
                inst_id=2,
                habit_id=1,
                inst_date=today - timedelta(days=1),
                status=Status.NOT_DONE,
                not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            ),
            # Anteontem: DONE
            _make_instance(
                inst_id=3,
                habit_id=1,
                inst_date=today - timedelta(days=2),
                status=Status.DONE,
            ),
        ]

        def side_effect(fn):
            session = MagicMock()

            call_count = {"n": 0}

            def exec_side(query):
                call_count["n"] += 1
                result = MagicMock()
                if call_count["n"] == 1:
                    result.all.return_value = [_make_habit()]
                else:
                    result.all.return_value = instances
                return result

            session.exec.side_effect = exec_side
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        # Skip ontem quebra streak: apenas hoje conta
        assert metrics["streak"] == 1

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_streak_two_misses_breaks(self, mock_sa):
        """Dois dias consecutivos sem DONE quebram streak (grace period)."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        instances = [
            # Hoje: PENDING (não fez)
            _make_instance(inst_id=1, habit_id=1, inst_date=today, status=Status.PENDING),
            # Ontem: PENDING (não fez) — segundo dia consecutivo
            _make_instance(
                inst_id=2,
                habit_id=1,
                inst_date=today - timedelta(days=1),
                status=Status.PENDING,
            ),
            # D-2 a D-5: DONE (streak anterior de 4)
            *[
                _make_instance(
                    inst_id=i + 3,
                    habit_id=1,
                    inst_date=today - timedelta(days=i + 2),
                    status=Status.DONE,
                )
                for i in range(4)
            ],
        ]

        def side_effect(fn):
            session = MagicMock()

            call_count = {"n": 0}

            def exec_side(query):
                call_count["n"] += 1
                result = MagicMock()
                if call_count["n"] == 1:
                    result.all.return_value = [_make_habit()]
                else:
                    result.all.return_value = instances
                return result

            session.exec.side_effect = exec_side
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        # Dois dias sem DONE quebram: streak = 0
        assert metrics["streak"] == 0


class TestBRTUI033R1HeatmapTotalHabits:
    """BR-TUI-033-R1: Heatmap mostra done/total, não 0/0."""

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_heatmap_shows_total_habits(self, mock_sa):
        """Dias com instâncias PENDING mostram 0/N no heatmap, não 0/0."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        # 2 hábitos, ambos PENDING hoje
        instances = [
            _make_instance(inst_id=1, habit_id=1, inst_date=today, status=Status.PENDING),
            _make_instance(inst_id=2, habit_id=2, inst_date=today, status=Status.PENDING),
        ]

        def side_effect(fn):
            session = MagicMock()

            call_count = {"n": 0}

            def exec_side(query):
                call_count["n"] += 1
                result = MagicMock()
                if call_count["n"] == 1:
                    result.all.return_value = [
                        _make_habit(habit_id=1),
                        _make_habit(habit_id=2),
                    ]
                else:
                    result.all.return_value = instances
                return result

            session.exec.side_effect = exec_side
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        # week_data para hoje deve mostrar (day, 0, 2, "..") — total=2, não 0
        assert metrics.get("week_data"), "week_data não pode ser vazio"
        today_entry = metrics["week_data"][-1]  # último = hoje
        _day_name, done, total, _checks = today_entry
        assert total == 2, f"Total deveria ser 2, obteve {total}"
        assert done == 0, f"Done deveria ser 0, obteve {done}"
