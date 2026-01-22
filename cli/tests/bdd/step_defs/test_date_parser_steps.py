# pyright: reportAttributeAccessIssue=false
"""Step definitions for date parser BDD tests."""

from datetime import date

from pytest import FixtureRequest
from pytest_bdd import given, parsers, scenarios, then, when

from timeblock.utils.date_parser import parse_date_input

scenarios("../features/date_parser.feature")


@given("the system is initialized")
def system_initialized(session: FixtureRequest) -> None:
    """Sistema inicializado."""
    pass


@when(parsers.parse('I provide the date "{date_str}"'))
def provide_date_string(session: FixtureRequest, date_str: str) -> None:
    """Fornece string de data."""
    session.info["input"] = date_str
    try:
        session.info["result"] = parse_date_input(date_str)
        session.info["error"] = None
    except (ValueError, TypeError) as e:
        session.info["result"] = None
        session.info["error"] = str(e)


@when("I provide an empty date string")
def provide_empty_date_string(session: FixtureRequest) -> None:
    """Fornece string vazia."""
    session.info["input"] = ""
    try:
        session.info["result"] = parse_date_input("")
        session.info["error"] = None
    except (ValueError, TypeError) as e:
        session.info["result"] = None
        session.info["error"] = str(e)


@when(parsers.parse("I provide a date object for {year:d}-{month:d}-{day:d}"))
def provide_date_object(session: FixtureRequest, year: int, month: int, day: int) -> None:
    """Fornece objeto date."""
    date_obj = date(year, month, day)
    session.info["input"] = date_obj
    try:
        session.info["result"] = parse_date_input(date_obj)
        session.info["error"] = None
    except (ValueError, TypeError) as e:
        session.info["result"] = None
        session.info["error"] = str(e)


@then(parsers.parse("the parsed date should be {year:d}-{month:d}-{day:d}"))
def check_parsed_date(session: FixtureRequest, year: int, month: int, day: int) -> None:
    """Verifica data parseada."""
    expected = date(year, month, day)
    assert session.info["result"] == expected, f"Expected {expected}, got {session.info['result']}"


@then(parsers.parse('it should raise error "{error_msg}"'))
def check_error_raised(session: FixtureRequest, error_msg: str) -> None:
    """Verifica erro levantado."""
    assert session.info["error"] is not None, "Expected error but got none"
    assert error_msg in session.info["error"], (
        f"Expected '{error_msg}' in error, got '{session.info['error']}'"
    )
