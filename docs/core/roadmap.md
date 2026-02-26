# Roadmap

**Versão:** 6.0.0

**Status:** Single Source of Truth (SSOT)

**Documentos relacionados:** architecture.md, business-rules.md, quality-metrics.md, technical-debt.md

---

## Sumário Executivo

ATOMVS TimeBlock é uma aplicação CLI/TUI para gerenciamento de tempo baseada em Time Blocking e nos princípios de Atomic Habits. A arquitetura segue o modelo offline-first, priorizando funcionalidade completa sem dependência de rede, com evolução planejada para API REST (v2.x), sincronização distribuída (v3.x) e mobile Android (v4.x).

O projeto atingiu maturidade significativa em infraestrutura: CI/CD dual-repo (GitLab fonte de verdade + GitHub showcase), sincronização automática, branch protection, pre-commit hooks, typecheck bloqueante e pipeline de 7 jobs com Docker e DevSecOps. Cobertura atingiu 87% (threshold 85%). O foco atual é a implementação da TUI com Textual (v1.7.0), com o sistema de cores semânticas Catppuccin Mocha (ADR-021) integrado ao dashboard e 1071 testes passando.

**Estado Atual (23/02/2026):**

- Versão: v1.7.0-dev (branch `feat/tui-phase1`)
- Qualidade: 87% cobertura, 0 erros mypy, 1071 testes
- Funcionalidade: 85% comandos CLI operacionais, TUI dashboard funcional com cores semânticas
- Infraestrutura: CI/CD dual-repo com Docker, DevSecOps, 7 jobs
- Documentação: 81 BRs formalizadas, 32 ADRs, color-system.md, mockups v4

---

## 1. Visão de Produto

### 1.1. Evolução Arquitetural

A estratégia de evolução do TimeBlock Organizer segue um modelo incremental onde cada versão major adiciona uma camada de capacidade sem descartar as anteriores. A CLI permanece funcional mesmo após a introdução da TUI e da API, garantindo que automações e scripts existentes não sejam quebrados. Essa coexistência de interfaces não é acidental — reflete a filosofia de que diferentes contextos de uso demandam diferentes modalidades de interação: scripts e pipelines usam a CLI, o trabalho diário interativo usa a TUI, e integrações externas usarão a API.

```plaintext
v1.5 CI/CD => v1.6 Docker/DevSecOps => v1.7 TUI => v2.x API => v3.x Sync => v4.x Mobile
```

A decisão de introduzir TUI ainda dentro da v1.x, antes da API, reflete a prioridade de manter a experiência do usuário local rica enquanto a camada de serviços amadurece. A TUI consome os mesmos services que a CLI — nenhuma lógica de negócio é duplicada — o que valida a arquitetura de camadas antes de expô-la via API REST. Detalhes em: `architecture.md` seção 9 (Evolução Futura).

O projeto adota o branding ATOMVS com namespace `atomvs-timeblock-*` para o ecossistema multi-repo. Detalhes em: ADR-032.

### 1.2. Princípios de Desenvolvimento

Estes princípios guiam todas as decisões técnicas e de produto. Não são aspiracionais -- são critérios de aceite aplicados em cada commit, verificados automaticamente pelo pipeline CI/CD e pelos pre-commit hooks.

1. **Offline-First:** Funcionalidade completa sem rede
2. **User Control:** Sistema propõe, usuário decide
3. **Quality First:** 85% cobertura, zero erros mypy em produção
4. **Engenharia de Requisitos:** BRs formalizadas antes da implementação (ISO/IEC/IEEE 29148:2018, SWEBOK v4.0)

---

## 2. Releases Entregues

O histórico de releases mostra uma progressão consistente: cada versão expandiu funcionalidade enquanto manteve ou melhorou métricas de qualidade. A trajetória de v1.0.0 até v1.6.0 demonstra um padrão disciplinado: fundação sólida primeiro (models, services, testes), infraestrutura robusta depois (CI/CD, Docker, DevSecOps), e só então interfaces ricas (TUI). Essa sequência não foi arbitrária — cada camada dependia da estabilidade da anterior para evoluir com segurança.

| Versão | Data     | Escopo                       | Detalhes     |
| ------ | -------- | ---------------------------- | ------------ |
| v1.0.0 | Out/2025 | Foundation                   | CHANGELOG.md |
| v1.1.0 | Nov/2025 | Core Features                | CHANGELOG.md |
| v1.2.0 | Nov/2025 | Status Refactoring           | CHANGELOG.md |
| v1.3.0 | Dez/2025 | Event Reordering (Parcial)   | CHANGELOG.md |
| v1.4.0 | Jan/2026 | Mypy Zero, Services Complete | CHANGELOG.md |
| v1.4.1 | Jan/2026 | E2E Tests, Quality Metrics   | CHANGELOG.md |
| v1.5.0 | Fev/2026 | CI/CD Dual-Repo, i18n        | CHANGELOG.md |
| v1.6.0 | Fev/2026 | Docker, DevSecOps, 87% cob.  | CHANGELOG.md |

O detalhamento de métricas por release está disponível em `docs/core/quality-metrics.md`.

---

## 3. Estado Atual

A versão v1.6.0 representou um ponto de inflexão na maturidade do projeto. A cobertura de testes saltou de 76% para 87%, superando o threshold de 85% configurado no pipeline. A introdução de Docker e DevSecOps (bandit, pip-audit) trouxe segurança automatizada. Com essa base consolidada, o projeto está preparado para adicionar complexidade na camada de apresentação sem risco de regressões silenciosas.

A branch `feat/tui-phase1` contém a implementação progressiva da TUI: estrutura de pacotes, theme CSS, NavBar, TimeBlockApp com navegação, DashboardScreen com grade temporal, keybindings globais, e mais recentemente o sistema de cores semânticas Catppuccin Mocha (ADR-021) com suporte completo a substatus (DONE: full/partial/overdone/excessive; NOT_DONE: justified/unjustified/ignored) e background colorido nos timeblocks da agenda.

- **Versão:** v1.7.0-dev
- **Branch:** `feat/tui-phase1`
- **Data:** 23 de Fevereiro de 2026

### 3.1. Métricas Principais

As métricas atuais refletem medições reais executadas em 23/02/2026. Os testes saltaram de 797 para 1071, um aumento de 34% motivado pela expansão do dashboard com substatus, cores semânticas e mock data abrangente. Cobertura se mantém em 87%.

| Métrica       | Atual | Meta v1.7.0 | Status     |
| ------------- | ----- | ----------- | ---------- |
| Cobertura     | 87%   | 85%         | [OK]       |
| Erros mypy    | 0     | 0           | [OK]       |
| Testes total  | 1071  | 850+        | [OK]       |
| CLI funcional | 85%   | 100%        | [PENDENTE] |
| BRs cobertas  | 83%   | 95%         | [PENDENTE] |

### 3.2. Distribuição de Testes

A pirâmide de testes cresceu significativamente com a implementação do dashboard. Os 104 testes do dashboard cobrem: formatação de duração (2 formatos), localização de blocos, mapeamento status/substatus para cores/ícones/bold/fill/background, heat de proximidade para tasks, renderização ASCII art do timer, e validação estrutural de mock data.

```
Unit:        869 (81.1%)
Integration: 116 (10.8%)
BDD:          56 (5.2%)
E2E:          30 (2.8%)
─────────────────────────
TOTAL:      1071 testes
```

### 3.3. Infraestrutura CI/CD

A infraestrutura de CI/CD opera em duas camadas complementares. O GitLab é a fonte de verdade com pipeline completo de 7 jobs, incluindo testes, linting, typecheck, cobertura com threshold, auditoria de segurança e build de documentação. O GitHub recebe sincronização automática após pipeline verde e executa validação espelho para garantir que o repositório de showcase permaneça íntegro.

```plaintext
GitLab CI: 7 jobs (test:all + lint + typecheck + coverage + 2 security + sync)
GitHub Actions: 6 checks + CodeQL
Sync automático: GitLab => GitHub (após pipeline verde)
Pipeline time: ~3min (local => GitHub sync)
```

### 3.4. Progresso TUI (v1.7.0)

A implementação da TUI segue o ADR-031 com sprints incrementais. A fase 1 cobriu a infraestrutura base (entry point, theme, navegação) e evoluiu para o dashboard com sistema de cores semânticas completo (ADR-021). A integração com a paleta Catppuccin Mocha foi documentada em `docs/tui/color-system.md` (550 linhas) com showcase visual em HTML. A fase 2 focará nas telas de conteúdo (Routines, Habits, Tasks) com CRUD contextual.

| Componente                                      | Status     | Commits             |
| ----------------------------------------------- | ---------- | ------------------- |
| Estrutura de pacotes, entry point (BR-TUI-001)  | [DONE]     | `7d4b0be`           |
| theme.tcss, paleta Material-like                | [DONE]     | `d94dda0`           |
| NavBar com navegação horizontal                 | [DONE]     | `fce818f`           |
| TimeBlockApp com navegação (BR-TUI-002)         | [DONE]     | `cacac32`           |
| DashboardScreen com grade temporal (BR-TUI-003) | [DONE]     | `3c29802`           |
| Global keybindings, help overlay (BR-TUI-004)   | [DONE]     | `4b74b90`           |
| color-system.md + showcase HTML (ADR-021)       | [DONE]     | `1e9772b`           |
| Migração cores Catppuccin Mocha                 | [DONE]     | `9733624`           |
| Substatus + backgrounds + ASCII timer           | [DONE]     | pendente commit     |
| Refactor SOLID (colors.py, mock_data.py)        | [PENDENTE] | próximo commit      |
| Documentação BRs novas (substatus, heat, etc.)  | [PENDENTE] | após refactor       |
| Routines Screen (BR-TUI-011)                    | [PENDENTE] | Documentação pronta |
| CRUD pattern (BR-TUI-005)                       | [PENDENTE] | -                   |
| Timer live display (BR-TUI-006)                 | [PENDENTE] | -                   |
| Habit instance actions (BR-TUI-010)             | [PENDENTE] | -                   |

**Documentação TUI:**

- Mockups: `docs/tui/dashboard-mockup-v4.md`, `docs/tui/routines-weekly-mockup.md`
- Color System: `docs/tui/color-system.md` (ADR-021, 550 linhas)
- Showcase: `docs/html/themes/catppuccin-mocha.html`
- BRs: BR-TUI-001 a BR-TUI-011 (seção 14 do business-rules.md)
- ADR: ADR-031 com 7 widgets e plano de sprints

**Mock Data (Rotina Demo):**

O dashboard utiliza mock data para renderização quando o banco está vazio. Os mocks simulam uma rotina completa ("Rotina Demo") com 9 hábitos exercitando todos os status (done, not_done, running, paused, pending) e substatus (full, partial, overdone, excessive, unjustified, ignored), 9 tasks cobrindo os 4 estados (pending, completed, cancelled, overdue) com heat de proximidade, e timer ativo. O mock data serve como rotina de referência visual durante desenvolvimento e será extraído para `mock_data.py` no refactor SOLID.

---

## 4. Roadmap Futuro

### v1.7.0 - TUI + Produção (Fevereiro-Março 2026)

A introdução da TUI com Textual marca a transição do TimeBlock de ferramenta de linha de comando pura para uma aplicação interativa completa. A TUI e a CLI coexistem: a CLI permanece como interface para automação e scripts, enquanto a TUI oferece navegação visual para uso interativo. O design segue a paleta Catppuccin Mocha com sistema de cores semânticas (ADR-021) fundamentado em ISO 3864 e ANSI Z535, keybindings padronizados e responsividade para diferentes tamanhos de terminal (80, 120, 160+ colunas).

A estratégia de implementação prioriza as telas de maior impacto no uso diário: Dashboard (visão do dia), Routines (planejamento semanal) e Timer (execução em tempo real). As telas de CRUD (Habits, Tasks) são construídas sobre um pattern reutilizável que reduz duplicação e mantém consistência visual.

| Feature            | Estimativa | Status     |
| ------------------ | ---------- | ---------- |
| TUI com Textual    | 16h        | [WIP]      |
| MkDocs publicado   | 4h         | [PENDENTE] |
| Release automation | 4h         | [PENDENTE] |
| PyPI publish       | 2h         | [PENDENTE] |

**Próximos passos imediatos (Dashboard):**

1. Commit visual: substatus + backgrounds + ASCII timer + nome herda cor
2. Refactor SOLID: extrair `colors.py`, `formatters.py`, `mock_data.py`
3. Documentar BRs novas (substatus DONE, substatus NOT_DONE, heat de proximidade, bold exclusivo, formatos de duração)
4. Fechar pendências do dashboard-sprint-notes.md

---

### v2.0.0 - REST API (Q2 2026)

A migração para API REST representa a mudança arquitetural mais significativa do projeto: separação entre frontend e backend, autenticação, e persistência em banco de dados relacional. A camada de services já existente — validada por 1071 testes e consumida tanto pela CLI quanto pela TUI — será exposta via endpoints RESTful, minimizando o risco de regressão na lógica de negócio.

**Stack:** FastAPI + PostgreSQL + JWT + Prometheus

Ver: `architecture.md` seção 9.2

---

### v3.0.0 - Sync (Q3 2026)

A camada de sincronização resolve o problema de múltiplos dispositivos acessando os mesmos dados. O modelo event-driven com resolução de conflitos garante que mudanças offline sejam integradas de forma consistente. A decisão de manter o modelo offline-first como fundação significa que o sync é uma camada adicional — o aplicativo permanece funcional sem conectividade.

**Stack:** Kafka + CloudEvents + Conflict Resolution

Ver: `architecture.md` seção 9.3

---

### v4.0.0 - Mobile (Q4 2026)

O cliente Android é o objetivo final da evolução arquitetural, tornando o TimeBlock acessível no dispositivo que o usuário mais carrega consigo. A aplicação mobile consumirá a mesma API REST e participará do mesmo protocolo de sync, compartilhando regras de negócio via contrato de API.

**Stack:** Kotlin + Jetpack Compose + Room

Ver: `architecture.md` seção 9.4

---

## 5. Débito Técnico

O inventário completo está em `docs/core/technical-debt.md`. A situação de débito técnico melhorou significativamente: dos 7 itens registrados, 6 estão resolvidos. O único item remanescente (DT-007, migration_001) é aceito como decisão consciente — a migração inicial é monolítica por design e será substituída por migrações incrementais na v2.0.0 quando o schema evoluir para PostgreSQL.

Um novo item de débito técnico foi identificado: o `dashboard.py` com 973 linhas viola SRP e deve ser refatorado em módulos separados (`colors.py`, `formatters.py`, `mock_data.py`). Este refactor está planejado como próximo commit após o fechamento visual.

| Status    | Quantidade | Itens                                          |
| --------- | ---------- | ---------------------------------------------- |
| Resolvido | 6          | DT-001, DT-002, DT-003, DT-004, DT-005, DT-006 |
| Aceito    | 1          | DT-007 (migration_001)                         |
| Planejado | 1          | DT-008 (dashboard.py SRP - refactor SOLID)     |

Nota: DT-003 (cobertura) resolvido — 87% supera a meta original de 80% e o threshold atual de 85%.

---

## 6. Política de Governança

A governança documental segue o princípio de Single Source of Truth (SSOT): cada tipo de informação tem exatamente um documento autoritativo. Quando há contradição entre documentos, o SSOT do domínio prevalece. ADRs são imutáveis após aceitas — novas decisões que alteram ADRs anteriores referenciam o superseded. Os documentos de TUI Design foram introduzidos como categoria própria para separar artefatos de design visual (mockups, wireframes) da especificação formal (business rules) e das decisões técnicas (ADRs).

### 6.1. Hierarquia de Documentos

```
SSOT Documents:
├── roadmap.md           => Estado e planejamento
├── business-rules.md    => Regras de negócio (81 BRs)
├── architecture.md      => Decisões técnicas
├── quality-metrics.md   => Métricas operacionais
├── technical-debt.md    => Inventário de débito técnico
└── CHANGELOG.md         => Histórico de releases

ADRs (Imutáveis):
└── docs/decisions/      => 32 decisões arquiteturais

TUI Design:
├── docs/tui/            => Mockups de telas, color-system.md
└── docs/html/           => Showcases visuais (HTML)

Working Documents:
└── docs/testing/        => Estratégias de teste
```

---

## 7. Changelog do Documento

| Data       | Versão | Mudanças                                                   |
| ---------- | ------ | ---------------------------------------------------------- |
| 2026-01-14 | 1.0.0  | Criação inicial                                            |
| 2026-01-16 | 2.0.0  | Reformulação profissional                                  |
| 2026-01-16 | 2.1.0  | Remoção de duplicações, referências a docs externos        |
| 2026-02-01 | 3.0.0  | Atualização com dados reais, retrospectiva v1.4.0          |
| 2026-02-03 | 4.0.0  | v1.5.0 entregue, replanejar v1.6.0 cobertura, v1.7.0 TUI   |
| 2026-02-20 | 5.0.0  | v1.6.0 entregue, v1.7.0 TUI em desenvolvimento             |
| 2026-02-23 | 6.0.0  | ADR-021 integrado, 1071 testes, mock data, próximos passos |

---

**Próxima Revisão:** Release v1.7.0

**Última atualização:** 25 de Fevereiro de 2026
