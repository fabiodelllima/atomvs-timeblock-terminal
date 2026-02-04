# Roadmap

**Versão:** 4.0.0

**Status:** Single Source of Truth (SSOT)

**Documentos Relacionados:** architecture.md, business-rules.md, quality-metrics.md, technical-debt.md

---

## Sumário Executivo

TimeBlock Organizer é uma aplicação CLI para gerenciamento de tempo baseada em Time Blocking e nos princípios de Atomic Habits. A arquitetura segue o modelo offline-first, priorizando funcionalidade completa sem dependência de rede, com evolução planejada para TUI (v1.7.x), API REST (v2.x), sincronização distribuída (v3.x) e mobile Android (v4.x).

O projeto atingiu maturidade significativa em infraestrutura: CI/CD dual-repo (GitLab fonte de verdade + GitHub showcase), sincronização automática, branch protection, pre-commit hooks, typecheck bloqueante e pipeline de 8 jobs. O foco atual é fechar gaps de cobertura de testes antes da introdução da interface TUI.

**Estado Atual (03/02/2026):**

- Versão: v1.5.0 (estável)
- Qualidade: 76% cobertura, 0 erros mypy, 873 testes
- Funcionalidade: 85% comandos CLI operacionais
- Infraestrutura: CI/CD dual-repo com sync automático, 8 jobs bloqueantes

---

## 1. Visão de Produto

### 1.1. Evolução Arquitetural

A estratégia de evolução do TimeBlock Organizer segue um modelo incremental onde cada versão major adiciona uma camada de capacidade sem descartar as anteriores. A CLI permanece funcional mesmo após a introdução da TUI e da API, garantindo que automações e scripts existentes não sejam quebrados.

```
v1.5 CI/CD => v1.6 Cobertura => v1.7 TUI => v2.x API => v3.x Sync => v4.x Mobile
```

A decisão de introduzir TUI ainda dentro da v1.x, antes da API, reflete a prioridade de manter a experiência do usuário local rica enquanto a camada de serviços amadurece. Detalhes em: `architecture.md` seção 9 (Evolução Futura).

### 1.2. Princípios de Desenvolvimento

Estes princípios guiam todas as decisões técnicas e de produto. Não são aspiracionais -- são critérios de aceite aplicados em cada commit, verificados automaticamente pelo pipeline CI/CD e pelos pre-commit hooks.

1. **Offline-First:** Funcionalidade completa sem rede
2. **User Control:** Sistema propõe, usuário decide
3. **Quality First:** 80% cobertura, zero erros mypy em produção
4. **Engenharia de Requisitos:** BRs formalizadas antes da implementação (ISO/IEC/IEEE 29148:2018, SWEBOK v4.0)

---

## 2. Releases Entregues

O histórico de releases mostra uma progressão consistente: cada versão expandiu funcionalidade enquanto manteve ou melhorou métricas de qualidade.

| Versão | Data     | Escopo                       | Detalhes     |
| ------ | -------- | ---------------------------- | ------------ |
| v1.0.0 | Out/2025 | Foundation                   | CHANGELOG.md |
| v1.1.0 | Nov/2025 | Core Features                | CHANGELOG.md |
| v1.2.0 | Nov/2025 | Status Refactoring           | CHANGELOG.md |
| v1.3.0 | Dez/2025 | Event Reordering (Parcial)   | CHANGELOG.md |
| v1.4.0 | Jan/2026 | Mypy Zero, Services Complete | CHANGELOG.md |
| v1.4.1 | Jan/2026 | E2E Tests, Quality Metrics   | CHANGELOG.md |
| v1.5.0 | Fev/2026 | CI/CD Dual-Repo, i18n        | CHANGELOG.md |

O detalhamento de métricas por release está disponível em `docs/core/quality-metrics.md`.

---

## 3. Estado Atual

A versão v1.5.0 consolidou a infraestrutura de CI/CD com arquitetura dual-repo (GitLab como fonte de verdade, GitHub como showcase), sincronização automática via job sync:github, e padronização de mensagens CLI em português.

- **Versão:** v1.5.0 (estável)
- **Branch:** `develop`
- **Data:** 03 de Fevereiro de 2026

### 3.1. Métricas Principais

As métricas atuais refletem medições reais executadas em 03/02/2026.

| Métrica       | Atual | Meta v1.6.0 | Status     |
| ------------- | ----- | ----------- | ---------- |
| Cobertura     | 76%   | 80%         | [PENDENTE] |
| Erros mypy    | 0     | 0           | [OK]       |
| Testes total  | 873   | 900+        | [OK]       |
| CLI funcional | 85%   | 100%        | [PENDENTE] |
| BRs cobertas  | 83%   | 95%         | [PENDENTE] |

### 3.2. Distribuição de Testes

```
Unit:        696 (79.7%)
Integration:  83 (9.5%)
BDD:          52 (6.0%)
E2E:          42 (4.8%)
─────────────────────────
TOTAL:       873 testes
```

### 3.3. Infraestrutura CI/CD

```
GitLab CI: 8 jobs (6 test + 1 build + 1 sync)
GitHub Actions: 6 checks + CodeQL
Sync automático: GitLab => GitHub (após pipeline verde)
Pipeline time: ~3min (local => GitHub sync)
```

---

## 4. Roadmap Futuro

### v1.6.0 - Cobertura (Fevereiro 2026)

A v1.6.0 é dedicada a fechar gaps de cobertura antes de introduzir a TUI. Adicionar interface gráfica sobre base com 35% de cobertura em commands/ cria risco de regressões silenciosas.

**Objetivo:** Atingir 80% cobertura global, 95% BRs com testes.

| Sprint | Objetivo                               | Estimativa |
| ------ | -------------------------------------- | ---------- |
| S1     | Cobrir BRs sem testes                  | 3h         |
| S2     | Subir cobertura services/              | 3h         |
| S3     | Subir cobertura commands/ (35% => 60%) | 4h         |

**Critérios de Conclusão:**

- [ ] Cobertura global >= 80%
- [ ] 95%+ BRs com testes
- [ ] 100% comandos CLI funcionais

---

### v1.7.0 - TUI + Produção (Março 2026)

A introdução da TUI com Textual marca a transição do TimeBlock de ferramenta de linha de comando pura para uma aplicação interativa completa. A TUI e a CLI coexistem: a CLI permanece como interface para automação e scripts, enquanto a TUI oferece navegação visual para uso interativo.

| Feature            | Estimativa |
| ------------------ | ---------- |
| TUI com Textual    | 16h        |
| MkDocs publicado   | 4h         |
| Release automation | 4h         |
| PyPI publish       | 2h         |

---

### v2.0.0 - REST API (Q2 2026)

A migração para API REST representa a mudança arquitetural mais significativa do projeto: separação entre frontend e backend, autenticação, e persistência em banco de dados relacional.

**Stack:** FastAPI + PostgreSQL + JWT + Prometheus

Ver: `architecture.md` seção 9.2

---

### v3.0.0 - Sync (Q3 2026)

A camada de sincronização resolve o problema de múltiplos dispositivos acessando os mesmos dados. O modelo event-driven com resolução de conflitos garante que mudanças offline sejam integradas de forma consistente.

**Stack:** Kafka + CloudEvents + Conflict Resolution

Ver: `architecture.md` seção 9.3

---

### v4.0.0 - Mobile (Q4 2026)

O cliente Android é o objetivo final da evolução arquitetural, tornando o TimeBlock acessível no dispositivo que o usuário mais carrega consigo.

**Stack:** Kotlin + Jetpack Compose + Room

Ver: `architecture.md` seção 9.4

---

## 4.1. Detalhamento v1.6.0

### Sprint 1: BRs Sem Cobertura (3h)

Das business rules formalizadas, algumas não possuem testes rastreáveis. Verificar nomenclatura antes de implementar novos testes.

| BR             | Domínio | Prioridade | Estimativa |
| -------------- | ------- | ---------- | ---------- |
| BR-TAG-001     | Tag     | Alta       | 30min      |
| BR-TAG-002     | Tag     | Alta       | 30min      |
| BR-SKIP-002    | Skip    | Verificar  | 15min      |
| BR-SKIP-003    | Skip    | Verificar  | 15min      |
| BR-SKIP-004    | Skip    | Verificar  | 15min      |
| BR-ROUTINE-006 | Routine | Média      | 30min      |
| BR-TASK-006    | Task    | Média      | 30min      |
| BR-CLI-001     | CLI     | Baixa      | 15min      |
| BR-CLI-003     | CLI     | Baixa      | 15min      |

---

### Sprint 2: Cobertura Services (3h)

Arquivos de service com maior gap de cobertura.

| Arquivo            | Atual | Meta | Ação                  |
| ------------------ | ----- | ---- | --------------------- |
| tag_service.py     | 100%  | -    | [DONE]                |
| routine_service.py | 91%   | -    | [DONE]                |

Nota: event_reordering_service.py já está em 86% (resolvido).

---

### Sprint 3: Cobertura Commands (4h)

A camada de commands/ está com cobertura desigual. Foco em testes de integração via CliRunner.

| Arquivo          | Atual | Meta | Ação              |
| ---------------- | ----- | ---- | ----------------- |
| habit/display.py | 14%   | 50%+ | Prioridade 1      |
| tag.py           | 21%   | 50%+ | Prioridade 2      |
| habit/atom.py    | 42%   | 60%+ | Prioridade 4      |
| routine.py       | 33%   | 50%+ | Prioridade 3      |
| reschedule.py    | 35%   | 60%+ | Integration tests |

---

## 5. Débito Técnico

O inventário completo está em `docs/core/technical-debt.md`.

**Resumo:**

| Status    | Quantidade | Itens                                  |
| --------- | ---------- | -------------------------------------- |
| Resolvido | 5          | DT-001, DT-002, DT-004, DT-005, DT-006 |
| Pendente  | 1          | DT-003 (cobertura 76%, meta 80%)       |
| Aceito    | 1          | DT-007 (migration_001)                 |

---

## 6. Política de Governança

### 6.1. Hierarquia de Documentos

```
SSOT Documents:
├── roadmap.md           => Estado e planejamento
├── business-rules.md    => Regras de negócio
├── architecture.md      => Decisões técnicas
├── quality-metrics.md   => Métricas operacionais
├── technical-debt.md    => Inventário de débito técnico
└── CHANGELOG.md         => Histórico de releases

ADRs (Imutáveis):
└── docs/decisions/      => Decisões arquiteturais

Working Documents:
└── docs/testing/        => Estratégias de teste
```

---

## 7. Changelog do Documento

| Data       | Versão | Mudanças                                                 |
| ---------- | ------ | -------------------------------------------------------- |
| 2026-01-14 | 1.0.0  | Criação inicial                                          |
| 2026-01-16 | 2.0.0  | Reformulação profissional                                |
| 2026-01-16 | 2.1.0  | Remoção de duplicações, referências a docs externos      |
| 2026-02-01 | 3.0.0  | Atualização com dados reais, retrospectiva v1.4.0        |
| 2026-02-03 | 4.0.0  | v1.5.0 entregue, replanejar v1.6.0 cobertura, v1.7.0 TUI |

---

**Próxima Revisão:** Fim v1.6.0

**Última atualização:** 03 de Fevereiro de 2026
