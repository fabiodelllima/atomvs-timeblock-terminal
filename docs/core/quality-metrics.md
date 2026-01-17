# Quality Metrics - TimeBlock Organizer

**Versão:** 1.0.0
**Última atualização:** 16 de Janeiro de 2026
**Status:** Documento Operacional (atualizado automaticamente)
**Relacionado:** roadmap.md, CHANGELOG.md

---

## 1. Métricas Atuais

**Data de Referência:** 16 de Janeiro de 2026
**Versão:** v1.3.0 (produção), v1.4.0 (desenvolvimento)
**Branch:** `refactor/service-dependency-injection`

### 1.1. Visão Geral

| Categoria           | Valor Atual | Meta v1.4.0 | Delta | Status         |
| ------------------- | ----------- | ----------- | ----- | -------------- |
| Testes Passando     | 454         | 480         | +26   | [EM PROGRESSO] |
| Testes Skipped      | 26          | 0           | -26   | [BLOQUEADO]    |
| Cobertura Global    | 61%         | 80%         | +19pp | [BLOQUEADO]    |
| Erros Mypy          | 156         | 0           | -156  | [BLOQUEADO]    |
| Commands Funcionais | 40%         | 100%        | +60pp | [BLOQUEADO]    |

### 1.2. Distribuição de Testes

| Tipo        | Quantidade | Percentual | Meta v1.4.0 | Alinhamento |
| ----------- | ---------- | ---------- | ----------- | ----------- |
| Unit        | 378        | 79%        | 70-75%      | [ACIMA]     |
| Integration | 64         | 13%        | 20-25%      | [ABAIXO]    |
| E2E         | 5          | 1%         | 5-10%       | [ABAIXO]    |
| BDD         | 7          | 1%         | Manter      | [OK]        |
| Skipped     | 26         | 5%         | 0%          | [CRÍTICO]   |

**Análise:** Pirâmide de testes desbalanceada. Excesso de unit tests, déficit de integration/E2E.

### 1.3. Cobertura por Módulo

| Módulo    | Cobertura | Status    | Ação Requerida | Sprint       |
| --------- | --------- | --------- | -------------- | ------------ |
| models/   | 95%       | [OK]      | Manutenção     | -            |
| services/ | 70%       | [ATENÇÃO] | +15pp          | v1.4.0 S2    |
| commands/ | 25%       | [CRÍTICO] | +55pp          | v1.4.0 S3    |
| utils/    | 60%       | [ATENÇÃO] | +20pp          | v1.4.0 S2-S3 |
| database/ | 40%       | [CRÍTICO] | +40pp          | v1.4.0 S4    |

**Módulos Críticos:**

- `commands/` - Interface principal do sistema
- `database/` - Migrations e engine configuration

### 1.4. Erros Mypy - Distribuição

| Arquivo                              | Erros   | Percentual | Categoria Principal |
| ------------------------------------ | ------- | ---------- | ------------------- |
| commands/timer.py                    | 23      | 15%        | Métodos ausentes    |
| services/event_reordering_service.py | 42      | 27%        | SQLAlchemy types    |
| commands/task.py                     | 7       | 4%         | Null safety         |
| services/timer_service.py            | 4       | 3%         | SQLAlchemy types    |
| utils/proposal_display.py            | 4       | 3%         | Model attributes    |
| commands/habit.py                    | 1       | 1%         | Type mismatch       |
| utils/queries.py                     | 1       | 1%         | SQLAlchemy types    |
| Outros arquivos                      | 74      | 47%        | Diversos            |
| **TOTAL**                            | **156** | **100%**   | -                   |

**Top 3 Causas:**

1. SQLAlchemy column methods (47 erros, 30%)
2. Service layer incompleto (31 erros, 20%)
3. Null safety em commands (7 erros, 4%)

---

## 2. Histórico de Métricas

### 2.1. Evolução por Release

| Release | Data     | Testes | Cobertura | Erros Mypy | Mudança Significativa |
| ------- | -------- | ------ | --------- | ---------- | --------------------- |
| v1.0.0  | Out/2025 | 50     | 30%       | 0          | Baseline              |
| v1.1.0  | Nov/2025 | 200    | 60%       | 12         | +150 testes           |
| v1.2.0  | Nov/2025 | 350    | 70%       | 38         | Status refactoring    |
| v1.3.0  | Dez/2025 | 454    | 61%       | 156        | Acúmulo de débito     |

**Tendência Preocupante:**

- v1.2.0 → v1.3.0: -9pp cobertura, +118 erros mypy
- Causa: Código não testado adicionado (EventReorderingService)

---

## 3. Metas e Critérios de Qualidade

### 3.1. Critérios de Release

**Obrigatórios (Gate de Release):**

- [ ] Zero erros mypy em modo strict
- [ ] Zero testes skipped sem justificativa
- [ ] Cobertura global ≥ 80%
- [ ] Cobertura de módulos críticos ≥ 85%
- [ ] 100% funcionalidades CLI operacionais
- [ ] Zero memory leaks (ResourceWarnings)

**Desejáveis (Qualidade Superior):**

- [ ] Cobertura ≥ 90%
- [ ] Tempo de execução suite < 60s
- [ ] Zero warnings pylint/ruff
- [ ] Documentação 100% atualizada

### 3.2. Pirâmide de Testes Ideal

```
Distribuição Alvo:

E2E (5-10%)          ▲
Integration (20%)   ███
Unit (70-75%)     ████████

Atual vs Alvo:

E2E:         1% vs 5-10%   [DÉFICIT]
Integration: 13% vs 20%    [DÉFICIT]
Unit:        79% vs 70-75% [EXCESSO]
```

**Ações Necessárias:**

- Adicionar 15-20 E2E tests
- Adicionar 30-40 integration tests
- Redistribuir esforço de unit para integration

### 3.3. Benchmarks de Cobertura

| Módulo    | Mínimo | Alvo | Crítico          |
| --------- | ------ | ---- | ---------------- |
| models/   | 90%    | 95%  | 100% (dados)     |
| services/ | 80%    | 90%  | 95% (lógica)     |
| commands/ | 75%    | 85%  | 90% (interface)  |
| utils/    | 70%    | 80%  | -                |
| database/ | 80%    | 90%  | 95% (migrations) |

---

## 4. Análise de Performance

### 4.1. Tempo de Execução (Suite Completa)

| Fase              | Tempo Atual | Meta      | Status |
| ----------------- | ----------- | --------- | ------ |
| Unit tests        | 8.5s        | < 10s     | [OK]   |
| Integration tests | 2.3s        | < 5s      | [OK]   |
| E2E tests         | 0.4s        | < 5s      | [OK]   |
| Fixtures setup    | 0.5s        | < 2s      | [OK]   |
| **TOTAL**         | **11.7s**   | **< 20s** | [OK]   |

**Análise:** Performance excelente. Suite rápida favorece TDD.

### 4.2. Gargalos Identificados

Nenhum gargalo crítico identificado.

**Observações:**

- Integration tests poderiam crescer 2x sem impacto
- E2E com potencial de crescer 10x mantendo < 60s total

---

## 5. Qualidade de Código

### 5.1. Análise Estática

| Ferramenta | Configuração   | Erros | Warnings | Status    |
| ---------- | -------------- | ----- | -------- | --------- |
| mypy       | strict mode    | 156   | 0        | [CRÍTICO] |
| ruff       | format + check | 0     | 0        | [OK]      |
| pylint     | disabled       | -     | -        | [N/A]     |

**Nota:** Projeto usa ruff exclusivamente para linting/formatting.

### 5.2. Complexidade Ciclomática

| Módulo    | Média | Máxima | Arquivos Complexos          |
| --------- | ----- | ------ | --------------------------- |
| models/   | 2.1   | 8      | 0                           |
| services/ | 4.3   | 15     | 2 (event_reordering, timer) |
| commands/ | 5.8   | 22     | 3 (timer, habit, routine)   |
| utils/    | 3.2   | 10     | 0                           |

**Arquivos Complexos (>15):**

- `services/event_reordering_service.py` - 15 (necessita refatoração)
- `commands/timer.py` - 22 (necessita refatoração)
- `commands/habit.py` - 18 (aceitável para CLI)

**Ação Requerida:** Refatorar event_reordering_service e timer.py em v1.5.0

---

## 6. Rastreabilidade

### 6.1. Business Rules → Tests

**Cobertura de BRs:**

- BRs documentadas: 50
- BRs com testes: ~40 (80%)
- BRs sem testes: ~10 (20%)

**BRs Não Testadas (Críticas):**

- BR-REORDER-003 a 005 (apply_proposal não implementado)
- BR-TIMER-004 (pause tracking em memória, não persistido)
- BR-STREAK-003 (edge cases não cobertos)

**Ação:** Adicionar testes para BRs pendentes em v1.4.0 Sprint 4

### 6.2. Requirements Traceability Matrix

Ver: `docs/testing/requirements-traceability-matrix.md`

---

## 7. Automação e CI/CD

### 7.1. Pre-commit Hooks

| Hook        | Status  | Tempo | Bloqueante         |
| ----------- | ------- | ----- | ------------------ |
| ruff format | [ATIVO] | 1.2s  | Sim                |
| ruff check  | [ATIVO] | 0.8s  | Sim                |
| mypy        | [ATIVO] | 3.5s  | Não (warning only) |
| pytest unit | [ATIVO] | 8.5s  | Sim                |

**Total:** ~14s por commit

**Nota:** Mypy não bloqueia commit para permitir progresso incremental.

### 7.2. CI/CD Pipeline

**Status:** Não implementado (planejado v1.5.0)

**Pipeline Planejado:**

1. Lint (ruff)
2. Type check (mypy strict)
3. Unit tests
4. Integration tests
5. E2E tests
6. Coverage report
7. Build & Release (se tag)

---

## 8. Processo de Atualização

### 8.1. Frequência

| Métrica             | Atualização | Responsável            |
| ------------------- | ----------- | ---------------------- |
| Testes/Cobertura    | Por commit  | Automated (pytest)     |
| Erros Mypy          | Por commit  | Automated (pre-commit) |
| Distribuição Testes | Semanal     | Tech Lead              |
| Histórico           | Por release | Tech Lead              |
| Complexidade        | Mensal      | Tech Lead              |

### 8.2. Scripts de Coleta

```bash
# Executar coleta completa de métricas
./scripts/collect-metrics.sh

# Saída: docs/core/quality-metrics.md (atualizado)
```

**Nota:** Script a implementar em v1.5.0

---

## 9. Referências

- **ROADMAP:** `docs/core/roadmap.md` - Planejamento estratégico
- **CHANGELOG:** `CHANGELOG.md` - Histórico de releases
- **Testing Strategy:** `docs/testing/test-strategy.md` - Abordagem de testes
- **Coverage Report:** `htmlcov/index.html` - Report detalhado (local)

---

## Changelog do Documento

| Data       | Versão | Mudanças                                           |
| ---------- | ------ | -------------------------------------------------- |
| 2026-01-16 | 1.0.0  | Criação inicial - métricas extraídas do roadmap.md |

---

**Atualização:** Por sprint ou quando métricas mudarem significativamente
**Automação:** Planejada para v1.5.0
