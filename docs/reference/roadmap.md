# Roadmap

- **Versão:** 10.0.0
- **Status:** Single Source of Truth (SSOT)
- **Documentos relacionados:** architecture.md, business-rules/, quality-metrics.md, technical-debt.md, sprints.md

---

## Sumário Executivo

ATOMVS Time Planner é uma aplicação CLI/TUI para gerenciamento de tempo baseada em Time Blocking e nos princípios de Atomic Habits. A arquitetura segue o modelo offline-first, priorizando funcionalidade completa sem dependência de rede, com evolução planejada para API REST (v2.x), sincronização distribuída (v3.x) e mobile Android (v4.x).

A v1.7.0 completou a TUI com dashboard interativo, CRUD contextual via modais, timer live, MetricsPanel com streak/heatmap e keybindings padronizados. A v1.7.1 consolidou qualidade: logging completo em todas as camadas, 14 diagramas auditados contra o código, README reescrito, e `technical-debt.md` com 62/73 itens resolvidos. A v1.7.2 entregou polish visual e correções urgentes de UX descobertas em uso real do dashboard via onze issues no GitLab. A v1.7.3 fechou três fixes críticos: vazamento de logs na TUI (#48), idempotência do `generate` de instâncias (#2) e unificação da declaração de versão entre `pyproject.toml` e `__init__.py` via `importlib.metadata`.

**Estado Atual (Maio 2026):**

- Versão: v1.7.3 (entregue 2026-05-01), v1.7.4 e v1.7.5 com escopo aberto no GitLab
- Qualidade: ~82% cobertura (threshold 80%), 0 erros basedpyright (standard), 1.402 testes (1.119 unit + 115 integration + 89 e2e + 79 bdd)
- Funcionalidade: CLI completa, TUI dashboard interativo com CRUD, timer, métricas
- Infraestrutura: CI/CD dual-repo com Docker, DevSecOps, 8 jobs paralelos, GitLab Push Mirroring para GitHub
- Documentação: 102 BRs únicas formalizadas em 15 domínios, 51 ADRs ativos mais 2 arquivados, 15 diagramas auditados, Diataxis + arc42

---

## 1. Visão de Produto

### 1.1. Evolução Arquitetural

A estratégia de evolução segue um modelo incremental onde cada versão major adiciona uma camada de capacidade sem descartar as anteriores. A CLI permanece funcional mesmo após a introdução da TUI e da API, garantindo que automações e scripts existentes não sejam quebrados. Essa coexistência de interfaces reflete a filosofia de que diferentes contextos de uso demandam diferentes modalidades de interação: scripts e pipelines usam a CLI, o trabalho diário interativo usa a TUI, e integrações externas usarão a API.

```plaintext
v1.5 CI/CD => v1.6 Docker/DevSecOps => v1.7 TUI => v2.x API => v3.x Sync => v4.x Mobile
```

A TUI consome os mesmos services que a CLI — nenhuma lógica de negócio é duplicada — o que valida a arquitetura de camadas antes de expô-la via API REST. Detalhes em: `architecture.md` seção 9 (Evolução Futura).

O projeto adota o branding ATOMVS com namespace `atomvs-timeblock-*` para o ecossistema multi-repo. Detalhes em: ADR-032. Rename planejado para `atomvs-timeplanner-terminal` na v1.8.0 (ADR-045).

### 1.2. Princípios de Desenvolvimento

Estes princípios guiam todas as decisões técnicas e de produto. Não são aspiracionais — são critérios de aceite aplicados em cada commit, verificados automaticamente pelo pipeline CI/CD e pelos pre-commit hooks.

1. **Offline-First:** Funcionalidade completa sem rede
2. **User Control:** Sistema propõe, usuário decide
3. **Quality First:** 80% cobertura, zero erros basedpyright (standard) em produção
4. **Engenharia de Requisitos:** BRs formalizadas antes da implementação (ISO/IEC/IEEE 29148:2018, SWEBOK v4.0)

---

## 2. Releases Entregues

Cada versão expandiu funcionalidade enquanto manteve ou melhorou métricas de qualidade. A trajetória demonstra um padrão disciplinado: fundação sólida primeiro (models, services, testes), infraestrutura robusta depois (CI/CD, Docker, DevSecOps), e só então interfaces ricas (TUI).

| Versão | Data       | Escopo                            | Detalhes     |
| ------ | ---------- | --------------------------------- | ------------ |
| v1.0.0 | 2025-10    | Foundation                        | CHANGELOG.md |
| v1.1.0 | 2025-11    | Core Features                     | CHANGELOG.md |
| v1.2.0 | 2025-11    | Status Refactoring                | CHANGELOG.md |
| v1.3.0 | 2025-12    | Event Reordering (Parcial)        | CHANGELOG.md |
| v1.4.0 | 2026-01    | Mypy Zero, Services Complete      | CHANGELOG.md |
| v1.4.1 | 2026-01    | E2E Tests, Quality Metrics        | CHANGELOG.md |
| v1.5.0 | 2026-02    | CI/CD Dual-Repo, i18n             | CHANGELOG.md |
| v1.6.0 | 2026-02    | Docker, DevSecOps, 87% cobertura  | CHANGELOG.md |
| v1.7.0 | 2026-04-05 | TUI Completa, 1340+ testes        | CHANGELOG.md |
| v1.7.1 | 2026-04-09 | Consolidação, Logging, Docs       | CHANGELOG.md |
| v1.7.2 | 2026-04-13 | Polish Visual e Bugfixes Urgentes | CHANGELOG.md |
| v1.7.3 | 2026-05-01 | Logger Leak, Idempotência, Versão | CHANGELOG.md |

O detalhamento de métricas por release está disponível em `docs/reference/quality-metrics.md`.

---

## 3. Estado Atual

### 3.1. Métricas Principais

Métricas medidas em 2026-05-01, branch `develop` no commit `2a90333` (tag `v1.7.3`).

| Métrica             | Valor        | Meta  | Status |
| ------------------- | ------------ | ----- | ------ |
| Cobertura           | ~82%         | 80%   | [OK]   |
| Erros basedpyright  | 0 (standard) | 0     | [OK]   |
| Testes totais       | 1.402        | 1200+ | [OK]   |
| BRs únicas          | 102          | 100+  | [OK]   |
| ADRs documentados   | 51 + 2 arq.  | 35+   | [OK]   |
| Diagramas auditados | 15           | 15    | [OK]   |
| DTs resolvidos      | 62/74        | —     | 84%    |

### 3.2. Distribuição de Testes

```plaintext
Unit:        1.119 (80%)
Integration:   115 (8%)
E2E:            89 (6%)
BDD:            79 (6%)
─────────────────────────
TOTAL:       1.402 testes
```

A pirâmide está aderente ao padrão do projeto (unit 70-75%, integration ~20%, e2e 5-10%), com BDD operando como camada paralela de documentação executável.

### 3.3. Infraestrutura CI/CD

O GitLab é a fonte de verdade com pipeline de oito jobs em quatro stages. O GitHub recebe sincronização automática via GitLab Push Mirroring (Mirror ID 4026663) e executa validação espelho. Branches `develop` e `main` são protegidas — todas as mudanças entram via MR com pipeline verde.

```plaintext
GitLab CI (8 jobs):
  - test:unit + test:integration + test:e2e
  - coverage:report + lint + test:typecheck
  - security:deps + security:bandit
GitHub: Push Mirroring automático, Dependabot para CVEs
Pipeline time: ~28min (e2e é o gargalo)
Pre-push hook: suite completa antes de cada push
```

### 3.4. Débito Técnico

O inventário completo e detalhamento estão em `docs/reference/technical-debt.md` (SSOT). A v2.34.0 incorpora a entrada formal DT-074 (BRs e Humble Objects sem cobertura), DT-075 (BR fantasma BR-EVENT-002), DT-076 (TimerScreen placeholder) e DT-077 (drift histórico de versão entre `pyproject.toml` e `__init__.py` — registrado como resolvido em v1.7.3 para fechar o ciclo de auditoria do structural-assessment).

| Status          | Quantidade | Percentual |
| --------------- | ---------- | ---------- |
| Resolvidos      | 64         | 83%        |
| Pendentes       | 7          | 9%         |
| Reclassificados | 5          | 6%         |
| Aceitos         | 1          | 1%         |
| **Total**       | **77**     | —          |

Os 5 DTs reclassificados foram promovidos a features no roadmap v1.8.0 (DT-019, DT-060, DT-063, DT-065, DT-069). Os 7 pendentes são: DT-012 (DI inconsistente, v2.0), DT-025 (Pyright CI, v2.0), DT-044 (basedpyright strict, v2.0), DT-071 (padrão header/footer docs), DT-073 (`__pycache__` portabilidade), DT-074 (cobertura BR/Humble Objects, em resolução desde v1.7.2), DT-075 (BR fantasma) e DT-076 (TimerScreen placeholder).

---

## 4. Roadmap Futuro

### v1.7.0 — TUI Completa (Entregue — 2026-04-05)

A introdução da TUI com Textual marcou a transição de ferramenta de linha de comando pura para aplicação interativa completa. A TUI e a CLI coexistem: a CLI permanece como interface para automação e scripts, enquanto a TUI oferece navegação visual para uso interativo. O design segue a paleta Catppuccin Mocha com sistema de cores semânticas (ADR-021) e keybindings padronizados (ADR-035/037).

Entregas: dashboard com 5 painéis (Agenda, Habits, Tasks, Timer, Metrics), CRUD contextual via modais (ADR-034), quick actions via message pattern, timer live com `set_interval`, MetricsPanel com streak/heatmap (BR-TUI-033), 61 cenários BDD, 117 testes e2e com snapshot testing.

### v1.7.1 — Consolidação e Qualidade (Entregue — 2026-04-09)

Release focada em observabilidade, documentação técnica e housekeeping. Sem features novas — apenas qualidade e preparação para v1.8.0.

### v1.7.2 — Polish Visual e Correções Urgentes (Entregue — 2026-04-13)

Primeira release planejada inteiramente via GitLab Issues (milestone v1.7.2, onze issues). O tracking migrou de `technical-debt.md` + `sprints.md` para GitLab Issues com labels estruturadas e milestones — decisão documentada no handoff da Sessão 19. Fechou os bugs críticos do dashboard (#5, #36, #33, #1) e batch de polish visual (#29, #30, #31, #32, #34, #11). Tag em `7218bb0`.

### v1.7.3 — Logger, Idempotência e Versão (Entregue — 2026-05-01)

Release de escopo enxuto com três fixes em categoria `Fixed`. Tag anotada em `2a90333`, fast-forward merge sem merge commit.

| Issue | Título                                              | Tipo |
| ----- | --------------------------------------------------- | ---- |
| #48   | Logger leak na TUI (BR-OBS-001 R11-12)              | bug  |
| #2    | `generate_instances` cria duplicatas (BR-HABIT-003) | bug  |
| —     | Unificação `__version__` via `importlib.metadata`   | bug  |

A correção do `__version__` resolve drift histórico desde a fundação do projeto: `pyproject.toml` declarava `1.7.2` e `__init__.py` declarava `0.1.0` (placeholder bootstrap). A unificação eliminou a duplicação refatorando `__init__.py` para ler via `importlib.metadata.version("atomvs-timeblock-terminal")`.

### v1.7.4 — Padronização Documental e Snapshots (Planejado)

Milestone aberta no GitLab, escopo focado em débito documental e estabilidade de testes visuais. Não há tag prevista — pode ser absorvida por v1.7.5 caso o escopo se mantenha pequeno.

| Issue | Título                                          | Tipo | Prioridade |
| ----- | ----------------------------------------------- | ---- | ---------- |
| #10   | DT-071: padrão de header/footer em documentação | debt | low        |
| #51   | ADR-020 desatualizado vs implementação corrente | debt | low        |
| #54   | Snapshots e2e flaky em ambiente CI              | bug  | medium     |
| #55   | CVE bump em pytest                              | sec  | medium     |

### v1.7.5 — Bugs e Cobertura Pendente (Planejado)

| Issue | Título                                               | Tipo | Prioridade |
| ----- | ---------------------------------------------------- | ---- | ---------- |
| #42   | DT-074: BRs e Humble Objects sem cobertura           | debt | high       |
| #43   | TasksPanel ordem incorreta de exibição               | bug  | medium     |
| #62   | Keybinding `x` (cancel) com comportamento divergente | bug  | medium     |

### v1.8.0 — Agenda, Sidebar, Archive Lifecycle e UX (Planejado)

Foco em tornar a TUI confortável para uso diário prolongado. Inclui features anteriormente registradas como débito técnico (DT-019, DT-060, DT-063, DT-065, DT-069) que foram reclassificadas — são funcionalidades novas, não dívida — e absorve a issue #61 reescopada para archive lifecycle de Habit.

| Feature                       | Origem  | Descrição                                                                                               | Dependência             |
| ----------------------------- | ------- | ------------------------------------------------------------------------------------------------------- | ----------------------- |
| AgendaPanel scroll horizontal | DT-061  | Separar margem de horas do conteúdo, `ScrollableContainer` com `scroll_x`                               | ADR-041                 |
| Blocos de tempo contínuos     | DT-062  | Accent bar + cor sólida, sem linhas cortando blocos                                                     | ADR-041                 |
| Paginação de dias             | DT-063  | Setas para navegar -3/+3 dias, `0`/`Home` retorna ao hoje                                               | ADR-041, BR-TUI-030     |
| Sidebar redesign              | DT-060  | Tabs horizontais no header ou modo oculto (zero cols perdidas)                                          | ADR-042                 |
| Layout adaptativo             | DT-065  | >=120 cols (2 colunas), 80-119 (1 coluna com scroll/tabs), <80 (aviso)                                  | —                       |
| Command Bar                   | DT-019  | Barra de comandos com prefixo `/` ou `Ctrl+P`                                                           | —                       |
| Settings screen               | DT-069  | Tela de configurações: tema, atalhos, caminho do banco, formato de hora                                 | —                       |
| Rename repositório            | —       | `atomvs-timeblock-terminal` → `atomvs-timeplanner-terminal` (GitLab, GitHub, Mirroring, URLs, etc)      | ADR-045                 |
| Rename src/                   | ADR-045 | `src/timeblock/` → `src/atomvs/` (481 imports em 161 arquivos)                                          | Rename repo             |
| Backup do banco               | #22     | Fase 1: CLI `atomvs backup/restore`, Fase 2: automático na inicialização                                | —                       |
| Rastreamento de pausas        | #21     | Fase 1: modal no resume com nota/tag, Fase 2: atribuição retroativa a habit/task                        | ADR-049, PauseLog       |
| Feature toggles               | #28     | Runtime config via SQLite ou TOML para ocultar features incompletas                                     | ADR-048                 |
| Archive lifecycle Habit       | #61     | Soft delete via `archived_at`, comando `purge_habit` para hard delete; preserva HabitInstance e TimeLog | nova ADR + BR-HABIT-006 |
| Reconciliação main↔develop    | #64     | Resolver divergência Gitflow (CVE Mako + refactor syrupy em main não merged-back)                       | —                       |

**Features candidatas (v1.8.0+ ou v1.9.0):**

- **RapidLog:** Captura rápida de notas, tarefas e eventos em formato livre — inspirado no Bullet Journal (CARROLL, 2018). Input de texto livre no dashboard que classifica automaticamente (task, note, event) via prefixo ou parsing.
- **BackLog:** Repositório de itens postergados ou não agendados. Tasks e hábitos adiados múltiplas vezes migram automaticamente. Revisão periódica permite reprojetar, descartar ou reagendar. Integra com `postponement_count` (BR-TASK-008).
- **Subtasks de Habits:** Modal de checklist interno a cada instância de hábito. Percentual de conclusão das subtarefas alimenta `completion_percentage` e `done_substatus` automaticamente.

### v2.0-alpha — Refactoring Fase 1 (Planejado)

Materialização das três primeiras camadas do plano de refactoring derivado da avaliação arquitetural sob SRP/SOLID de abril/2026 (mantida em `docs/wiki/assessments/` por ter natureza de diagnóstico temporal — ver decisão de governança da Sessão 29). Operação não-funcional com cobertura de testes preservada como rede de segurança.

| Camada | Escopo                                              | ADR/RF          |
| ------ | --------------------------------------------------- | --------------- |
| 1      | Uniformização Service Pattern (4 services afetados) | ADR-053         |
| 2      | Schedulable Protocol + SchedulableKind enum         | ADR-054, RF-018 |
| 5      | Extração de regras puras de utils/validators.py     | ADR-055         |

A errata sobre `TaskService` (assessment v1.1.0) está incorporada — escopo da Camada 1 cobre `TimerService`, `HabitInstanceService`, `EventReorderingService` e `TaskService`.

### v2.0-beta — Refactoring Fase 2 (Planejado)

Camadas 3 e 4 do plano de refactoring (extração de repository layer no `dashboard/loader.py`, splits do `TimerService` por responsabilidade), preparando para v2.0.0.

### v2.0.0 — REST API (Planejado)

A migração para API REST representa a mudança arquitetural mais significativa do projeto: separação entre frontend e backend, autenticação, e persistência em banco de dados relacional. A camada de services já existente — validada por mais de 1.400 testes e consumida tanto pela CLI quanto pela TUI — será exposta via endpoints RESTful, minimizando o risco de regressão na lógica de negócio.

Inclui também: rename `src/timeblock/` → `src/atomvs/` (ADR-045) caso não tenha sido executado em v1.8.0, unificação de DI nos services (DT-012), upgrade basedpyright para strict (DT-044), Pyright como job CI (DT-025).

**Stack:** FastAPI + PostgreSQL + JWT + Prometheus

Ver: `architecture.md` seção 9.2

### v3.0.0 — Sync (Planejado)

Camada de sincronização para múltiplos dispositivos. Modelo event-driven com resolução de conflitos. O aplicativo permanece funcional sem conectividade (offline-first como fundação).

O parking lot de **analytics temporal** (issue #49) — agregações estatísticas sobre `TimeLog` para sugestão de horário ótimo por hábito — está registrado nesta faixa, formalizando a linha "IA para prever melhores horários" já prevista em ADR-011.

**Stack:** Kafka + CloudEvents + Conflict Resolution

Ver: `architecture.md` seção 9.3

### v4.0.0 — Mobile (Planejado)

Cliente Android consumindo a mesma API REST e participando do mesmo protocolo de sync.

**Stack:** Kotlin + Jetpack Compose + Room

Ver: `architecture.md` seção 9.4

---

## 5. Política de Governança

A governança documental segue o princípio de Single Source of Truth (SSOT): cada tipo de informação tem exatamente um documento autoritativo. Quando há contradição entre documentos, o SSOT do domínio prevalece. ADRs são imutáveis após aceitas — novas decisões que alteram ADRs anteriores referenciam o superseded.

Desde a Sessão 19 (2026-04), o tracking operacional de trabalho corrente migrou para GitLab Issues com milestones. O `technical-debt.md` permanece como SSOT para débito técnico acumulado e decisões de governança de longo prazo. O `sprints.md` foi descontinuado como SSOT operacional e mantido apenas como registro histórico — a v1.7.4+ não recebe entradas formais de sprint, e a declaração de descontinuação está no próprio cabeçalho do documento.

### 5.1. Hierarquia de Documentos

```plaintext
SSOT Documents:
├── roadmap.md           => Estado e planejamento de longo prazo
├── business-rules/      => Regras de negócio (15 domínios, 102 BRs únicas)
├── architecture.md      => Decisões técnicas
├── quality-metrics.md   => Métricas operacionais
├── technical-debt.md    => Inventário de débito técnico acumulado
├── CHANGELOG.md         => Histórico de releases (inglês)
└── GitLab Issues        => Tracking operacional corrente (milestones v1.7.4+)

ADRs (Imutáveis após aceitas):
└── docs/decisions/      => 51 decisões ativas + 2 arquivadas

Documentação (Diataxis + arc42):
├── docs/tutorials/      => Guias passo-a-passo
├── docs/guides/         => How-to guides
├── docs/reference/      => Especificações e referência
├── docs/explanation/    => Contexto e decisões
└── docs/diagrams/       => 15 diagramas Mermaid auditados
```

### 5.2. Análises Estruturais Periódicas

Os assessments arquiteturais (avaliação sob SRP/SOLID de abril/2026 v1.1.0 com errata sobre `TaskService`, e análise estrutural de 1º de maio de 2026 v1.0.0) compõem a base de diagnóstico e são mantidos em `docs/wiki/assessments/` em vez de versionados sob `docs/reference/`. A decisão (Sessão 29) reconhece que assessments têm natureza de diagnóstico temporal — capturam um snapshot da base num commit específico — e versioná-los criaria atrito de manutenção a cada resolução de achado, sem agregar SSOT real (os achados acionáveis já são representados em DTs, ADRs e issues). Análises subsequentes podem aproveitar estes documentos como ponto de partida e devem ser nomeadas no padrão `<tipo>-assessment-<YYYY-MM-DD>-<foco>.md`.

---

## 6. Changelog do Documento

| Data       | Versão | Mudanças                                                                    |
| ---------- | ------ | --------------------------------------------------------------------------- |
| 2026-01-14 | 1.0.0  | Criação inicial                                                             |
| 2026-01-16 | 2.0.0  | Reformulação profissional                                                   |
| 2026-01-16 | 2.1.0  | Remoção de duplicações, referências a docs externos                         |
| 2026-02-01 | 3.0.0  | Atualização com dados reais, retrospectiva v1.4.0                           |
| 2026-02-03 | 4.0.0  | v1.5.0 entregue, replanejar v1.6.0 cobertura, v1.7.0 TUI                    |
| 2026-02-20 | 5.0.0  | v1.6.0 entregue, v1.7.0 TUI em desenvolvimento                              |
| 2026-02-23 | 6.0.0  | ADR-021 integrado, 1071 testes, mock data, próximos passos                  |
| 2026-03-05 | 7.0.0  | Sprint 3.2 DONE, Sprint 4 dashboard-first CRUD (ADR-034)                    |
| 2026-04-05 | 8.0.0  | v1.7.0 entregue. 1340+ testes, 47 ADRs, 115+ BRs, TUI [DONE]                |
| 2026-04-08 | 9.0.0  | Reescrita estrutural: v1.7.1 documentada, seção de débito técnico           |
|            |        | consolidada como referência ao SSOT, métricas atualizadas, v1.8.0 detalhada |
| 2026-05-01 | 10.0.0 | v1.7.2 e v1.7.3 absorvidas. Métricas atualizadas (1.402 testes, 102 BRs,    |
|            |        | 51 ADRs). v1.7.4 e v1.7.5 detalhadas com escopo de issues abertas. v1.8.0   |
|            |        | absorve archive lifecycle (#61) e reconciliação main/develop (#64).         |
|            |        | Política de governança atualizada para refletir migração para GitLab Issues |
|            |        | (Sessão 19) e descontinuação operacional do sprints.md.                     |

---

- **Próxima revisão:** Após v1.7.4 entregue
- **Última atualização:** 1 de Maio de 2026
