"""Step definitions para date_validation.feature (BR-VAL-002).

Implementa os passos BDD para validação de datas conforme especificado
na Business Rule BR-VAL-002: Date Validation.
"""

from datetime import date

from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

# Importação será adicionada quando a função existir
# from timeblock.utils.validators import validate_date


# Carrega todos os cenários do arquivo date_validation.feature
scenarios("../features/date_validation.feature")


# ============================================================================
# Given Steps - Preparação do contexto
# ============================================================================


@given("the system is configured with minimum date as 2025-01-01")
def system_configured():
    """Sistema configurado com data mínima de 2025-01-01.

    Esta é uma configuração implícita do sistema. A data mínima está
    hardcoded na função validate_date().
    """
    pass  # Configuração implícita


@given(parsers.parse('I have a date "{date_str}"'))
def prepare_date_object(session: Session, date_str: str):
    """Prepara objeto date a partir de string ISO.

    Args:
        session: Sessão do banco de dados (para armazenar contexto)
        date_str: Data no formato YYYY-MM-DD
    """
    year, month, day = map(int, date_str.split("-"))
    session.info = {"input": date(year, month, day), "input_type": "date"}  # type: ignore


@given(parsers.parse('I have a date string "{date_str}"'))
def prepare_date_string(session: Session, date_str: str):
    """Prepara string de data para validação.

    Args:
        session: Sessão do banco de dados (para armazenar contexto)
        date_str: String contendo a data em qualquer formato
    """
    session.info = {"input": date_str, "input_type": "string"}  # type: ignore


@given("I have an empty date string")
def prepare_empty_date_string(session: Session):
    """Prepara string vazia de data para validação.

    Args:
        session: Sessão do banco de dados (para armazenar contexto)
    """
    session.info = {"input": "", "input_type": "string"}  # type: ignore


# ============================================================================
# When Steps - Ações
# ============================================================================


@when("I validate the date")
def validate_date_action(session: Session):
    """Executa validação de data.

    Tenta validar a data usando a função validate_date(). Captura
    qualquer ValueError que possa ocorrer durante a validação.

    Args:
        session: Sessão do banco de dados (contém input e armazena resultado)
    """
    info = getattr(session, "info", {})
    input_data = info.get("input")

    try:
        # Validar data (object ou string)
        # result = validate_date(input_data)
        # session.info["result"] = result  # type: ignore
        # session.info["error"] = None  # type: ignore
        raise NotImplementedError("validate_date() não implementada ainda")
    except (ValueError, NotImplementedError) as e:
        session.info["result"] = None  # type: ignore
        session.info["error"] = str(e)  # type: ignore


# ============================================================================
# Then Steps - Verificações
# ============================================================================


@then("the date should be accepted")
def date_accepted(session: Session):
    """Verifica que data foi aceita sem erros.

    Args:
        session: Sessão contendo o contexto da validação
    """
    info = getattr(session, "info", {})
    error = info.get("error")
    assert error is None, f"Data deveria ser aceita mas houve erro: {error}"
    assert "result" in info, "Data aceita mas resultado não foi retornado"


@then(parsers.parse("the returned date should be {expected_date}"))
def verify_returned_date(session: Session, expected_date: str):
    """Verifica valor da data retornada.

    Args:
        session: Sessão contendo o contexto da validação
        expected_date: Data esperada no formato YYYY-MM-DD
    """
    info = getattr(session, "info", {})
    result = info.get("result")
    year, month, day = map(int, expected_date.split("-"))
    expected = date(year, month, day)
    assert result == expected, f"Data retornada {result} diferente da esperada {expected}"


@then(parsers.parse('the validation should fail with message "{message}"'))
def validation_failed(session: Session, message: str):
    """Verifica que validação falhou com mensagem específica.

    Args:
        session: Sessão contendo o contexto da validação
        message: Mensagem de erro esperada (ou parte dela)
    """
    info = getattr(session, "info", {})
    error = info.get("error")
    assert error is not None, "Validação deveria ter falhado mas não houve erro"
    assert message in error, f"Mensagem esperada '{message}' não encontrada em '{error}'"
