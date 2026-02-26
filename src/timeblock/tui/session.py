"""Session helper para TUI (BR-TUI-009).

Encapsula acesso ao banco de dados para a camada TUI,
garantindo session-per-action e propagação de erros.

Padrão de uso:
    from timeblock.tui.session import get_session, service_action

    # Opção 1: Context manager direto
    with get_session() as session:
        service = RoutineService(session)
        routines = service.list_routines()

    # Opção 2: Wrapper com tratamento de erro
    result, error = service_action(lambda s: RoutineService(s).list_routines())
    if error:
        show_error(error)
"""

from collections.abc import Callable
from contextlib import contextmanager

from sqlmodel import Session

from timeblock.database.engine import get_engine_context


@contextmanager
def get_session():
    """Context manager que fornece Session para operações TUI.

    Cada chamada cria uma sessão independente (session-per-action).
    A sessão é fechada automaticamente ao sair do bloco.

    Yields:
        Session: Sessão SQLModel pronta para uso com services.
    """
    with get_engine_context() as engine, Session(engine) as session:
        yield session


def service_action[T](
    action: Callable[[Session], T],
) -> tuple[T | None, str | None]:
    """Executa operação de service com tratamento de erro.

    Encapsula o padrão try/except para que a TUI nunca
    receba exceções diretamente dos services.

    Args:
        action: Callable que recebe Session e retorna resultado.

    Returns:
        Tupla (resultado, None) em sucesso ou (None, mensagem_erro) em falha.
    """
    try:
        with get_session() as session:
            result = action(session)
            return result, None
    except (ValueError, KeyError) as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)
