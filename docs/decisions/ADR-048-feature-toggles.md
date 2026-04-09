# ADR-048: Feature Toggles para Lançamento Incremental

- **Status:** Proposto
- **Data:** 2026-04-09

---

## Contexto

O projeto precisa de um mecanismo para lançar funcionalidades incrementalmente sem expor features incompletas ao usuário. Com a v1.8.0 introduzindo features estruturais (pause tracking em duas fases, backup automático, AgendaPanel redesign), o risco de bloquear releases por dependência entre features é alto.

Humble e Farley (2010, Cap. 13) documentam quatro estratégias para manter a aplicação releasable: feature hiding, mudanças incrementais, branch by abstraction e componentização. Feature toggles são a estratégia mais adequada para o ATOMVS porque permitem deploy de código semi-completo sem impacto no usuário.

O ATOMVS já possui um padrão semelhante na detecção de Textual (BR-TUI-001): sem args abre TUI se disponível, caso contrário cai para CLI. Formalizar este padrão como feature toggles generaliza a prática.

## Decisão

Adotar feature toggles via runtime configuration com os seguintes princípios:

**Mecanismo:** Tabela SQLite `feature_toggles` com schema `(key TEXT PK, enabled BOOL, description TEXT)`. Alternativa futura: arquivo TOML para configurações que não dependam de banco.

**Ciclo de vida de um toggle:**

1. Criado como `enabled=False` quando a feature entra em desenvolvimento
2. Habilitado em builds de desenvolvimento para teste
3. Habilitado por padrão quando a feature está completa
4. Removido (código e toggle) na release seguinte à estabilização

**Convenção de nomes:** `feature.<domínio>.<nome>`, ex: `feature.timer.pause_tracking_phase2`, `feature.agenda.day_pagination`.

**Acesso no código:**

```python
from timeblock.services.feature_service import is_enabled

if is_enabled(session, "feature.timer.pause_tracking_phase2"):
    show_retroactive_attribution_modal()
```

**Poda:** análise estática no commit stage pode listar toggles ativos. Toggles que persistem por mais de 2 releases geram aviso no pipeline.

## Consequências

- Features podem ser lançadas em fases sem bloquear releases
- Código semi-completo é deployado mas inacessível
- Necessário criar `FeatureToggle` model e `feature_service.py`
- Necessário migração de banco (nova tabela)
- Risco de toggles acumularem — mitigado pela regra de poda
- Referência: issue #28
