# Technical Debt

**Versão:** 1.0.0

**Status:** SSOT

**Documentos Relacionados:** roadmap.md, quality-metrics.md

---

## 1. Inventário

| ID     | Descrição                     | Severidade | Status    | Resolvido em | Sprint planejado |
| ------ | ----------------------------- | ---------- | --------- | ------------ | ---------------- |
| DT-001 | 156 erros mypy                | CRÍTICA    | RESOLVIDO | Jan/2026     | v1.4.0 S1-S3     |
| DT-002 | 15 testes skipped             | ALTA       | RESOLVIDO | Jan/2026     | v1.4.0 S4        |
| DT-003 | Cobertura abaixo de 80%       | ALTA       | PENDENTE  | -            | v1.5.0 S2-S3     |
| DT-004 | EventReordering parcial (61%) | MÉDIA      | PENDENTE  | -            | v1.5.0 S2        |
| DT-005 | Código morto                  | BAIXA      | PENDENTE  | -            | v1.5.0           |
| DT-006 | Idioma misto EN/PT em CLI     | MÉDIA      | PENDENTE  | -            | v1.5.0 S4        |
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

---

## 3. Detalhamento de Itens Pendentes

### DT-003: Cobertura Abaixo de 80%

- **Cobertura atual:** 72%
- **Meta:** 80%
- **Gap principal:** commands/ (35%), tag_service.py (29%), routine_service.py (53%)
- **Ação:** Testes de integração para commands, testes unitários para services
- **Sprint:** v1.5.0 S2-S3

### DT-004: EventReordering Parcial

- **Cobertura atual:** event_reordering_service.py em 61%
- **Linhas não cobertas:** 101-176 (fluxo de reorganização principal), 187-189, 204-207
- **Ação:** Testes de integração cobrindo cenários de reorganização
- **Sprint:** v1.5.0 S2

### DT-005: Código Morto

- **Descrição:** Possíveis imports não utilizados, funções órfãs
- **Ação:** Análise com vulture ou ruff --select F401,F841
- **Sprint:** v1.5.0

### DT-006: Idioma Misto EN/PT

- **Referência:** ADR-018 (Language Standards)
- **Impacto:** Mensagens de CLI alternando entre inglês e português
- **Exemplo:** `init.py:34` contém "Error initializing database" em vez de "Erro ao inicializar banco de dados"
- **Ação:** Padronizar todas as mensagens user-facing para PT-BR
- **Critério de conclusão:** `grep -rn "Error\|Warning\|Success\|Created\|Updated\|Deleted\|Not found\|Invalid" src/timeblock/commands/` retorna apenas linhas de código (except, class), não mensagens
- **Sprint:** v1.5.0 S4

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

| Data       | Versão | Mudanças                                       |
| ---------- | ------ | ---------------------------------------------- |
| 2026-02-01 | 1.0.0  | Extração do roadmap.md para documento dedicado |

---

**Próxima Revisão:** Fim v1.5.0

**Última atualização:** 01 de Fevereiro de 2026
