# Roadmap

- **Versão:** 1.7.2
- **Status:** Single Source of Truth (SSOT)
- **Documentos relacionados:** architecture.md, business-rules.md, quality-metrics.md, technical-debt.md

---

## Sumário Executivo

ATOMVS Time Planner é uma aplicação CLI/TUI para gerenciamento de tempo baseada em Time Blocking e nos princípios de Atomic Habits. A arquitetura segue o modelo offline-first, priorizando funcionalidade completa sem dependência de rede, com evolução planejada para API REST (v2.x), sincronização distribuída (v3.x) e mobile Android (v4.x).

A v1.7.0 completou a TUI com dashboard interativo, CRUD contextual via modais, timer live, MetricsPanel com streak/heatmap e keybindings padronizados. A v1.7.1 consolidou qualidade: logging completo em todas as camadas, 14 diagramas auditados contra o código, README reescrito, e `technical-debt.md` com 62/73 itens resolvidos (85%).

**Estado Atual (Abril 2026):**

- Versão: v1.7.1 (entregue), v1.7.2 (em desenvolvimento)
- Qualidade: ~82% cobertura (threshold 80%), 0 erros basedpyright (standard), 1345 testes
- Funcionalidade: CLI completa, TUI dashboard interativo com CRUD, timer, métricas
- Infraestrutura: CI/CD dual-repo com Docker, DevSecOps, 7 jobs paralelos
- Documentação: 114 BRs formalizadas, 46 ADRs, 15 diagramas auditados, Diataxis framework

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

| Versão | Data       | Escopo                           | Detalhes     |
| ------ | ---------- | -------------------------------- | ------------ |
| v1.0.0 | 2025-10    | Foundation                       | CHANGELOG.md |
| v1.1.0 | 2025-11    | Core Features                    | CHANGELOG.md |
| v1.2.0 | 2025-11    | Status Refactoring               | CHANGELOG.md |
| v1.3.0 | 2025-12    | Event Reordering (Parcial)       | CHANGELOG.md |
| v1.4.0 | 2026-01    | Mypy Zero, Services Complete     | CHANGELOG.md |
| v1.4.1 | 2026-01    | E2E Tests, Quality Metrics       | CHANGELOG.md |
| v1.5.0 | 2026-02    | CI/CD Dual-Repo, i18n            | CHANGELOG.md |
| v1.6.0 | 2026-02    | Docker, DevSecOps, 87% cobertura | CHANGELOG.md |
| v1.7.0 | 2026-04-05 | TUI Completa, 1340+ testes       | CHANGELOG.md |
| v1.7.1 | 2026-04-09 | Consolidação, Logging, Docs      | CHANGELOG.md |

O detalhamento de métricas por release está disponível em `docs/reference/quality-metrics.md`.

---

## 3. Estado Atual

### 3.1. Métricas Principais

Métricas medidas em 2026-04-08, branch `chore/v1.7.1-release-prep`.

| Métrica             | Valor | Meta  | Status |
| ------------------- | ----- | ----- | ------ |
| Cobertura           | ~82%  | 80%   | [OK]   |
| Erros basedpyright  | 0     | 0     | [OK]   |
| Testes totais       | 1345  | 1200+ | [OK]   |
| BRs formalizadas    | 114   | 110+  | [OK]   |
| ADRs documentados   | 46    | 35+   | [OK]   |
| Diagramas auditados | 15    | 15    | [OK]   |
| DTs resolvidos      | 62/73 | —     | 85%    |

### 3.2. Distribuição de Testes

```plaintext
Unit:        ~990 (74%)
Integration: ~150 (11%)
BDD:           83 (6%)
E2E:          ~117 (9%)
─────────────────────────
TOTAL:       ~1345 testes
```

### 3.3. Infraestrutura CI/CD

O GitLab é a fonte de verdade com pipeline de 7 jobs em 4 stages. O GitHub recebe sincronização automática via GitLab Push Mirroring e executa validação espelho. Branches `develop` e `main` são protegidas — todas as mudanças entram via MR com pipeline verde.

```plaintext
GitLab CI: 7 jobs (test:unit + test:integration + test:e2e + coverage:report + lint + test:typecheck + security:deps + security:bandit)
GitHub: Push Mirroring automático, Dependabot para CVEs
Pipeline time: ~28min (e2e é o gargalo)
Pre-push hook: suite completa antes de cada push
```

### 3.4. Débito Técnico

O inventário completo e detalhamento estão em `docs/reference/technical-debt.md` (SSOT). Resumo de alto nível:

| Status          | Quantidade | Percentual |
| --------------- | ---------- | ---------- |
| Resolvidos      | 62         | 85%        |
| Pendentes       | 5          | 7%         |
| Reclassificados | 5          | 7%         |
| Aceitos         | 1          | 1%         |
| **Total**       | **73**     | —          |

Os 5 DTs reclassificados foram promovidos a features no roadmap v1.8.0 (DT-019, DT-060, DT-063, DT-065, DT-069). Os 5 pendentes são: DT-012 (DI inconsistente, v2.0), DT-025 (Pyright CI, v2.0), DT-044 (basedpyright strict, v2.0), DT-071 (padrão header/footer docs), DT-073 (`__pycache__` portabilidade).

---

## 4. Roadmap Futuro

### v1.7.0 — TUI Completa (Entregue — 2026-04-05)

A introdução da TUI com Textual marcou a transição de ferramenta de linha de comando pura para aplicação interativa completa. A TUI e a CLI coexistem: a CLI permanece como interface para automação e scripts, enquanto a TUI oferece navegação visual para uso interativo. O design segue a paleta Catppuccin Mocha com sistema de cores semânticas (ADR-021) e keybindings padronizados (ADR-035/037).

Entregas: dashboard com 5 painéis (Agenda, Habits, Tasks, Timer, Metrics), CRUD contextual via modais (ADR-034), quick actions via message pattern, timer live com `set_interval`, MetricsPanel com streak/heatmap (BR-TUI-033), 61 cenários BDD, 117 testes e2e com snapshot testing.

### v1.7.1 — Consolidação e Qualidade (Entregue — 2026-04-09)

Release focada em observabilidade, documentação técnica e housekeeping. Sem features novas — apenas qualidade e preparação para v1.8.0.

| Entrega                             | MR/Branch                 |
| ----------------------------------- | ------------------------- |
| Logging completo (6 camadas)        | MR !73                    |
| 14 diagramas auditados + README     | MR !72                    |
| 5 DTs reclassificados como features | MR !74                    |
| Snapshots atualizados               | chore/v1.7.1-release-prep |
| `technical-debt.md` reorganizado    | chore/v1.7.1-release-prep |
| Dev deps corrigidas (pyproject)     | chore/v1.7.1-release-prep |
| CONTRIBUTING.md e SECURITY.md       | chore/v1.7.1-release-prep |

### v1.7.2 — Polish Visual e Correções Urgentes (Planejado)

Release focada em correções de bugs descobertos em uso real do dashboard e polish visual. Primeira release planejada inteiramente via GitLab Issues (milestone v1.7.2, 11 issues). O tracking migrou de `technical-debt.md` + `sprints.md` para GitLab Issues com labels estruturadas e milestones — decisão documentada no handoff da Sessão 19.

| Issue | Título                                              | Tipo    | Prioridade |
| ----- | --------------------------------------------------- | ------- | ---------- |
| #5    | TimerPanel não converte >60min para H:MM:SS         | bug     | high       |
| #36   | Impossível iniciar nova sessão em habit já done     | bug     | high       |
| #33   | Header exibe placeholders em vez de dados dinâmicos | bug     | high       |
| #1    | update não propaga horários para instâncias         | bug     | high       |
| #2    | generate cria duplicatas                            | bug     | high       |
| #30   | Corrigir title/subtitle no header                   | bug     | medium     |
| #31   | Reordenar panels (timer > habits > tasks > metrics) | feature | medium     |
| #29   | Remover hint do TimerPanel                          | feature | low        |
| #32   | Footer — cores dos hints e margem inferior          | feature | low        |
| #34   | Remover régua no AgendaPanel                        | feature | low        |
| #11   | DT-073: **pycache** paths absolutos                 | debt    | low        |

**Critérios de release:** pipeline verde (8 jobs), 0 erros basedpyright standard, todos os testes passando, sem regressão visual nos snapshots e2e.

### v1.8.0 — Agenda, Sidebar e UX (Planejado)

Foco em tornar a TUI confortável para uso diário prolongado. Inclui features anteriormente registradas como débito técnico (DT-019, DT-060, DT-063, DT-065, DT-069) que foram reclassificadas — são funcionalidades novas, não dívida.

| Feature                       | Origem  | Descrição                                                                                          | Dependência         |
| ----------------------------- | ------- | -------------------------------------------------------------------------------------------------- | ------------------- |
| AgendaPanel scroll horizontal | DT-061  | Separar margem de horas do conteúdo, `ScrollableContainer` com `scroll_x`                          | ADR-041             |
| Blocos de tempo contínuos     | DT-062  | Accent bar + cor sólida, sem linhas cortando blocos                                                | ADR-041             |
| Paginação de dias             | DT-063  | Setas para navegar -3/+3 dias, `0`/`Home` retorna ao hoje                                          | ADR-041, BR-TUI-030 |
| Sidebar redesign              | DT-060  | Tabs horizontais no header ou modo oculto (zero cols perdidas)                                     | ADR-042             |
| Layout adaptativo             | DT-065  | >=120 cols (2 colunas), 80-119 (1 coluna com scroll/tabs), <80 (aviso)                             | —                   |
| Command Bar                   | DT-019  | Barra de comandos com prefixo `/` ou `Ctrl+P`                                                      | —                   |
| Settings screen               | DT-069  | Tela de configurações: tema, atalhos, caminho do banco, formato de hora                            | —                   |
| Rename repositório            | —       | `atomvs-timeblock-terminal` → `atomvs-timeplanner-terminal` (GitLab, GitHub, Mirroring, URLs, etc) | ADR-045             |
| Rename src/                   | ADR-045 | `src/timeblock/` → `src/atomvs/` (481 imports em 161 arquivos)                                     | Rename repo         |
| Backup do banco               | #22     | Fase 1: CLI `atomvs backup/restore`, Fase 2: automático na inicialização                           | —                   |
| Rastreamento de pausas        | #21     | Fase 1: modal no resume com nota/tag, Fase 2: atribuição retroativa a habit/task                   | ADR-049, PauseLog   |
| Feature toggles               | #28     | Runtime config via SQLite ou TOML para ocultar features incompletas                                | ADR-048             |

**Features candidatas (v1.8.0+ ou v1.9.0):**

- **RapidLog:** Captura rápida de notas, tarefas e eventos em formato livre — inspirado no Bullet Journal (CARROLL, 2018). Input de texto livre no dashboard que classifica automaticamente (task, note, event) via prefixo ou parsing.
- **BackLog:** Repositório de itens postergados ou não agendados. Tasks e hábitos adiados múltiplas vezes migram automaticamente. Revisão periódica permite reprojetar, descartar ou reagendar. Integra com `postponement_count` (BR-TASK-008).
- **Subtasks de Habits:** Modal de checklist interno a cada instância de hábito. Percentual de conclusão das subtarefas alimenta `completion_percentage` e `done_substatus` automaticamente.

### v2.0.0 — REST API (Q2 2026)

A migração para API REST representa a mudança arquitetural mais significativa do projeto: separação entre frontend e backend, autenticação, e persistência em banco de dados relacional. A camada de services já existente — validada por 1345 testes e consumida tanto pela CLI quanto pela TUI — será exposta via endpoints RESTful, minimizando o risco de regressão na lógica de negócio.

Inclui também: rename `src/timeblock/` → `src/atomvs/` (ADR-045), unificação de DI nos services (DT-012), upgrade basedpyright para strict (DT-044), Pyright como job CI (DT-025).

**Stack:** FastAPI + PostgreSQL + JWT + Prometheus

Ver: `architecture.md` seção 9.2

### v3.0.0 — Sync (Q3 2026)

Camada de sincronização para múltiplos dispositivos. Modelo event-driven com resolução de conflitos. O aplicativo permanece funcional sem conectividade (offline-first como fundação).

O parking lot de **analytics temporal** (issue #49) — agregações estatísticas sobre `TimeLog` para sugestão de horário ótimo por hábito — está registrado nesta faixa, formalizando a linha "IA para prever melhores horários" já prevista em ADR-011.

**Stack:** Kafka + CloudEvents + Conflict Resolution

Ver: `architecture.md` seção 9.3

### v4.0.0 — Mobile (Q4 2026)

Cliente Android consumindo a mesma API REST e participando do mesmo protocolo de sync.

**Stack:** Kotlin + Jetpack Compose + Room

Ver: `architecture.md` seção 9.4

---

## 5. Política de Governança

A governança documental segue o princípio de Single Source of Truth (SSOT): cada tipo de informação tem exatamente um documento autoritativo. Quando há contradição entre documentos, o SSOT do domínio prevalece. ADRs são imutáveis após aceitas — novas decisões que alteram ADRs anteriores referenciam o superseded.

### 5.1. Hierarquia de Documentos

```plaintext
SSOT Documents:
├── roadmap.md           => Estado e planejamento
├── business-rules.md    => Regras de negócio (114 BRs)
├── architecture.md      => Decisões técnicas
├── quality-metrics.md   => Métricas operacionais
├── technical-debt.md    => Inventário de débito técnico
└── CHANGELOG.md         => Histórico de releases

ADRs (Imutáveis):
└── docs/decisions/      => 46 decisões arquiteturais

Documentação (Diataxis):
├── docs/tutorials/      => Guias passo-a-passo
├── docs/guides/         => How-to guides
├── docs/reference/      => Especificações e referência
├── docs/explanation/    => Contexto e decisões
└── docs/diagrams/       => 15 diagramas Mermaid auditados
```

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

---

- **Próxima revisão:** Release v1.7.2
- **Última atualização:** 9 de Abril de 2026
