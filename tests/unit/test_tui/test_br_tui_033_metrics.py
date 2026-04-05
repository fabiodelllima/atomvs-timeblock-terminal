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
        best_streak=0,
    )


def _mock_period_session(
    routine: SimpleNamespace,
    habits: list[SimpleNamespace],
    existing_ids_per_call: list[list[int]] | None = None,
) -> MagicMock:
    """Cria mock de Session para ensure_period_instances.

    Sequência de session.exec():
      1. select(Routine) → .first() retorna routine
      2. select(Habit) → .all() retorna habits
      3+. select(HabitInstance.habit_id) por data → .all() retorna IDs existentes
    """
    session = MagicMock()
    call_count = {"n": 0}
    _existing = existing_ids_per_call or []

    def exec_side(query):
        call_count["n"] += 1
        result = MagicMock()
        if call_count["n"] == 1:
            result.first.return_value = routine
        elif call_count["n"] == 2:
            result.all.return_value = habits
        else:
            idx = call_count["n"] - 3
            if idx < len(_existing):
                result.all.return_value = _existing[idx]
            else:
                result.all.return_value = []
        return result

    session.exec.side_effect = exec_side
    return session


# =========================================================================
# BR-TUI-033-R8: Geração retroativa de instâncias
# =========================================================================


class TestBRTUI033R8RetroactiveInstances:
    """BR-TUI-033-R8: Dias sem instâncias recebem PENDING retroativo."""

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_creates_pending_for_missing_days(self, mock_sa):
        """Dias sem instância para hábito EVERYDAY geram PENDING retroativo."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        habit = _make_habit(habit_id=1, recurrence=Recurrence.EVERYDAY)
        routine = _make_routine(created_at=datetime.now() - timedelta(days=10))
        added_instances = []

        def side_effect(fn):
            session = _mock_period_session(routine, [habit])
            session.add.side_effect = lambda obj: added_instances.append(obj)
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = ensure_period_instances(routine_id=1, days=7)

        assert result >= 1, "Deveria criar instâncias retroativas"
        assert len(added_instances) >= 1

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_respects_recurrence_on_retroactive(self, mock_sa):
        """Hábito WEEKDAYS não gera instância retroativa em sábado/domingo."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        habit = _make_habit(habit_id=1, recurrence=Recurrence.WEEKDAYS)
        routine = _make_routine(created_at=datetime.now() - timedelta(days=10))
        added_instances = []

        def side_effect(fn):
            session = _mock_period_session(routine, [habit])
            session.add.side_effect = lambda obj: added_instances.append(obj)
            return fn(session), None

        mock_sa.side_effect = side_effect
        ensure_period_instances(routine_id=1, days=7)

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
        routine = _make_routine(created_at=datetime.now() - timedelta(days=10))

        # Todas as datas já têm habit_id=1
        all_existing = [[1]] * 7

        def side_effect(fn):
            session = _mock_period_session(routine, [habit], existing_ids_per_call=all_existing)
            return fn(session), None

        mock_sa.side_effect = side_effect
        result = ensure_period_instances(routine_id=1, days=2)

        assert result == 0, "Não deveria criar duplicatas"

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_respects_routine_created_at_boundary(self, mock_sa):
        """Não gera instâncias para datas anteriores ao created_at da rotina."""
        from timeblock.tui.screens.dashboard.loader import ensure_period_instances

        routine = _make_routine(created_at=datetime.now() - timedelta(days=3))
        habit = _make_habit(habit_id=1, recurrence=Recurrence.EVERYDAY)
        added_instances = []

        def side_effect(fn):
            session = _mock_period_session(routine, [habit])
            session.add.side_effect = lambda obj: added_instances.append(obj)
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
        instances = [
            _make_instance(
                inst_id=i + 1, habit_id=1, inst_date=today - timedelta(days=i), status=Status.DONE
            )
            for i in range(3)
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
            session.get.return_value = _make_routine()
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
            _make_instance(inst_id=1, habit_id=1, inst_date=today, status=Status.DONE),
            _make_instance(
                inst_id=2,
                habit_id=1,
                inst_date=today - timedelta(days=1),
                status=Status.NOT_DONE,
                not_done_substatus=NotDoneSubstatus.SKIPPED_JUSTIFIED,
            ),
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
            session.get.return_value = _make_routine()
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        assert metrics["streak"] == 1

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_streak_two_misses_breaks(self, mock_sa):
        """Dois dias consecutivos sem DONE quebram streak (grace period)."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        instances = [
            _make_instance(inst_id=1, habit_id=1, inst_date=today, status=Status.PENDING),
            _make_instance(
                inst_id=2,
                habit_id=1,
                inst_date=today - timedelta(days=1),
                status=Status.PENDING,
            ),
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
            session.get.return_value = _make_routine()
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        assert metrics["streak"] == 0


class TestBRTUI033R1HeatmapTotalHabits:
    """BR-TUI-033-R1: Heatmap mostra done/total, não 0/0."""

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_heatmap_shows_total_habits(self, mock_sa):
        """Dias com instâncias PENDING mostram 0/N no heatmap, não 0/0."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
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
            session.get.return_value = _make_routine()
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        assert metrics.get("week_data"), "week_data não pode ser vazio"
        today_entry = metrics["week_data"][-1]
        _day_name, done, total, _checks = today_entry
        assert total == 2, f"Total deveria ser 2, obteve {total}"
        assert done == 0, f"Done deveria ser 0, obteve {done}"


# =========================================================================
# BR-TUI-033-R7/R13/R14: Keybinding f, footer contextual, mock text
# =========================================================================


class TestBRTUI033R14MockTextRemoved:
    """BR-TUI-033-R14: Texto mock [f] 7d/14d/30d removido do corpo do panel."""

    def test_br_tui_033_no_mock_text_in_panel(self):
        """Renderização do MetricsPanel não contém texto mock [f]."""
        from timeblock.tui.widgets.metrics_panel import MetricsPanel

        panel = MetricsPanel()
        captured: list[str] = []
        panel.update = lambda text: captured.append(text)  # type: ignore[assignment]
        panel.border_title = ""
        panel.border_subtitle = ""

        panel._refresh_content(
            {
                "pct_7d": 50,
                "pct_14d": 30,
                "pct_30d": 40,
                "streak": 3,
                "best_streak": 5,
                "week_data": [],
            }
        )

        assert captured, "Panel deveria ter chamado update()"
        assert "[f]" not in captured[0], "Texto mock [f] deveria ter sido removido (R14)"


class TestBRTUI033R7KeybindingPeriod:
    """BR-TUI-033-R7: Keybinding f alterna período entre 7d/14d/30d."""

    def test_br_tui_033_keybinding_f_cycles_period(self):
        """_cycle_period alterna 7 -> 14 -> 30 -> 7."""
        from timeblock.tui.widgets.metrics_panel import MetricsPanel

        panel = MetricsPanel()
        assert panel._period_days == 7, "Período inicial deveria ser 7"

        panel._cycle_period()
        assert panel._period_days == 14

        panel._cycle_period()
        assert panel._period_days == 30

        panel._cycle_period()
        assert panel._period_days == 7, "Deveria voltar para 7 após 30"

    def test_br_tui_033_panel_shows_selected_period_bar(self):
        """Panel exibe barra de completude do período selecionado."""
        from timeblock.tui.widgets.metrics_panel import MetricsPanel

        panel = MetricsPanel()
        captured: list[str] = []
        panel.update = lambda text: captured.append(text)  # type: ignore[assignment]
        panel.border_title = ""
        panel.border_subtitle = ""

        data = {
            "pct_7d": 80,
            "pct_14d": 60,
            "pct_30d": 40,
            "streak": 3,
            "best_streak": 5,
            "week_data": [],
        }

        # Período padrão: 7d
        panel._refresh_content(data)
        assert "80%" in captured[-1], "Deveria mostrar pct_7d (80%)"

        # Cicla para 14d
        panel._period_days = 14
        captured.clear()
        panel._refresh_content(data)
        assert "60%" in captured[-1], "Deveria mostrar pct_14d (60%)"

        # Cicla para 30d
        panel._period_days = 30
        captured.clear()
        panel._refresh_content(data)
        assert "40%" in captured[-1], "Deveria mostrar pct_30d (40%)"


class TestBRTUI033R13FooterContextual:
    """BR-TUI-033-R13: Footer mostra hint de keybinding f para MetricsPanel."""

    def test_br_tui_033_status_bar_has_metrics_keybindings(self):
        """PANEL_KEYBINDINGS para panel-metrics inclui keybinding f."""
        from timeblock.tui.widgets.status_bar import PANEL_KEYBINDINGS

        keys = PANEL_KEYBINDINGS.get("panel-metrics", "")
        assert "f" in keys, "panel-metrics deveria listar keybinding f no footer"


class TestBRTUI033Completude14d:
    """BR-TUI-033: load_metrics retorna pct_14d além de pct_7d e pct_30d."""

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_completude_14d_in_metrics(self, mock_sa):
        """load_metrics retorna pct_14d calculado corretamente."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        # 10 dias de instâncias DONE, restante sem instância
        instances = [
            _make_instance(
                inst_id=i + 1,
                habit_id=1,
                inst_date=today - timedelta(days=i),
                status=Status.DONE,
            )
            for i in range(10)
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
            session.get.return_value = _make_routine()
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        assert "pct_14d" in metrics, "load_metrics deveria retornar pct_14d"
        assert metrics["pct_14d"] > 0, "pct_14d deveria ser > 0 com 10 dias DONE"


# =========================================================================
# BR-TUI-033-R3: best_streak persistido
# =========================================================================


class TestBRTUI033R3BestStreakPersisted:
    """BR-TUI-033-R3: best_streak persiste o maior valor no banco."""

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_best_streak_from_db_when_higher(self, mock_sa):
        """best_streak retornado é o persistido quando maior que o da janela."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        # Janela atual: 2 dias DONE (streak=2, window_best=2)
        instances = [
            _make_instance(
                inst_id=i + 1,
                habit_id=1,
                inst_date=today - timedelta(days=i),
                status=Status.DONE,
            )
            for i in range(2)
        ]

        # Routine com best_streak=15 persistido (de meses atrás)
        routine_obj = _make_routine(routine_id=1)
        routine_obj.best_streak = 15

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
            session.get.return_value = routine_obj
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        assert metrics["best_streak"] == 15, (
            f"best_streak deveria ser 15 (persistido), obteve {metrics['best_streak']}"
        )

    @patch("timeblock.tui.screens.dashboard.loader.service_action")
    def test_br_tui_033_best_streak_updates_db_when_new_record(self, mock_sa):
        """Atualiza best_streak no banco quando streak atual supera o persistido."""
        from timeblock.tui.screens.dashboard.loader import load_metrics

        today = date.today()
        # 5 dias consecutivos DONE
        instances = [
            _make_instance(
                inst_id=i + 1,
                habit_id=1,
                inst_date=today - timedelta(days=i),
                status=Status.DONE,
            )
            for i in range(5)
        ]

        # Routine com best_streak=3 (inferior ao atual)
        routine_obj = _make_routine(routine_id=1)
        routine_obj.best_streak = 3

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
            session.get.return_value = routine_obj

            def track_commit():
                pass

            session.commit.side_effect = track_commit
            return fn(session), None

        mock_sa.side_effect = side_effect
        metrics = load_metrics(routine_id=1)

        assert metrics["best_streak"] == 5, (
            f"best_streak deveria ser 5 (novo recorde), obteve {metrics['best_streak']}"
        )
        assert routine_obj.best_streak == 5, (
            "Routine.best_streak deveria ter sido atualizado para 5"
        )
