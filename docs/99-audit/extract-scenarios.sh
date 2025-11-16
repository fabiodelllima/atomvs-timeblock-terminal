#!/bin/bash
# Extrai todos os scenarios BDD

echo "# BDD Scenarios Inventory"
echo "## Gerado em: $(date)"
echo ""

for file in docs/06-bdd/scenarios/*.feature; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "### File: ${filename}"
        grep -E "Cenário:|Scenario:" "$file" | sed 's/^  /- /'
        echo ""
    fi
done
