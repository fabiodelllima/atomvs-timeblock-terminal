"""Configuração compartilhada dos testes e2e.

Inclui monkey-patch para pytest-textual-snapshot 1.1.0 que não trata
o retorno de reportinfo() como str (bug com Python 3.14 + pytest 8.4.2).
Ref: pytest changelog #7259 — reportinfo() retorna str | os.PathLike[str].
"""

from pathlib import Path

import pytest_textual_snapshot


def _patched_node_to_report_path(node) -> Path:
    """Versão corrigida de node_to_report_path que aceita str ou Path."""
    tempdir = pytest_textual_snapshot.get_tempdir()
    path_raw, _, name = node.reportinfo()
    path = Path(path_raw) if isinstance(path_raw, str) else path_raw
    temp = Path(path.parent)
    base = []
    while temp != temp.parent and temp.name != "tests":
        base.append(temp.name)
        temp = temp.parent
    parts = []
    if base:
        parts.append("_".join(reversed(base)))
    parts.append(path.name.replace(".", "_"))
    parts.append(name.replace("[", "_").replace("]", "_"))
    return Path(tempdir.name) / "_".join(parts)


# Aplica o patch no módulo
pytest_textual_snapshot.node_to_report_path = _patched_node_to_report_path
