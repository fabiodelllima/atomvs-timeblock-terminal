# Análise de Débito Técnico — ATOMVS TimeBlock Terminal

**Versão:** 1.0.0

**Status:** HISTORICO — documento congelado, dados migrados para technical-debt.md, quality-metrics.md e snapshot-testing.md

**Data de referência:** 30 de Março de 2026

**Branch analisada:** develop (commit 7463273)

**Documentos fonte:** technical-debt.md v2.25.0 (dados corrigidos para v2.25.0 real: 62 DTs), quality-metrics.md v3.0.0, refactoring-catalog.md v1.0.0, sprints.md v6.0.0, roadmap.md v7.0.0

---

## Parte 1 — Análise

### 1. Resumo Executivo

O projeto ATOMVS TimeBlock Terminal encontra-se em estado de maturidade técnica saudável. De 62 itens de débito técnico catalogados, 46 foram resolvidos (74%), 14 permanecem pendentes (23%) e 1 foi aceito conscientemente (2%). Nenhum item CRÍTICO permanece aberto — todos os 5 CRÍTICOs históricos (DT-034, DT-035, DT-049, DT-054, DT-055) foram resolvidos em Março/2026. Os 16 itens pendentes concentram-se em severidades MÉDIA (9) e BAIXA (7), sem bloqueios para o release v1.7.0.

| Indicador                | Valor        |
| ------------------------ | ------------ |
| Total de DTs registrados | 62           |
| Resolvidos               | 46 (74%)     |
| Pendentes                | 14 (23%)     |
| Aceitos                  | 1 (2%)       |
| Críticos pendentes       | 0            |
| Testes totais            | ~1.320       |
| Cobertura global         | ~82%         |
| Mypy erros               | 0            |
| Basedpyright erros       | 0 (standard) |
| ADRs documentados        | 46           |
| BRs formalizadas         | 110+         |

---

### 2. Evolução Temporal

```
Jan/2026 ─── DT-001 (156 mypy erros) ───── RESOLVIDO
         ─── DT-002 (15 testes skipped) ── RESOLVIDO
         ─── 618 testes, 67% cobertura

Fev/2026 ─── DT-004 (EventReordering 61%) ─ RESOLVIDO
         ─── DT-005 (código morto) ──────── RESOLVIDO
         ─── DT-006 (idioma misto) ──────── RESOLVIDO
         ─── 873 testes, 87% cobertura

Mar/2026 ─── DT-003 (cobertura <80%) ───── RESOLVIDO
         ─── DT-034/035 (CRÍTICOs) ─────── RESOLVIDOS
         ─── DT-049/054/055 (CRÍTICOs) ─── RESOLVIDOS
         ─── DT-045..062 (TUI Phase 1) ─── 18 itens RESOLVIDOS
         ─── ~1.320 testes, ~82% cobertura

Atual ────── 16 pendentes (MÉDIA/BAIXA)
         ─── 0 críticos abertos
```

**Velocidade de resolução:** 53 itens em ~3 meses (Jan–Mar/2026), média de ~18 itens/mês. Pico em Mar/2026 com 30+ resoluções concentradas na TUI Phase 1.

---

### 3. Inventário Pendente (16 itens)

#### 3.1 Agrupamento por Tema

**Infraestrutura e CI (4 itens)**

| ID     | Descrição                               | Severidade | Sprint planejado     |
| ------ | --------------------------------------- | ---------- | -------------------- |
| DT-025 | Pyright como job CI complementar        | BAIXA      | Sprint futuro        |
| DT-044 | basedpyright strict: ~647 warnings      | MÉDIA      | v2.0                 |
| DT-058 | Logging ausente na CLI                  | MÉDIA      | Sprint futuro        |
| DT-064 | CVE-2026-4539 pygments sem fix upstream | BAIXA      | Quando > 2.19.2 sair |

**UX e Visual (6 itens)**

| ID     | Descrição                                 | Severidade | Sprint planejado |
| ------ | ----------------------------------------- | ---------- | ---------------- |
| DT-019 | command_bar.py stub vazio (0 bytes)       | BAIXA      | Sprint 6+        |
| DT-060 | Sidebar ocupa ~15 cols desnecessariamente | MÉDIA      | Sprint futuro    |
| DT-063 | Agenda limitada ao dia atual              | MÉDIA      | Sprint futuro    |
| DT-065 | Responsividade em terminal 80x24          | MÉDIA      | v1.7.0           |
| DT-066 | Placeholders truncados nos panels         | BAIXA      | v1.7.0           |
| DT-069 | Tela de configurações não planejada       | BAIXA      | Sprint futuro    |

**Arquitetura (2 itens)**

| ID     | Descrição                                | Severidade | Sprint planejado |
| ------ | ---------------------------------------- | ---------- | ---------------- |
| DT-012 | DI inconsistente entre services          | MÉDIA      | v2.0             |
| DT-059 | Mensagens de migração visíveis no stdout | MÉDIA      | Sprint futuro    |

**Documentação (2 itens)**

| ID     | Descrição                                | Severidade | Sprint planejado |
| ------ | ---------------------------------------- | ---------- | ---------------- |
| DT-067 | README sem links para ~16 diagramas      | MÉDIA      | v1.7.0           |
| DT-068 | Habits não ordenados por scheduled_start | MÉDIA      | Sprint futuro    |

**Observação:** DT-068 tem fix implementado (commit 7463273) mas ainda não foi marcado como RESOLVIDO no SSOT.

---

### 4. Cruzamento com Refactoring Catalog

O catálogo de refatoração (Fowler, 2018) registra 10 itens (RF-001 a RF-010). Estado atual:

| RF     | Descrição                           | Fowler (2018)                | Status na develop | DT relacionado |
| ------ | ----------------------------------- | ---------------------------- | ----------------- | -------------- |
| RF-001 | Extract Delegate (quick actions)    | Extract Class, p. 182        | Pendente          | —              |
| RF-002 | C_HIGHLIGHT → colors.py             | Extract Variable, p. 119     | RESOLVIDO         | DT-009         |
| RF-003 | Split Phase (data loading)          | Split Phase, p. 154          | Pendente          | —              |
| RF-004 | Remove @staticmethod duplicado      | Remove Dead Code, p. 237     | RESOLVIDO         | —              |
| RF-005 | Dict → dataclass nos panels         | Parameter Object, p. 140     | Pendente          | —              |
| RF-006 | Polimorfismo por status             | Replace Conditional, p. 272  | Adiado (Sprint 6) | —              |
| RF-007 | Empty state centralizado            | Parameterize Function, p.310 | RESOLVIDO         | DT-010/011     |
| RF-008 | Counter em \_refresh_content        | Consolidate Cond., p. 263    | Pendente          | —              |
| RF-009 | Imports lazy eliminados             | Encapsulate Variable, p.132  | RESOLVIDO         | —              |
| RF-010 | Split timer_service.py (549 linhas) | Separate Query/Mod., p. 306  | Adiado (Sprint 5) | —              |

**Resumo:** 4 resolvidos, 4 pendentes, 2 adiados por design.

---

### 5. Gaps de Cobertura

#### 5.1 Cobertura por Módulo

| Módulo    | Cobertura | Status  |
| --------- | --------- | ------- |
| models/   | ~98%      | OK      |
| services/ | ~93%      | OK      |
| tui/      | ~97%      | OK      |
| utils/    | ~99%      | OK      |
| commands/ | ~45%      | ATENÇÃO |
| database/ | ~60%      | ATENÇÃO |

#### 5.2 Business Rules sem Cobertura de Testes

| Domínio | Cobertura  | BRs sem testes                        |
| ------- | ---------- | ------------------------------------- |
| TAG     | 0% (0/2)   | BR-TAG-001, BR-TAG-002                |
| SKIP    | 25% (1/4)  | BR-SKIP-002, BR-SKIP-003, BR-SKIP-004 |
| CLI     | 33% (1/3)  | BR-CLI-001, BR-CLI-003                |
| TUI     | 36% (4/11) | BR-TUI-005 a BR-TUI-011               |

#### 5.3 Anotações no Código

| Tipo         | Quantidade | Observação                               |
| ------------ | ---------- | ---------------------------------------- |
| TODO         | 9          | Todos são features futuras, sem bloqueio |
| type: ignore | 36         | Majoritariamente ORM/SQLAlchemy          |
| Any usage    | 65         | Concentrado na camada TUI (Textual)      |
| Deprecated   | 2          | timer_service, habit_instance_service    |

---

### 6. Qualidade da Documentação

**Pontos Fortes:**

- Modelo SSOT com versionamento em todos os docs
- 46 ADRs imutáveis documentando decisões arquiteturais
- 110+ BRs formalizadas com nomenclatura ISO/IEC/IEEE 29148:2018
- Reestruturação Diátaxis (explanation/, guides/, reference/, tutorials/)
- Referências acadêmicas (Fowler 2018, Humble & Farley 2010)
- Rastreabilidade BR → ADR → Teste → Código

**Gaps:**

- DT-067: 16 diagramas em `docs/diagrams/` sem referência no README e possivelmente desatualizados
- DT-069: Tela de configurações sem BR nem ADR
- quality-metrics.md com data de referência de Fev/2026 (defasado 1 mês)

---

## Parte 2 — Plano de Execução para Finalização da Dashboard TUI (v1.7.0)

### Estratégia de Branches

A finalização da Dashboard TUI para release v1.7.0 está organizada em **3 branches sequenciais** com escopos distintos. A ordem de merge é: testes → validação → release.

```
develop (base)
├── 1. test/c/sprint-5.5-hardening    ← Testes e2e edge-case, remover xfail
│   └── merge → develop
├── 2. fix/c/dashboard-validation     ← DT-065/066/059, checklist manual
│   └── merge → develop
└── 3. chore/c/v1.7.0-release-prep   ← CHANGELOG, version bump, tag
    └── merge → develop → tag v1.7.0
```

---

### Branch 1: `test/c/sprint-5.5-hardening`

**Objetivo:** Completar Sprint 5.5 Phase 5 — test hardening para atingir meta de 1.241+ testes e 0 xfail.

**Commits planejados:**

1. `test(e2e): Modal cancellation — Esc fecha FormModal e ConfirmDialog sem side effects`
   - Arquivos: `tests/e2e/test_dashboard_complete.py`
   - Cenários: Esc em done modal, skip modal, edit modal, delete confirm
   - BRs: BR-TUI-020, BR-TUI-022, BR-TUI-024

2. `test(e2e): Arrow key navigation equivalente a j/k nos panels`
   - Arquivos: `tests/e2e/test_dashboard_complete.py`
   - Cenários: ↑↓ movem cursor em HabitsPanel e TasksPanel
   - BRs: BR-TUI-012

3. `test(e2e): Timer blocking — apenas 1 timer ativo por aplicação`
   - Arquivos: `tests/e2e/test_dashboard_complete.py`
   - Cenários: t em hábito B com timer A ativo → mensagem de bloqueio
   - BRs: BR-TIMER-001

4. `test(unit): Testes para BR-TAG-001 e BR-TAG-002`
   - Arquivos: `tests/unit/test_business_rules/test_br_tag.py`

5. `test(unit): Testes para BR-SKIP-002, BR-SKIP-003, BR-SKIP-004`
   - Arquivos: `tests/unit/test_business_rules/test_br_skip_002.py`, `test_br_skip_003.py`, `test_br_skip_004.py`

6. `test(integration): Testes CliRunner para BR-CLI-001 e BR-CLI-003`
   - Arquivos: `tests/unit/test_business_rules/test_br_cli.py`

7. `test(e2e): Fortalece asserções — substatus, skip_reason, completion_pct em todos os fluxos`
   - Arquivos: `tests/e2e/test_dashboard_complete.py`

8. `fix(test): Remove xfail workarounds remanescentes`
   - Arquivos: `tests/e2e/test_dashboard_complete.py`

**Meta:** ~1.350 testes, 0 xfail (exceto DT-026 aceito)

---

### Branch 2: `fix/c/dashboard-validation`

**Objetivo:** Resolver DTs que afetam a experiência do dashboard e validar cenários do checklist manual.

**Commits planejados:**

1. `fix(tui): Layout adaptativo com breakpoint 120/80 cols (DT-065)`
   - Arquivos: `src/timeblock/tui/screens/dashboard/screen.py`, `src/timeblock/tui/styles/dashboard.tcss`
   - Lógica: >=120 cols → 2 colunas; 80-119 → 1 coluna com scroll; <80 → aviso
   - BRs: BR-TUI-003

2. `test(e2e): Snapshot baseline para layout 80x24 responsivo`
   - Arquivos: `tests/e2e/test_snapshots.py`

3. `fix(tui): Move instruções de placeholder para footer contextual (DT-066)`
   - Arquivos: `src/timeblock/tui/widgets/focusable_panel.py`, `src/timeblock/tui/widgets/status_bar.py`

4. `fix(database): Redireciona output de migrations para logger (DT-059)`
   - Arquivos: `src/timeblock/database/migrations/__init__.py`

5. `docs(debt): Marca DT-068 como RESOLVIDO (commit 7463273)`
   - Arquivos: `docs/reference/technical-debt.md`

6. `docs(audit): Audita 16 diagramas e adiciona links ao README (DT-067)`
   - Arquivos: `docs/diagrams/**/*.md`, `README.md`

**Meta:** 4 DTs resolvidos (DT-059, DT-065, DT-066, DT-067), DT-068 documentado, ~16 cenários do checklist manual validados.

---

### Branch 3: `chore/c/v1.7.0-release-prep`

**Objetivo:** Tarefas mecânicas de release — documentação, versão, tag.

**Commits planejados:**

1. `chore(coverage): Mede e documenta cobertura do pacote tui/ (meta >=80%)`
   - Arquivos: `docs/reference/quality-metrics.md`
   - Ação: `pytest --cov=src/timeblock/tui --cov-report=term-missing`

2. `chore(audit): Quality audit BR-TUI-015 — SOLID, complexidade ciclomática`
   - Arquivos: `docs/reference/quality-metrics.md`
   - Ação: Verificar que nenhum arquivo >500 linhas (exceto timer_service.py aceito), nenhuma função >50 linhas

3. `docs(changelog): Entrada completa v1.7.0 no CHANGELOG.md`
   - Arquivos: `CHANGELOG.md`
   - Seções: Added, Changed, Fixed, Metrics

4. `chore(version): Bump versão para 1.7.0 no pyproject.toml`
   - Arquivos: `pyproject.toml`

5. `docs(roadmap): Marca v1.7.0 como entregue, atualiza métricas`
   - Arquivos: `docs/reference/roadmap.md`

6. `docs(sprints): Move v1.7.0 para sprints-archive.md`
   - Arquivos: `docs/reference/sprints.md`, `docs/reference/sprints-archive.md`

7. `chore(release): Tag v1.7.0`
   - Ação: `git tag -a v1.7.0 -m "v1.7.0: TUI Dashboard com Textual"`

**Meta:** Release v1.7.0 publicado com tag, changelog e documentação atualizados.

---

### Plano de Execução Pós-v1.7.0

As branches abaixo são planejadas para sprints futuros e não bloqueiam o release.

#### Sprint v1.8.0 — Otimização

| #   | Branch                                      | Escopo                                    | DTs/RFs        |
| --- | ------------------------------------------- | ----------------------------------------- | -------------- |
| 1   | `refactor/c/split-timer-service`            | Extrai PauseResumeService (RF-010)        | RF-010         |
| 2   | `refactor/c/extract-delegate-quick-actions` | Panels emitem mensagens (RF-001)          | RF-001         |
| 3   | `refactor/c/loader-split-phase-dataclass`   | Split Phase + dataclasses (RF-003/RF-005) | RF-003, RF-005 |
| 4   | `refactor/c/consolidate-status-counting`    | Counter em \_refresh_content (RF-008)     | RF-008         |
| 5   | `feat/c/sidebar-compact`                    | Tabs horizontais (ADR-042)                | DT-060         |
| 6   | `feat/c/cli-logging`                        | Logging estruturado na CLI                | DT-058         |
| 7   | `feat/c/agenda-pagination`                  | Paginação -3/+3 dias (ADR-041)            | DT-063         |
| 8   | `test/c/commands-coverage`                  | CliRunner para commands/ (meta >80%)      | —              |

**Dependências:** RF-003/005 depende de RF-001. RF-008 depende de RF-005.

#### Sprint v2.0 — Arquitetura

| #   | Branch                           | Escopo                           | DTs/RFs |
| --- | -------------------------------- | -------------------------------- | ------- |
| 1   | `refactor/c/unified-di-pattern`  | Repository Pattern unificado     | DT-012  |
| 2   | `refactor/c/basedpyright-strict` | TypedDict, casts, strict mode    | DT-044  |
| 3   | `ci/c/pyright-ci-job`            | Pyright no pipeline CI (ADR-044) | DT-025  |

**Dependências:** DT-044 depende de RF-005. DT-025 depende de DT-044.

---

### Itens Sem Branch Planejada (Monitoramento)

| ID     | Descrição                   | Razão                                                 |
| ------ | --------------------------- | ----------------------------------------------------- |
| DT-007 | migration_001 sem cobertura | ACEITO — será removida na v2.0                        |
| DT-019 | command_bar.py stub         | Feature planejada Sprint 6+ — não é débito, é backlog |
| DT-064 | CVE-2026-4539 pygments      | Aguarda fix upstream — monitorar releases             |
| DT-069 | Tela de configurações       | Requer BR + ADR antes de implementação                |
| RF-006 | Polimorfismo por status     | Avaliado como over-engineering no estado atual        |

---

### Grafo de Dependências Completo

```
v1.7.0 (sequencial)
├── 1. test/c/sprint-5.5-hardening     → merge → develop
├── 2. fix/c/dashboard-validation      → merge → develop
└── 3. chore/c/v1.7.0-release-prep     → merge → develop → tag v1.7.0

v1.8.0 (paralelo, exceto onde indicado)
├── refactor/c/split-timer-service
├── refactor/c/extract-delegate-quick-actions
│   └── refactor/c/loader-split-phase-dataclass (depende de RF-001)
│       └── refactor/c/consolidate-status-counting (depende de RF-005)
├── feat/c/sidebar-compact
├── feat/c/cli-logging
├── feat/c/agenda-pagination
└── test/c/commands-coverage

v2.0 (sequencial)
├── refactor/c/unified-di-pattern (depende de RF-010 + RF-001)
├── refactor/c/basedpyright-strict (depende de RF-005)
│   └── ci/c/pyright-ci-job (depende de DT-044)
```

---

### Resumo Quantitativo

| Sprint    | Branches | Commits estimados | DTs resolvidos  | RFs resolvidos |
| --------- | -------- | ----------------- | --------------- | -------------- |
| v1.7.0    | 3        | ~21               | 4 (59,65,66,67) | 0              |
| v1.8.0    | 8        | ~16               | 3 (58,60,63)    | 4 (1,3,5,8)    |
| v2.0      | 3        | ~8                | 3 (12,25,44)    | 0              |
| **Total** | **14**   | **~45**           | **10**          | **4**          |

Com a execução completa, o projeto atingirá:

- 64/70 DTs resolvidos (91%)
- 8/10 RFs aplicados (80%)
- Cobertura de BRs >90%
- Cobertura `commands/` >80%

---

## Parte 3 — Snapshot Tests: Estado e Limitações

### Inventário

O projeto possui **17 testes de snapshot** (pytest-textual-snapshot 1.1.0 + syrupy 4.8.0) com **19 baselines SVG**:

| Categoria                               | Testes | Baselines |
| --------------------------------------- | ------ | --------- |
| Dashboard (empty, routine, 80x24)       | 3      | 3 SVGs    |
| CRUD modals (routines, habits, tasks)   | 8      | 8 SVGs    |
| Quick actions (done, skip modals)       | 2      | 2 SVGs    |
| Dashboard states (done, skipped, timer) | 3      | 3 SVGs    |
| Metrics (7-day mixed, streak perfeito)  | 2      | 3 SVGs    |
| **Total**                               | **17** | **19**    |

### Limitação de CI — Incompatibilidade de Versionamento

Snapshots estão **excluídos de todo CI** (GitLab, GitHub, pre-push hook):

```
Python 3.14 → pytest 8.4.2 (reportinfo() retorna str | PathLike)
    → pytest-textual-snapshot 1.1.0 (espera só str) → CRASH
```

- Monkey-patch em `tests/e2e/conftest.py` resolve localmente
- pytest-textual-snapshot não lançou fix upstream
- **Decisão: aceitar como limitação** — snapshots continuam local-only

### Gaps sem Baseline

1. **Agenda panel com blocos renderizados** — alta prioridade
2. **Help overlay** — baixa prioridade
3. **Telas secundárias** (Routines, Habits, Tasks, Timer screens)
4. **Layout responsivo 160 colunas**
5. **Timer live updates** — removido por flakiness

### Monitoramento

Acompanhar releases de `pytest-textual-snapshot` no PyPI. Quando versão >1.1.0 sair com fix:

1. Remover monkey-patch do conftest.py
2. Remover `--ignore` dos CIs
3. Adicionar job `test:snapshots` no pipeline
4. Definir política de aprovação (PR review para diff de baseline)

---

## Parte 4 — Checklist de Finalização v1.7.0

### Itens bloqueantes para release

- [ ] Merge das 3 branches → develop (test → validation → release-prep)
- [ ] Rodar suite completa (~1.320 testes, confirmar 0 falhas)
- [ ] Criar tag v1.7.0

### Itens não-bloqueantes (aceitos para v1.7.0)

| Item                                | Razão                                              |
| ----------------------------------- | -------------------------------------------------- |
| 14 DTs pendentes (MÉDIA/BAIXA)      | Nenhum CRÍTICO ou ALTO                             |
| 5 telas secundárias stub            | ADR-034: dashboard-first, telas são expanded views |
| Responsividade 80x24 (DT-065)       | Limitação documentada                              |
| Cobertura commands/ em 45%          | Meta v1.8.0                                        |
| Snapshots excluídos do CI           | Bloqueio upstream (pytest-textual-snapshot)        |
| 7 TODOs no código TUI               | Todos features futuras (Sprint 5+)                 |
| README sem links diagramas (DT-067) | Pode ser v1.7.1                                    |

### Gates de release

| Gate                            | Status                     |
| ------------------------------- | -------------------------- |
| Mypy 0 erros (strict)           | [OK]                       |
| Ruff 0 warnings                 | [OK]                       |
| Basedpyright 0 erros (standard) | [OK]                       |
| Cobertura ≥80%                  | [OK] ~82%                  |
| 0 testes skipped/xfail          | [OK]                       |
| CHANGELOG v1.7.0                | [OK] (branch release-prep) |
| Version bump 1.7.0              | [OK] (branch release-prep) |

---

## Referências

- FOWLER, M. _Refactoring: Improving the Design of Existing Code_. 2nd ed. Boston: Addison-Wesley, 2018.
- HUMBLE, J.; FARLEY, D. _Continuous Delivery_. Boston: Addison-Wesley, 2010.
- technical-debt.md v2.25.0 (dados corrigidos para v2.25.0 real: 62 DTs) — SSOT do débito técnico
- quality-metrics.md v3.0.0 — Métricas de qualidade
- refactoring-catalog.md v1.0.0 — Catálogo de refatorações
- sprints.md v6.0.0 — Sprints ativas
- roadmap.md v7.0.0 — Visão de produto

---

**Última atualização:** 30 de Março de 2026
