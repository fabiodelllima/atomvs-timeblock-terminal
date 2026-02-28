# Technical Debt

**Versão:** 1.1.0

**Status:** SSOT

**Documentos Relacionados:** roadmap.md, quality-metrics.md

---

## 1. Inventário

| ID     | Descrição                     | Severidade | Status    | Resolvido em | Sprint planejado |
| ------ | ----------------------------- | ---------- | --------- | ------------ | ---------------- |
| DT-001 | 156 erros mypy                | CRÍTICA    | RESOLVIDO | Jan/2026     | v1.4.0 S1-S3     |
| DT-002 | 15 testes skipped             | ALTA       | RESOLVIDO | Jan/2026     | v1.4.0 S4        |
| DT-003 | Cobertura abaixo de 80%       | ALTA       | PENDENTE  | -            | v1.6.0           |
| DT-004 | EventReordering parcial (61%) | MÉDIA      | RESOLVIDO | Fev/2026     | -                |
| DT-005 | Código morto                  | BAIXA      | RESOLVIDO | Fev/2026     | -                |
| DT-006 | Idioma misto EN/PT em CLI     | MÉDIA      | RESOLVIDO | Fev/2026     | v1.5.0           |
| DT-007 | migration_001 sem cobertura   | BAIXA      | ACEITO    | -            | -                |

---

## 2. Detalhamento de Itens Resolvidos

### DT-001: Erros Mypy (RESOLVIDO)

- **Descoberto:** 16/01/2026
- **Resolvido:** Jan/2026
- **Impacto original:** 156 erros em modo strict, commands não passavam no type checker
- **Resolução:** Instalação de stubs, correção de Session.exec, correção de SQLAlchemy datetime comparisons, completude do Service Layer, null checks em commands
- **Estado final:** 0 erros em 45 arquivos fonte

### DT-002: Testes Skipped (RESOLVIDO)

- **Descoberto:** 16/01/2026
- **Resolvido:** Jan/2026
- **Impacto original:** 15 testes marcados como skip (stubs vazios, timer API v1, migrations)
- **Resolução:** Implementação dos stubs, atualização para API v2, remoção de testes obsoletos
- **Estado final:** 0 testes skipped, 618 passando

### DT-004: EventReordering Parcial (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Cobertura original:** 61%
- **Cobertura atual:** 86%
- **Resolução:** Testes de integração cobrindo cenários de reorganização

### DT-005: Código Morto (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Verificação:** `ruff check src/timeblock --select F401,F841` retorna 0 issues
- **Resolução:** Limpeza gradual durante refatorações

### DT-006: Idioma Misto EN/PT (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Referência:** ADR-018 (Language Standards)
- **Resolução:** Tradução de mensagens CLI para PT-BR, criação de script lint-i18n.py
- **Verificação:** `python scripts/lint-i18n.py` retorna 0 inconsistências

---

## 3. Detalhamento de Itens Pendentes

### DT-003: Cobertura Abaixo de 80%

- **Cobertura atual:** 76%
- **Meta:** 80%
- **Gap principal:** commands/ (média 40-70%), reschedule.py (35%), routine.py (33%)
- **Ação:** Testes de integração para commands CLI
- **Sprint:** v1.6.0

### DT-007: migration_001 Sem Cobertura (ACEITO)

- **Cobertura:** 0%
- **Justificativa:** Migração one-shot já executada em produção. Custo de testar supera benefício. Será removida quando migração definitiva for criada (v2.0.0).
- **Decisão:** Aceitar o débito. Não investir esforço em cobertura.

---

## 4. Política de Gestão

Novos débitos técnicos devem ser registrados aqui com ID sequencial (DT-XXX), severidade e sprint planejado para resolução. O inventário é revisado a cada release.

**Severidades:**

- **CRÍTICA:** Bloqueia desenvolvimento ou deploy
- **ALTA:** Impacta qualidade ou manutenibilidade significativamente
- **MÉDIA:** Degradação gradual, deve ser resolvido no próximo release
- **BAIXA:** Cosmético ou preferencial, resolver quando conveniente
- **ACEITO:** Débito consciente com justificativa documentada

---

## 5. Changelog do Documento

| Data       | Versão | Mudanças                                           |
| ---------- | ------ | -------------------------------------------------- |
| 2026-02-03 | 1.1.0  | Atualiza status: DT-004, DT-005, DT-006 resolvidos |
| 2026-02-01 | 1.0.0  | Extração do roadmap.md para documento dedicado     |

---

**Próxima Revisão:** Fim v1.6.0

**Última atualização:** 03 de Fevereiro de 2026
