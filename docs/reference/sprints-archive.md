# Sprints — Arquivo Histórico

**Última atualização:** 5 de Fevereiro de 2026

---

## Visão Geral

Este documento registra as sprints concluídas do projeto ATOMVS TimeBlock Terminal. Cada release é reconstituída a partir do CHANGELOG.md e dos commits históricos, preservando o contexto de decisões e entregas. O planejamento e acompanhamento de sprints ativas está em `docs/core/sprints.md`.

---

## v1.0.0 — Foundation (Outubro 2025)

O release inaugural estabeleceu a base funcional do projeto: esquema de banco de dados SQLite, operações CRUD de eventos, listagem com filtros por dia e semana, e suporte ao formato de horário brasileiro (7h, 14h30). A detecção de conflitos foi implementada como aviso não-bloqueante, e o suporte a eventos cruzando meia-noite já estava presente desde o início.

- [x] Inicialização do banco SQLite (`timeblock init`)
- [x] CRUD básico de eventos (`timeblock add`, `timeblock list`)
- [x] Filtros de listagem por dia e semana
- [x] Suporte a formato de horário brasileiro
- [x] Detecção básica de conflitos (warning only)
- [x] Suporte a eventos cruzando meia-noite
- [x] 141 testes com 99% de cobertura

---

## v1.1.0 — Event Reordering (Novembro 2025)

A v1.1.0 implementou o sistema de reordenação de eventos com detecção automática de conflitos, cálculo de prioridades baseado em status e deadlines, e algoritmo sequencial de reordenação. O comando `timeblock reschedule` foi introduzido com confirmação interativa, respeitando o princípio de que o sistema informa mas o usuário decide.

- [x] `EventReorderingService` — lógica central de reordenação (90% cobertura)
- [x] `event_reordering_models.py` — EventPriority, Conflict, ProposedChange, ReorderingProposal
- [x] `proposal_display.py` — output formatado com Rich
- [x] Comando CLI `timeblock reschedule [preview] [--auto-approve]`
- [x] TaskService, HabitInstanceService e TimerService integrados com detecção de conflitos
- [x] 78 novos testes (219 total, +55%)
- [x] Documentação técnica e retrospectiva de sprint

---

## v1.2.1 — Documentação e Consolidação (Novembro 2025)

A v1.2.1 reorganizou a estrutura de documentação do projeto, eliminando duplicações entre diretórios e tornando 20 ADRs navegáveis no MkDocs. A filosofia do projeto (Atomic Habits, controle do usuário) e a arquitetura de sincronização v2.0 foram documentadas como artefatos independentes.

- [x] 9 ADRs adicionados e tornados navegáveis (ADR-012 a ADR-020)
- [x] Estrutura `01-architecture/` consolidada (removidas duplicações)
- [x] `00-architecture-overview.md` — visão consolidada (20KB)
- [x] `16-sync-architecture-v2.md` — arquitetura de sincronização
- [x] `17-user-control-philosophy.md` — filosofia de controle do usuário (15KB)
- [x] `18-project-philosophy.md` — filosofia Atomic Habits (12KB)
- [x] 20 ADRs navegáveis (vs 11 anteriormente, +82%)

---

## v1.2.2 — Logging System (Novembro 2025)

A v1.2.2 introduziu o sistema de logging estruturado com rotating file handler, suporte a console e arquivo, e controles para desabilitar logging em testes. A cobertura de testes subiu de 43% para 83% neste release.

- [x] `logger.py` — setup_logger, get_logger, disable_logging, enable_logging
- [x] Formato estruturado: `[timestamp] [level] [module] message`
- [x] Rotação automática (10MB, 5 backups)
- [x] Testes E2E, integração e unitários para logging
- [x] ADRs 015-018 (refactor HabitAtom)
- [x] Cobertura: 43% → 83%

---

## v1.3.0 — Testing and Quality Consolidation (Dezembro 2025)

A v1.3.0 consolidou a estrutura de testes e formalizou as Business Rules do domínio de Event Reordering (BR-EVENT-001 a BR-EVENT-007). O glossário foi expandido para 298 linhas e a Requirements Traceability Matrix (RTM) foi criada com rastreabilidade completa BR → Test → Code. A filosofia de que o sistema apenas detecta conflitos, sem propor reordenação automática, foi formalizada.

- [x] Estrutura de testes consolidada em `05-testing/`
- [x] `testing-philosophy.md`, `requirements-traceability-matrix.md`, `test-strategy.md`
- [x] 5 cenários de teste acessíveis
- [x] Glossário expandido para 298 linhas
- [x] BR-EVENT-001 a BR-EVENT-007 formalizadas
- [x] Princípios documentados: Controle Explícito do Usuário, Informação Sem Imposição

---

## v1.3.1 — Database Isolation Strategy (Janeiro 2026)

A v1.3.1 implementou a ADR-026 (Test Database Isolation Strategy) com estratégia híbrida: injeção de dependência para testes unitários e variável de ambiente para integração. A análise de cobertura BR → Tests identificou 17 BRs sem cobertura de um total de 52 documentadas. O SSOT para database path foi centralizado em `engine.get_db_path()`.

- [x] ADR-026: Test Database Isolation Strategy
- [x] Matriz completa de cobertura BR → Tests em quality-metrics.md
- [x] 52 BRs documentadas, 35 com testes (67%)
- [x] SSOT de database path em `engine.get_db_path()`
- [x] Fixtures de integração simplificadas (`isolated_db` via env var)
- [x] Fix BR-SKIP-003: IGNORED aceita justificativa retroativa
- [x] 466 testes, 65% cobertura, 0 erros mypy

---

## v1.3.2 — Validation Rules (Janeiro 2026)

A v1.3.2 formalizou as regras de validação de tempo e data (BR-VAL-001 e BR-VAL-002) com 55 novos testes unitários e estrutura BDD para validação de datas. A configuração do pyright foi adicionada ao pyproject.toml.

- [x] BR-VAL-001: Time Validation (20 testes unitários)
- [x] BR-VAL-002: Date Validation (35 testes unitários)
- [x] Estrutura BDD para feature de validação de datas
- [x] Configuração pyright em pyproject.toml
- [x] 466 → 558 testes (+92), cobertura 42%

---

## v1.4.0 — Mypy Zero, Services Complete (Janeiro 2026)

A v1.4.0 atingiu zero erros mypy, documentou 27 ADRs categorizados e formalizou 67 Business Rules. A ADR-027 (Documentation Tooling) estabeleceu MkDocs + mkdocstrings como stack de documentação. O parser multi-formato de datetime (BR-CLI-002) foi implementado suportando ISO 8601, DD-MM-YYYY e DD/MM/YYYY.

- [x] ADR-027: Documentation Tooling (MkDocs + mkdocstrings)
- [x] BR-CLI-002: Multi-format datetime parser
- [x] Seção 5 em architecture.md com modelos reais (Event, PauseLog, ChangeLog)
- [x] Seção 7 em architecture.md com 27 ADRs categorizados
- [x] glab CLI para monitoramento de pipelines GitLab
- [x] Dependências atualizadas (sqlmodel 0.0.31, typer 0.21.1)
- [x] 513 testes, 44% cobertura, 0 erros mypy, 67 BRs

---

## v1.4.1 — E2E Tests Expansion (Janeiro 2026)

A v1.4.1 expandiu significativamente a suite de testes E2E com 28 novos testes cobrindo o lifecycle de tasks e filtros de listagem. A cobertura global subiu de 44% para 71% e o README recebeu o logo ATOMVS e tabela de conteúdos expandida.

- [x] 16 testes E2E para task lifecycle (BR-TASK-001 a 005)
- [x] 12 testes E2E para filtros do comando list
- [x] Logo ATOMVS e TOC expandida no README
- [x] quality-metrics.md atualizado com métricas v2.0.0
- [x] Referências atualizadas (SWEBOK v4.0, ISO/IEC/IEEE 29148:2018)
- [x] 685 testes, 71% cobertura, 42 E2E

---

## v1.5.0 — CI/CD Dual-Repo (Fevereiro 2026)

A v1.5.0 consolidou a infraestrutura de CI/CD com arquitetura dual-repo: GitLab como fonte de verdade e GitHub como showcase público. A sincronização automática via job `sync:github` foi implementada, e o pipeline GitLab alcançou 8 jobs (6 test + 1 build + 1 sync).

- [x] Sincronização automática GitLab → GitHub via job sync:github
- [x] Suporte a GitHub Merge Queue (evento merge_group)
- [x] cicd-flow.md v2.0 com arquitetura dual-repo completa
- [x] GitLab definido como fonte de verdade
- [x] GitHub configurado como showcase público
- [x] Fix: históricos divergentes entre GitLab e GitHub
- [x] 873 testes, 76% cobertura, pipeline ~3min

---

## v1.6.0 — Coverage Sprint (Fevereiro 2026)

A v1.6.0 foi dedicada a fechar gaps de cobertura antes da introdução da TUI. A cobertura global subiu de 76% para 87%, o typecheck foi tornado bloqueante no pipeline, e a sincronização de tags para o GitHub foi automatizada. Ao final, 10 branches auxiliares foram limpas.

- [x] Cobertura global: 76% → 87% (+11pp)
- [x] Testes: 873 → 778 (consolidação, remoção de duplicados)
- [x] MR #14: typecheck bloqueante (`allow_failure: false`)
- [x] MR #15: documentação v1.6.0
- [x] MR #16: sync de tags para GitHub
- [x] Limpeza de 10 branches (GitLab + GitHub + local)
- [x] Tag v1.6.0 criada (commit b015636)
- [x] BRs cobertas: 92%, CLI funcional: 95%
