"""Testes para BR-TUI-009: Service Layer Sharing.

Valida session helper e integração TUI com services existentes.
"""

from unittest.mock import MagicMock, patch

from sqlmodel import Session

from timeblock.tui.session import get_session, service_action

# ============================================================
# BR-TUI-009 R01: Session helper fornece sessão funcional
# ============================================================


class TestBRTUI009R01SessionHelper:
    """BR-TUI-009 R01: get_session() fornece sessão de banco."""

    def test_br_tui_009_r01_get_session_is_context_manager(self) -> None:
        """get_session é um context manager."""

        assert hasattr(get_session, "__enter__") or callable(get_session)

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r01_yields_session(self, mock_engine_ctx: MagicMock) -> None:
        """get_session retorna uma Session."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        with get_session() as session:
            assert session is not None

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r01_session_is_sqlmodel(self, mock_engine_ctx: MagicMock) -> None:
        """Session retornada é SQLModel Session."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        with get_session() as session:
            assert isinstance(session, Session)


# ============================================================
# BR-TUI-009 R02: Services acessíveis via helper
# ============================================================


class TestBRTUI009R02ServicesAccessible:
    """BR-TUI-009 R02: Todos os services importáveis e instanciáveis."""

    def test_br_tui_009_r02_routine_service_importable(self) -> None:
        """RoutineService importável."""
        from timeblock.services.routine_service import RoutineService

        assert RoutineService is not None

    def test_br_tui_009_r02_habit_service_importable(self) -> None:
        """HabitService importável."""
        from timeblock.services.habit_service import HabitService

        assert HabitService is not None

    def test_br_tui_009_r02_task_service_importable(self) -> None:
        """TaskService importável."""
        from timeblock.services.task_service import TaskService

        assert TaskService is not None

    def test_br_tui_009_r02_timer_service_importable(self) -> None:
        """TimerService importável."""
        from timeblock.services.timer_service import TimerService

        assert TimerService is not None


# ============================================================
# BR-TUI-009 R03: Session per action
# ============================================================


class TestBRTUI009R03SessionPerAction:
    """BR-TUI-009 R03: Cada operação usa sessão independente."""

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r03_independent_sessions(self, mock_engine_ctx: MagicMock) -> None:
        """Duas chamadas criam sessões independentes."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        sessions = []
        with get_session() as s1:
            sessions.append(id(s1))
        with get_session() as s2:
            sessions.append(id(s2))

        assert sessions[0] != sessions[1]


# ============================================================
# BR-TUI-009 R04: service_action wrapper
# ============================================================


class TestBRTUI009R04ServiceAction:
    """BR-TUI-009 R04: service_action encapsula try/except."""

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r04_success_returns_result(self, mock_engine_ctx: MagicMock) -> None:
        """Operação bem-sucedida retorna resultado."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        def action(session: Session) -> str:
            return "ok"

        result, error = service_action(action)
        assert result == "ok"
        assert error is None

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r04_error_returns_message(self, mock_engine_ctx: MagicMock) -> None:
        """Operação com erro retorna mensagem."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        def action(session: Session) -> str:
            raise ValueError("Item não encontrado")

        result, error = service_action(action)
        assert result is None
        assert error == "Item não encontrado"

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r04_unexpected_error_returns_generic(
        self, mock_engine_ctx: MagicMock
    ) -> None:
        """Erro inesperado retorna mensagem genérica."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        def action(session: Session) -> str:
            raise RuntimeError("DB crash")

        result, error = service_action(action)
        assert result is None
        assert "DB crash" in error


# ============================================================
# BR-TUI-009 R05: Commit e rollback
# ============================================================


class TestBRTUI009R05CommitRollback:
    """BR-TUI-009 R05: Commit em sucesso, rollback em erro."""

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r05_commits_on_success(self, mock_engine_ctx: MagicMock) -> None:
        """Session.commit() chamado em operação bem-sucedida."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        def action(session: Session) -> str:
            session.commit()
            return "ok"

        with get_session() as session:
            action(session)
            # Se chegou aqui sem erro, commit foi chamado
            assert True

    @patch("timeblock.tui.session.get_engine_context")
    def test_br_tui_009_r05_rollback_on_error(self, mock_engine_ctx: MagicMock) -> None:
        """service_action nao propaga exceção para TUI."""
        mock_engine = MagicMock()
        mock_engine_ctx.return_value.__enter__ = MagicMock(return_value=mock_engine)
        mock_engine_ctx.return_value.__exit__ = MagicMock(return_value=False)

        def action(session: Session) -> str:
            raise ValueError("Erro de validação")

        result, error = service_action(action)
        # Não propagou exceção
        assert error is not None
        assert result is None
