#!/usr/bin/env python3
"""Validador de consistência de idioma (ADR-018).

Verifica:
- Mensagens CLI em português
- Detecta palavras inglesas comuns em contextos PT-BR
"""

import re
import sys
from pathlib import Path

# Palavras inglesas comuns que indicam mensagem não traduzida
ENGLISH_PATTERNS = [
    r'(?<!\{)\b(Error|Warning|Success|Failed|Created|Updated|Deleted)\b(?!\})',
    r'\b(Not found|Invalid|Cannot|Please|Already exists)\b',
    r'\b(Initialization|Database|Cancelled|Completed)\b(?!\})',
    r'"[^"]*\b(The|This|That|These|Those)\s+\w+[^"]*"',
    r'"[^"]*\b(is|are|was|were|has been|have been)\s+\w+[^"]*"',
    r'\b(must|should|cannot|can\'t|won\'t|doesn\'t)\b',
]

# Exceções válidas (termos técnicos, nomes de classe, etc)
EXCEPTIONS = [
    'HabitInstance', 'TimeLog', 'EventStatus', 'TimerStatus',
    'Console', 'TypeError', 'ValueError', 'KeyError',
    'SQLModel', 'Session', 'Typer', 'Rich',
    'ID', 'CLI', 'API', 'SQL', 'ORM', 'BDD', 'TDD',
    '{completed}', '{created}', '{updated}', '{deleted}',
]


def check_file(filepath: Path) -> list[dict]:
    """Verifica arquivo por inconsistências de idioma."""
    issues = []
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Ignorar imports e definições
        if line.strip().startswith(('import ', 'from ', 'class ', 'def ')):
            continue
            
        # Verificar mensagens console.print/typer
        if 'console.print' in line or 'typer.echo' in line or 'typer.confirm' in line:
            # Remover variáveis f-string antes de verificar
            clean_line = re.sub(r'\{[^}]+\}', '', line)
            
            for pattern in ENGLISH_PATTERNS:
                match = re.search(pattern, clean_line, re.IGNORECASE)
                if match:
                    word = match.group(0)
                    if not any(exc.lower() in word.lower() for exc in EXCEPTIONS):
                        issues.append({
                            'file': str(filepath),
                            'line': i,
                            'type': 'CLI_MESSAGE',
                            'content': line.strip()[:80],
                            'match': word,
                        })
                        break
    
    return issues


def main():
    """Executa validação de idioma."""
    src_path = Path('src/timeblock')
    if not src_path.exists():
        src_path = Path('cli/src/timeblock')
    
    if not src_path.exists():
        print("[ERRO] Diretório src/timeblock não encontrado")
        sys.exit(1)
    
    all_issues = []
    files_checked = 0
    
    for py_file in src_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        files_checked += 1
        issues = check_file(py_file)
        all_issues.extend(issues)
    
    # Relatório
    print("=" * 60)
    print("VALIDAÇÃO DE IDIOMA (ADR-018)")
    print("=" * 60)
    print(f"\nArquivos verificados: {files_checked}")
    print(f"Inconsistências encontradas: {len(all_issues)}")
    
    if all_issues:
        print("\n" + "-" * 60)
        print("DETALHES:")
        print("-" * 60)
        
        for issue in all_issues:
            print(f"\n  {issue['file']}:{issue['line']}")
            print(f"    Match: '{issue['match']}'")
            print(f"    Linha: {issue['content']}")
        
        print("\n" + "=" * 60)
        print(f"[FAIL] {len(all_issues)} inconsistências encontradas")
        print("=" * 60)
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("[OK] Todas as mensagens estão em português")
        print("=" * 60)
        sys.exit(0)


if __name__ == '__main__':
    main()
