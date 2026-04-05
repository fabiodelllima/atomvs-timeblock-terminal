# Roadmap

- **Versão:** 7.0.0
- **Status:** Single Source of Truth (SSOT)
- **Documentos relacionados:** architecture.md, business-rules.md, quality-metrics.md, technical-debt.md

---

## Sumário Executivo

ATOMVS TimeBlock é uma aplicação CLI/TUI para gerenciamento de tempo baseada em Time Blocking e nos princípios de Atomic Habits. A arquitetura segue o modelo offline-first, priorizando funcionalidade completa sem dependência de rede, com evolução planejada para API REST (v2.x), sincronização distribuída (v3.x) e mobile Android (v4.x).

O projeto atingiu maturidade significativa em infraestrutura: CI/CD dual-repo (GitLab fonte de verdade + GitHub showcase), sincronização automática, branch protection, pre-commit hooks, typecheck bloqueante e pipeline de 8 jobs paralelos com Docker e DevSecOps. Cobertura em ~81% (threshold 80%). O foco atual é a Sprint 4 — Dashboard-first CRUD com modais contextuais (ADR-034), fixture optimization (ADR-033), e refatorações fundamentadas em Fowler (2002) e Humble & Farley (2010).

**Estado Atual (05/03/2026):**

- Versão: v1.7.0-dev (branch `feat/tui-crud-dashboard`)
- Qualidade: ~81% cobertura (threshold 80%), 0 erros mypy, 1079 testes
- Funcionalidade: 85% CLI, TUI dashboard interativo com dados reais, quick actions, backup automático
- Infraestrutura: CI/CD dual-repo com Docker, DevSecOps, 8 jobs paralelos
- Documentação: 104 BRs formalizadas, 35 ADRs, TCSS modularizado (7 módulos)

---

## 1. Visão de Produto

### 1.1. Evolução Arquitetural

A estratégia de evolução do TimeBlock Planner segue um modelo incremental onde cada versão major adiciona uma camada de capacidade sem descartar as anteriores. A CLI permanece funcional mesmo após a introdução da TUI e da API, garantindo que automações e scripts existentes não sejam quebrados. Essa coexistência de interfaces não é acidental — reflete a filosofia de que diferentes contextos de uso demandam diferentes modalidades de interação: scripts e pipelines usam a CLI, o trabalho diário interativo usa a TUI, e integrações externas usarão a API.

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

O detalhamento de métricas por release está disponível em `docs/reference/quality-metrics.md`.

---

## 3. Estado Atual

A versão v1.6.0 representou um ponto de inflexão na maturidade do projeto. A cobertura de testes saltou de 76% para 87%, superando o threshold de 85% configurado no pipeline. A introdução de Docker e DevSecOps (bandit, pip-audit) trouxe segurança automatizada. Com essa base consolidada, o projeto está preparado para adicionar complexidade na camada de apresentação sem risco de regressões silenciosas.

A Sprint 4 entregou CRUD completo via dashboard com modais contextuais (ADR-034), quick actions via message pattern (RF-001), placeholders editáveis (BR-TUI-013), e widgets reutilizáveis (ConfirmDialog, FormModal). A Sprint 4.5 (First Complete Loop) conectou o fluxo de ponta a ponta no dashboard: criar rotina, criar hábito, iniciar timer, pausar/retomar, parar e marcar done — tudo sem sair do dashboard. O timer atualiza a cada segundo via set_interval, a agenda auto-refresh a cada 60 segundos, e os keybindings foram padronizados conforme ADR-035.

- **Versão:** v1.7.0-dev
- **Branch:** `feat/tui-dashboard-timer`
- **Data:** 11 de Março de 2026

### 3.1. Métricas Principais

As métricas atuais refletem medições reais executadas em 05/03/2026 (branch `feat/tui-dashboard-interactive` pronta para MR → develop). Sprint 3.2 concluída com 1079 testes. Próxima branch: `feat/tui-crud-dashboard`.

| Métrica       | Atual | Meta v1.7.0 | Status     |
| ------------- | ----- | ----------- | ---------- |
| Cobertura     | ~82%  | 80%         | [OK]       |
| Erros mypy    | 0     | 0           | [OK]       |
| Testes total  | 1284  | 1200+       | [OK]       |
| BRs cobertas  | ~110  | 110+        | [OK]       |
| ADRs          | 42    | 35+         | [OK]       |
| CLI funcional | 85%   | 100%        | [PENDENTE] |

### 3.2. Distribuição de Testes

A pirâmide de testes cresceu significativamente ao longo da v1.7.0. A suíte cobre dashboard completo (5 painéis), CRUD contextual, timer live, métricas com streak/heatmap, snapshot testing e BDD com 61 cenários Gherkin.

```plaintext
Unit:        ~990 (74%)
Integration: ~150 (11%)
BDD:           83 (6%)
E2E:          ~117 (9%)
─────────────────────────
TOTAL:       ~1340 testes
```

### 3.3. Infraestrutura CI/CD

A infraestrutura de CI/CD opera em duas camadas complementares. O GitLab é a fonte de verdade com pipeline de 8 jobs em 5 stages paralelos: 3 jobs de teste (unit, integration, e2e) com coverage combine, lint, typecheck, 2 jobs de segurança (bandit, pip-audit) e sync automático. O GitHub recebe sincronização automática após pipeline verde e executa validação espelho para garantir que o repositório de showcase permaneça íntegro.

```plaintext
GitLab CI: 8 jobs (test:unit + test:integration + test:e2e + coverage:report + lint + typecheck + 2 security + sync)
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
- BRs: BR-TUI-001 a BR-TUI-021, BR-TEST-001 (seção 14 e 16 do business-rules.md)
- ADRs: ADR-031 (TUI), ADR-033 (Fixture), ADR-034 (Dashboard-first CRUD), ADR-035 (Keybindings)

**Mock Data (Rotina Demo):**

O dashboard utiliza mock data para renderização quando o banco está vazio. Os mocks simulam uma rotina completa ("Rotina Demo") com 9 hábitos exercitando todos os status (done, not_done, running, paused, pending) e substatus (full, partial, overdone, excessive, unjustified, ignored), 9 tasks cobrindo os 4 estados (pending, completed, cancelled, overdue) com heat de proximidade, e timer ativo. O mock data serve como rotina de referência visual durante desenvolvimento e será extraído para `mock_data.py` no refactor SOLID.

---

## 4. Roadmap Futuro

### v1.7.0 - TUI Completa (Entregue — Abril 2026)

A introdução da TUI com Textual marca a transição do TimeBlock de ferramenta de linha de comando pura para uma aplicação interativa completa. A TUI e a CLI coexistem: a CLI permanece como interface para automação e scripts, enquanto a TUI oferece navegação visual para uso interativo. O design segue a paleta Catppuccin Mocha com sistema de cores semânticas (ADR-021) fundamentado em ISO 3864 e ANSI Z535, keybindings padronizados e responsividade para diferentes tamanhos de terminal (80, 120, 160+ colunas).

A estratégia de implementação prioriza as telas de maior impacto no uso diário: Dashboard (visão do dia), Routines (planejamento semanal) e Timer (execução em tempo real). As telas de CRUD (Habits, Tasks) são construídas sobre um pattern reutilizável que reduz duplicação e mantém consistência visual.

| Feature            | Estimativa | Status     |
| ------------------ | ---------- | ---------- |
| TUI com Textual    | 16h        | [DONE]     |
| MkDocs publicado   | 4h         | [PENDENTE] |
| Release automation | 4h         | [PENDENTE] |
| PyPI publish       | 2h         | [PENDENTE] |

**Próximos passos imediatos (Sprint 4 — Dashboard-first CRUD):**

1. MR `feat/tui-dashboard-interactive` → develop (--no-ff)
2. Criar branch `feat/tui-crud-dashboard`
3. Fixture optimization: scope="session" + rollback transacional (ADR-033, BR-TEST-001)
4. Widgets base: ConfirmDialog (BR-TUI-019) + FormModal (BR-TUI-020)
5. CRUD Rotinas via dashboard (BR-TUI-016), Hábitos (BR-TUI-017), Tarefas (BR-TUI-018)
6. Refatorações R1-R5 aplicadas incrementalmente durante cada entrega

**Refatorações em andamento (fundamentadas em literatura):**

| ID  | Refatoração                  | Referência                       | Sprint |
| --- | ---------------------------- | -------------------------------- | ------ |
| R1  | DI nos widgets TUI           | HUMBLE; FARLEY, 2010, p. 179     | 4      |
| R2  | Mock services nos testes TUI | HUMBLE; FARLEY, 2010, p. 180-183 | 4      |
| R3  | Minimizar estado nos testes  | HUMBLE; FARLEY, 2010, p. 183-184 | 4      |
| R5  | Service Layer como boundary  | FOWLER, 2002, p. 133             | 4      |
| R7  | Rollback transacional        | HUMBLE; FARLEY, 2010, p. 375     | 4.0    |
| R8  | Pipeline < 10min             | HUMBLE; FARLEY, 2010, p. 185     | Monit. |
| R4  | Abstração de tempo           | HUMBLE; FARLEY, 2010, p. 184     | 5      |
| R6  | Repository pattern           | FOWLER, 2002, p. 322             | v2.0   |

**Teste e validação da dashboard (Sprint futuro):**

- Checklist de teste manual: `docs/testing/manual-testing-checklist.md` (94 cenários, 9 seções)
- Automação visual planejada: script pexpect + asciinema que lança a app num pseudo-terminal, executa cada fluxo com delays visíveis, e grava um `.cast` reproduzível. Permite que qualquer pessoa assista uma sessão completa de validação da TUI com `asciinema play`. Substitui validação manual repetitiva por gravação determinística.
- Smoke tests via pexpect: app abre, renderiza, responde a input básico — complementa testes e2e com pilot (ADR-037).

**Features futuras planejadas (v1.8.0+):**

- **RapidLog:** Captura rápida de notas, tarefas e eventos em formato livre — inspirado no Bullet Journal (CARROLL, 2018). Input de texto livre no dashboard que classifica automaticamente (task, note, event) via prefixo ou parsing. Reduz fricção de entrada: o usuário digita e o sistema organiza.
- **BackLog:** Repositório de itens postergados ou não agendados. Tasks e hábitos que foram adiados múltiplas vezes migram automaticamente para o BackLog. Revisão periódica (semanal/mensal) permite reprojetar, descartar ou reagendar. Integra com postponement_count (BR-TASK-008).
- **Subtasks de Habits:** Modal de checklist interno a cada hábito para um dia específico. O usuário define subtarefas que precisa cumprir dentro daquele hábito naquela instância — lista dentro de lista. Percentual de conclusão das subtarefas alimenta completion_percentage e done_substatus automaticamente. Modelo: HabitSubtask com FK para HabitInstance, campos title + completed.

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

O inventário completo está em `docs/reference/technical-debt.md`. A situação de débito técnico melhorou significativamente: dos 7 itens registrados, 6 estão resolvidos. O único item remanescente (DT-007, migration_001) é aceito como decisão consciente — a migração inicial é monolítica por design e será substituída por migrações incrementais na v2.0.0 quando o schema evoluir para PostgreSQL.

Um novo item de débito técnico foi identificado: o `dashboard.py` com 973 linhas viola SRP e deve ser refatorado em módulos separados (`colors.py`, `formatters.py`, `mock_data.py`). Este refactor está planejado como próximo commit após o fechamento visual.

| Status    | Quantidade | Itens                                                           |
| --------- | ---------- | --------------------------------------------------------------- |
| Resolvido | 58         | DT-001 a DT-068 (exceto aceitos e pendentes)                    |
| Aceito    | 1          | DT-007 (migration_001)                                          |
| Pendente  | 12         | DT-012, DT-019, DT-025, DT-044, DT-058, DT-060, DT-063, DT-065, |
|           |            | DT-067, DT-069, DT-070, DT-071                                  |

Nota: DT-003 (cobertura) resolvido — ~82% supera o threshold atual de 80%. Meta será elevada para 85% após Sprint 3.2 expandir cobertura TUI.

---

## 6. Política de Governança

A governança documental segue o princípio de Single Source of Truth (SSOT): cada tipo de informação tem exatamente um documento autoritativo. Quando há contradição entre documentos, o SSOT do domínio prevalece. ADRs são imutáveis após aceitas — novas decisões que alteram ADRs anteriores referenciam o superseded. Os documentos de TUI Design foram introduzidos como categoria própria para separar artefatos de design visual (mockups, wireframes) da especificação formal (business rules) e das decisões técnicas (ADRs).

### 6.1. Hierarquia de Documentos

```plaintext
SSOT Documents:
├── roadmap.md           => Estado e planejamento
├── business-rules.md    => Regras de negócio (104 BRs)
├── architecture.md      => Decisões técnicas
├── quality-metrics.md   => Métricas operacionais
├── technical-debt.md    => Inventário de débito técnico
└── CHANGELOG.md         => Histórico de releases

ADRs (Imutáveis):
└── docs/decisions/      => 35 decisões arquiteturais

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
| 2026-03-05 | 7.0.0  | Sprint 3.2 DONE, Sprint 4 dashboard-first CRUD (ADR-034),  |
|            |        | 104 BRs, 35 ADRs, refatorações R1-R8 fundamentadas em      |
|            |        | Fowler (2002) e Humble & Farley (2010)                     |
| 2026-04-05 | 8.0.0  | v1.7.0 entregue. Métricas atualizadas: ~1340 testes,       |
|            |        | 47 ADRs, 115+ BRs, 58/71 DTs resolvidos. TUI [DONE].       |

---

- **Próxima revisão:** Release v1.7.1
- **Última atualização:** 5 de Abril de 2026
