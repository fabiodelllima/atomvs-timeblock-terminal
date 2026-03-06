#!/usr/bin/env bash
# Executa testes no mesmo container do CI para validação pré-push.
# Uso: ./scripts/ci-local.sh [unit|integration|e2e|all]

set -euo pipefail

CI_IMAGE="registry.gitlab.com/delimafabio/atomvs-timeblock-terminal/ci:latest"
SCOPE="${1:-all}"

case "$SCOPE" in
    unit)        TESTS="tests/unit/" ;;
    integration) TESTS="tests/integration/ tests/bdd/" ;;
    e2e)         TESTS="tests/e2e/" ;;
    all)         TESTS="tests/" ;;
    *)           echo "Uso: $0 [unit|integration|e2e|all]"; exit 1 ;;
esac

echo "=== CI Local: $SCOPE ==="
echo "Image: $CI_IMAGE"
echo "Tests: $TESTS"
echo ""

docker run --rm \
    -v "$(pwd)":/app \
    -w /app \
    "$CI_IMAGE" \
    bash -c "pip install --no-deps -e . 2>/dev/null && coverage run -m pytest $TESTS -v --tb=short"
