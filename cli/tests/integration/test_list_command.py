"""Testes de caracterização para comando list.

Estes testes capturam o comportamento atual do código
antes da refatoração.
"""

from typer.testing import CliRunner


def test_pytest_works():
    """Teste canário - verifica que pytest está funcionando.

    Este é um teste trivial que sempre passa.
    Serve para confirmar que o setup está correto.
    """
    assert True
    assert 1 + 1 == 2


def test_typer_cli_runner_works():
    """Teste canário - verifica que CliRunner funciona.

    Testa se conseguimos importar o CliRunner do Typer,
    que será usado nos testes reais.
    """
    runner = CliRunner()
    assert runner is not None
