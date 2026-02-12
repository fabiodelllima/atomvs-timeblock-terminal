#!/bin/bash
set -e

echo "=== Validação CI/CD Local ==="

# Verifica estrutura
for dir in src tests docs; do
    if [ -d "$dir" ]; then
        echo "[OK] $dir/ existe"
    else
        echo "[FAIL] $dir/ não encontrado"
        exit 1
    fi
done

# Verifica configs na raiz
for file in pyproject.toml .ruff.toml .gitlab-ci.yml; do
    if [ -f "$file" ]; then
        echo "[OK] $file existe"
    else
        echo "[FAIL] $file não encontrado"
        exit 1
    fi
done

# Ativa venv
source venv/bin/activate

# Linting
echo "--- Ruff Check ---"
ruff check src/ tests/

echo "--- Ruff Format ---"
ruff format --check src/ tests/

# Typecheck
echo "--- Mypy ---"
mypy src/timeblock --check-untyped-defs

# Testes
echo "--- Pytest ---"
python -m pytest tests/ -v --tb=short

echo "=== Validação completa ==="
