#!/bin/bash
# Extrai todas as Business Rules documentadas

echo "# Business Rules Inventory"
echo "## Gerado em: $(date)"
echo ""

for domain in habit-skip habit-instance streak routine timer; do
    file="docs/04-specifications/business-rules/${domain}.md"
    if [ -f "$file" ]; then
        echo "### Domain: ${domain}"
        grep -E "^## BR-" "$file" | sed 's/^## /- /'
        echo ""
    fi
done
