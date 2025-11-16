#!/bin/bash
# Extrai todos os testes TDD

echo "# TDD Tests Inventory"
echo "## Gerado em: $(date)"
echo ""

for file in cli/tests/unit/test_business_rules/test_br_*.py; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "### File: ${filename}"
        grep -E "def test_br_" "$file" | sed 's/    def /- /' | sed 's/(self)://'
        echo ""
    fi
done
