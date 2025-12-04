#!/usr/bin/env bash
set -euo pipefail

echo "[LEMBRETE] Push GitLab completo. Considere atualizar:"
echo "  - docs/core/workflows.md (se workflow mudou)"
echo "  - CHANGELOG.md (features, fixes, breaking changes)"
echo "  - docs/decisions/ (nova ADR se decisão arquitetural)"
echo ""

echo -e "${BLUE}==========================================${NC}"
echo -e "${YELLOW}[LEMBRETE]${NC} Push GitLab completo. Considere atualizar:"
echo "  - docs/core/workflows.md (se workflow mudou)"
echo "  - CHANGELOG.md (features, fixes, breaking changes)"
echo "  - docs/decisions/ (nova ADR se decisão arquitetural)"
echo -e "${BLUE}==========================================${NC}"
echo ""

# ========================================
# LEMBRETE PÓS-PUSH
# ========================================
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${YELLOW}[LEMBRETE]${NC} Push GitLab completo. Considere atualizar:"
echo "  - docs/core/workflows.md (se workflow mudou)"
echo "  - CHANGELOG.md (features, fixes, breaking changes)"
echo "  - docs/decisions/ (nova ADR se decisão arquitetural)"
echo -e "${BLUE}==========================================${NC}"
echo ""
