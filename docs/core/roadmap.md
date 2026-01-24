# Roadmap - TimeBlock Organizer

**Versão:** 2.1.0

**Status:** Single Source of Truth (SSOT)

**Documentos Relacionados:** architecture.md, business-rules.md, quality-metrics.md

---

## Sumário Executivo

TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo baseada em Time Blocking e nos princípios de Atomic Habits. Arquitetura offline-first com evolução planejada para API REST (v2.x), sincronização distribuída (v3.x) e mobile Android (v4.x).

**Estado Atual (16/01/2026):**

- Versão: v1.3.3 (produção) / v1.4.0 (desenvolvimento)
- Qualidade: 68% cobertura, 0 erros mypy, 15 testes skipped
- Funcionalidade: 40% comandos CLI operacionais

---

## 1. Visão de Produto

### 1.1. Evolução Arquitetural

```
v1.x CLI => v2.x API => v3.x Sync => v4.x Mobile
```

Detalhes em: `architecture.md` seção 9 (Evolução Futura)

### 1.2. Princípios de Desenvolvimento

1. **Offline-First:** Funcionalidade completa sem rede
2. **User Control:** Sistema propõe, usuário decide
3. **Quality First:** 80% cobertura, zero erros mypy em produção
4. **DOCS => CODE:** Documentação precede implementação

---

## 2. Releases Entregues

| Versão | Data     | Escopo                     | Detalhes     |
| ------ | -------- | -------------------------- | ------------ |
| v1.0.0 | Out/2025 | Foundation                 | CHANGELOG.md |
| v1.1.0 | Nov/2025 | Core Features              | CHANGELOG.md |
| v1.2.0 | Nov/2025 | Status Refactoring         | CHANGELOG.md |
| v1.3.0 | Dez/2025 | Event Reordering (Parcial) | CHANGELOG.md |

**Métricas Históricas:** Ver `docs/core/quality-metrics.md`

---

## 3. Estado Atual

- **Versão:** v1.3.3 (produção), v1.4.0 (desenvolvimento)
- **Branch:** `refactor/service-dependency-injection`
- **Data:** 22 de Janeiro de 2026

### 3.1. Métricas Principais

| Métrica        | Atual | Meta v1.4 | Status      |
| -------------- | ----- | --------- | ----------- |
| Cobertura      | 68%   | 80%       | [BLOQUEADO] |
| Erros mypy     | 0     | 0         | [DONE]      |
| Testes skipped | 15    | 0         | [BLOQUEADO] |
| CLI funcional  | 40%   | 100%      | [BLOQUEADO] |

**Detalhamento:** Ver `docs/core/quality-metrics.md`

### 3.2. Problemas Críticos

| ID  | Descrição                | Severidade | Sprint    |
| --- | ------------------------ | ---------- | --------- |
| P1  | Service Layer incompleto | CRÍTICA    | v1.4.0 S2 |
| P2  | Commands layer quebrado  | ALTA       | v1.4.0 S3 |
| P3  | Cobertura inadequada     | MÉDIA      | v1.4.0 S4 |

**Detalhamento P1:** Ver seção 5 (Débito Técnico)

---

## 4. Roadmap Futuro

### v1.4.0 - MVP Funcional (Fevereiro 2026)

**Objetivo:** CLI 100% operacional, zero erros mypy

**Duração:** 16 horas (2 semanas)

| Sprint | Objetivo               | Duração | Entregável                      |
| ------ | ---------------------- | ------- | ------------------------------- |
| S1     | Infraestrutura mypy    | 2h      | -40 erros mypy                  |
| S2     | Completar services     | 4h      | -31 erros mypy, timer funcional |
| S3     | Atualizar commands     | 6h      | -85 erros mypy (zero total)     |
| S4     | Resolver skipped tests | 4h      | 480+ testes, zero skipped       |

**Critérios de Conclusão:**

- [ ] Zero erros mypy
- [ ] Zero testes skipped
- [ ] 80%+ cobertura global
- [ ] 100% comandos CLI funcionais

**Detalhamento:** Ver seção 4.1 (Sprints v1.4.0)

---

### v1.5.0 - Production Ready (Março 2026)

**Objetivo:** Infraestrutura para produção

| Feature            | Estimativa |
| ------------------ | ---------- |
| Docker + CI/CD     | 10h        |
| MkDocs publicado   | 8h         |
| Pre-commit hooks   | 2h         |
| Release automation | 4h         |

---

### v2.0.0 - REST API (Q2 2026)

**Stack:** FastAPI + PostgreSQL + JWT + Prometheus

Ver: `architecture.md` seção 9.2

---

### v3.0.0 - Sync (Q3 2026)

**Stack:** Kafka + CloudEvents + Conflict Resolution

Ver: `architecture.md` seção 9.3

---

### v4.0.0 - Mobile (Q4 2026)

**Stack:** Kotlin + Jetpack Compose + Room

Ver: `architecture.md` seção 9.4

---

## 4.1. Detalhamento v1.4.0

### Sprint 1: Infraestrutura Mypy (2h)

| Task                | Descrição                  | Tempo |
| ------------------- | -------------------------- | ----- |
| Instalar stubs      | types-python-dateutil      | 15min |
| Corrigir migrations | Session.exec => execute    | 45min |
| Corrigir SQLAlchemy | datetime.is\_() => == None | 1h    |

**Entregável:** -40 erros (156 => 116)

---

### Sprint 2: Completar Service Layer (4h)

**Contexto:** Commands referenciam métodos inexistentes em services.

**Impacto:** 31 erros mypy, timer não funcional.

**Resolução:**

| Service              | Métodos Necessários                                     | Tempo |
| -------------------- | ------------------------------------------------------- | ----- |
| TimerService         | get_timelog(), get_active_timer(), start_timer(task_id) | 90min |
| HabitInstanceService | get_instance()                                          | 30min |
| Stubs MVP            | list*instances(), get_timelogs_by*\*()                  | 45min |
| Commands update      | timer.py refactor                                       | 60min |
| Validação            | E2E manual                                              | 30min |

**Entregável:**

- +7 métodos em services
- Timer funcional (start/stop/pause/resume/status)
- -31 erros mypy (116 => 85)

**Detalhamento Técnico:**

- Análise completa: Seção 5 (Débito Técnico => Service Layer Gap)
- Signatures: ADR-007 (será atualizado)
- Implementação: GitHub Issue #TBD

---

### Sprint 3: Commands Layer (6h)

| Command     | Ação                      | Tempo |
| ----------- | ------------------------- | ----- |
| timer.py    | Refatorar para API nova   | 90min |
| task.py     | Null checks               | 60min |
| habit.py    | Type fixes                | 30min |
| schedule.py | Align com services        | 60min |
| report.py   | Verificar compatibilidade | 90min |
| Validação   | E2E workflows             | 30min |

**Entregável:** Zero erros mypy

---

### Sprint 4: Cobertura de BRs (6h)

**Análise (2026-01-19):** 17 BRs sem cobertura de testes

| Prioridade | BRs                                                  | Testes Estimados | Tempo |
| ---------- | ---------------------------------------------------- | ---------------- | ----- |
| Alta       | BR-HABITINSTANCE-002/003, BR-VAL-001/002/003         | 15               | 2h    |
| Média      | BR-SKIP-002/003/004, BR-TASK-004/005, BR-TAG-001/002 | 20               | 3h    |
| Baixa      | BR-ROUTINE-006, BR-TIMER-007, BR-CLI-001/002         | 10               | 1h    |

**Testes Skipped (15):**

| Categoria                  | Quantidade | Ação                    |
| -------------------------- | ---------- | ----------------------- |
| Stubs vazios (integration) | 11         | Implementar ou deletar  |
| Timer API v1               | 6          | Atualizar para v2       |
| Migrations                 | 6          | Aguarda migrate_v2()    |
| Outros                     | 3          | Avaliar individualmente |

**Entregável:** 80% BRs cobertas, <10 skipped

---

## 5. Débito Técnico

### 5.1. Inventário

| ID     | Descrição                | Severidade | Esforço | Sprint       |
| ------ | ------------------------ | ---------- | ------- | ------------ |
| DT-001 | 156 erros mypy           | CRÍTICA    | 16h     | v1.4.0       |
| DT-002 | 15 testes skipped        | ALTA       | 8h      | v1.4.0 S4    |
| DT-003 | Cobertura 65%            | ALTA       | 8h      | v1.4.0 S3-S4 |
| DT-004 | EventReordering parcial  | MÉDIA      | 12h     | v1.5.0       |
| DT-005 | Código morto             | BAIXA      | 2h      | v1.5.0       |
| DT-006 | Inconsistência de idioma | MÉDIA      | 4h      | v1.5.0       |

### 5.2. Service Layer Gap (DT-001 Parcial)

- **Descoberto:** 16/01/2026
- **Severidade:** CRÍTICA
- **Impacto:** 31 erros mypy (20% do total), timer não funcional

#### Problema

Commands referenciam métodos inexistentes:

- `TimerService.get_timelog()` - chamado em timer.py:43
- `HabitInstanceService.get_instance()` - chamado em 4 locais
- `TimerService.start_timer(task_id=X)` - signature incompatível

**Causa Raiz:** ADR-007 define padrão, mas implementação incompleta.

#### Impacto Quantificado

| Arquivo  | Erros | Categoria        |
| -------- | ----- | ---------------- |
| timer.py | 23    | Métodos ausentes |
| task.py  | 7     | Null checks      |
| habit.py | 1     | Type mismatch    |

**Comandos Afetados:** timer start/stop/pause/resume/status (100% quebrados)

#### Resolução Planejada

- **Sprint:** v1.4.0 Sprint 2
- **Duração:** 4 horas
- **Responsável:** Service Layer Team

**Fases:**

1. Implementar métodos críticos (2h)
2. Implementar stubs MVP (45min)
3. Atualizar commands (90min)

**Critérios de Sucesso:**

- [ ] +7 métodos em services
- [ ] Timer 100% funcional
- [ ] Zero erros mypy em timer.py, task.py, habit.py
- [ ] ADR-007 atualizado com API obrigatória

**Documentação Técnica:**

- **Signatures Obrigatórias:** ADR-007 (atualização pendente)
- **Testes:** test_timer_service.py, test_habit_instance_service.py

### 5.3. Inconsistência de Idioma (DT-006)

- **Descoberto:** 24/01/2026
- **Severidade:** MÉDIA
- **Impacto:** UX inconsistente, confusão para usuário

#### Problema

Arquivos CLI com idioma misto (inglês/português) violando ADR-018:

| Arquivo  | Problema                          | ADR-018 diz |
| -------- | --------------------------------- | ----------- |
| add.py   | Mensagens, helps, docstrings (EN) | PT-BR       |
| list.py  | Mensagens de erro (EN)            | PT-BR       |
| init.py  | Docstrings (EN)                   | PT-BR       |
| timer.py | Helps parcialmente (EN)           | PT-BR       |

**Exemplos:**

```python
# INCORRETO (atual)
console.print(f"[red]Error creating event: {e}")
help="Event title"

# CORRETO (ADR-018)
console.print(f"[red]Erro ao criar evento: {e}")
help="Título do evento"
```

#### Impacto UX

- Usuário vê "Error" em alguns comandos e "Erro" em outros
- Helps misturados dificultam compreensão
- Experiência fragmentada

#### Resolução Planejada

- **Sprint:** v1.5.0
- **Duração:** 4 horas
- **Referência:** ADR-018-language-standards.md

**Arquivos a Corrigir:**

1. `commands/add.py` - Traduzir mensagens, helps, docstrings
2. `commands/list.py` - Traduzir mensagens de erro
3. `commands/init.py` - Traduzir docstrings
4. `commands/timer.py` - Revisar helps

**Critérios de Sucesso:**

- [ ] 100% mensagens CLI em português
- [ ] 100% helps em português
- [ ] 100% docstrings de commands em português
- [ ] Zero inconsistências detectadas por grep

---

## 6. Política de Governança

### 6.1. Hierarquia de Documentos

```
SSOT Documents:
├── roadmap.md           => Estado e planejamento
├── business-rules.md    => Regras de negócio
├── architecture.md      => Decisões técnicas
├── quality-metrics.md   => Métricas operacionais
└── CHANGELOG.md         => Histórico de releases

ADRs (Imutáveis):
└── docs/decisions/      => Decisões arquiteturais

Working Documents:
└── docs/testing/        => Estratégias de teste
```

---

## 7. Changelog do Documento

| Data       | Versão | Mudanças                                            |
| ---------- | ------ | --------------------------------------------------- |
| 2026-01-14 | 1.0.0  | Criação inicial                                     |
| 2026-01-16 | 2.0.0  | Reformulação profissional                           |
| 2026-01-16 | 2.1.0  | Remoção de duplicações, referências a docs externos |

---

**Próxima Revisão:** Fim v1.4.0 Sprint 4

**Última atualização:** 22 de Janeiro de 2026
