"""Testes para BR-CLI-003: Padronização de Idioma PT-BR.

Valida que mensagens CLI, helps e textos exibidos ao usuário
estão em Português Brasileiro conforme ADR-018.
"""

import re
from pathlib import Path

import pytest


COMMANDS_DIR = Path("src/timeblock/commands")

# Palavras inglesas que indicam mensagem não traduzida
ENGLISH_MARKERS = re.compile(
    r'\b(Error|Warning|Success|Failed|Created|Updated|Deleted'
    r'|Not found|Invalid input|Cannot|Please|Already exists'
    r'|must be|should be|is required)\b',
    re.IGNORECASE,
)

# Contextos onde inglês é esperado (exceções BR-CLI-003)
SKIP_LINE_PATTERNS = [
    r'^\s*(import |from |class |def |#|@|logger\.|raise )',
    r'__tablename__',
    r'\.exception\(',
    r'\.warning\(',
    r'\.debug\(',
    r'\.info\(',
]


def _get_user_facing_strings(filepath: Path) -> list[tuple[int, str]]:
    """Extrai linhas com strings voltadas ao usuário (help=, console.print, etc)."""
    results = []
    content = filepath.read_text(encoding="utf-8")

    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()

        # Pular linhas que não são voltadas ao usuário
        if any(re.match(p, stripped) for p in SKIP_LINE_PATTERNS):
            continue

        # Capturar help=, console.print, typer.echo, mensagens Rich
        if any(kw in line for kw in ['help="', "help='", "console.print", "typer.echo"]):
            results.append((i, line))

    return results


class TestBRCli003:
    """Valida BR-CLI-003: Padronização de idioma PT-BR nos commands."""

    def test_br_cli_003_commands_dir_exists(self):
        """BR-CLI-003: diretório de commands existe."""
        assert COMMANDS_DIR.exists(), f"{COMMANDS_DIR} deve existir"

    def test_br_cli_003_help_strings_in_portuguese(self):
        """BR-CLI-003: strings help= dos Typer commands estão em PT-BR."""
        violations = []

        for py_file in COMMANDS_DIR.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            content = py_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.split("\n"), 1):
                # Procurar help="..." ou help='...'
                help_matches = re.findall(r'help=["\']([^"\']+)["\']', line)
                for help_text in help_matches:
                    if ENGLISH_MARKERS.search(help_text):
                        violations.append(f"{py_file.name}:{i}: help=\"{help_text}\"")

        assert not violations, (
            f"BR-CLI-003: {len(violations)} help strings em inglês encontradas:\n"
            + "\n".join(violations)
        )

    def test_br_cli_003_typer_app_help_in_portuguese(self):
        """BR-CLI-003: Typer(help=...) de cada app está em PT-BR."""
        violations = []

        for py_file in COMMANDS_DIR.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.split("\n"), 1):
                if "Typer(help=" in line:
                    help_match = re.search(r'help=["\']([^"\']+)["\']', line)
                    if help_match and ENGLISH_MARKERS.search(help_match.group(1)):
                        violations.append(
                            f"{py_file.name}:{i}: Typer help=\"{help_match.group(1)}\""
                        )

        assert not violations, (
            f"BR-CLI-003: Typer app helps em inglês:\n" + "\n".join(violations)
        )

    def test_br_cli_003_no_english_user_messages(self):
        """BR-CLI-003: console.print/typer.echo sem mensagens em inglês."""
        violations = []

        for py_file in COMMANDS_DIR.rglob("*.py"):
            if py_file.name in ("demo.py",):  # demo pode ter termos técnicos
                continue

            content = py_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.split("\n"), 1):
                if "console.print" in line or "typer.echo" in line:
                    # Remover f-string vars antes de verificar
                    clean = re.sub(r"\{[^}]+\}", "", line)
                    if ENGLISH_MARKERS.search(clean):
                        violations.append(f"{py_file.name}:{i}: {line.strip()[:80]}")

        assert not violations, (
            f"BR-CLI-003: {len(violations)} mensagens em inglês:\n"
            + "\n".join(violations)
        )

    def test_br_cli_003_lint_i18n_script_exists(self):
        """BR-CLI-003: script de validação lint-i18n.py existe."""
        script = Path("scripts/lint-i18n.py")
        assert script.exists(), "scripts/lint-i18n.py deve existir (ADR-018)"
