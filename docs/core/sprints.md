# Sprints

**Versão:** 5.0.0

**Status:** Single Source of Truth (SSOT)

---

## Visão Geral

Este documento acompanha as sprints ativas do projeto ATOMVS TimeBlock Terminal. Cada sprint representa um ciclo de entregas incrementais onde requisitos formalizados são decompostos em tarefas atômicas, validados e implementados com rastreabilidade completa. A metodologia de engenharia de requisitos, análise comportamental e implementação orientada por testes está documentada em `docs/core/development.md`.

O histórico de sprints concluídas (v1.0.0 a v1.6.0) está arquivado em `docs/core/sprints-archive.md`.

---

## v1.7.0 — TUI com Textual (Em Andamento)

A v1.7.0 marca a transição do ATOMVS TimeBlock de ferramenta CLI pura para uma aplicação interativa completa com interface TUI baseada em Textual. A CLI permanece como interface de automação e scripts, enquanto a TUI oferece navegação visual para uso diário interativo. O escopo inclui reestruturação do repositório (flatten de `cli/`, branding ATOMVS), implementação de 5 screens navegáveis (Dashboard, Routines, Habits, Tasks, Timer) com design Material-like e 15 business rules do domínio TUI (BR-TUI-001 a BR-TUI-015).

**Métricas de acompanhamento:**

| Métrica               | Início (v1.6.0) | Atual (15/03)           | Meta v1.7.0 |
| --------------------- | --------------- | ----------------------- | ----------- |
| Cobertura global      | 87%             | ~82%                    | >= 80%      |
| Cobertura tui/        | 0%              | ~65% (parcial)          | >= 80%      |
| Testes totais         | 778             | 1241                    | 1200+       |
| Erros mypy            | 0               | 0                       | 0           |
| BRs TUI especificadas | 0               | 26                      | 26/26       |
| BRs TUI implementadas | 0               | 8 (001-004,016-018,021) | 26/26       |
| Screens funcionais    | 0/5             | 1/5 (Dashboard)         | 5/5         |

---

### Sprint 0 — Reestruturação e Branding [DONE]

O Sprint 0 preparou a infraestrutura do repositório para receber a TUI. Incluiu a adoção do branding ATOMVS (ADR-032), o rename de `docs/ssot/` para `docs/core/`, a documentação arquitetural da TUI (ADR-031), as Business Rules do domínio TUI, o flatten do diretório `cli/` para a raiz, e a atualização de toda a cadeia CI/CD e documentação.

**Branch:** `docs/branding` → mergeado em `develop`

- [x] ADR-032: Branding ATOMVS + namespace `atomvs-timeblock-*`
- [x] Atualizar `docs/core/architecture.md` — nomenclatura repos seção 13.1
- [x] Atualizar `docs/core/roadmap.md` — sumário executivo com branding
- [x] Renomear `docs/ssot/` → `docs/core/`
- [x] Atualizar referências internas `docs/ssot/` → `docs/core/` em todos os .md
- [x] ADR-031: Implementação TUI com Textual
- [x] Seção BR-TUI (BR-TUI-001 a BR-TUI-015) em `docs/core/business-rules.md`
- [x] Criar `docs/core/sprints.md` (este documento)
- [x] Criar `docs/core/sprints-archive.md` (histórico v1.0.0 a v1.6.0)
- [ ] Adicionar parágrafos introdutórios nas seções do `docs/core/business-rules.md`
- [ ] Adicionar parágrafos introdutórios nas seções do `docs/core/architecture.md`
- [x] Criar `docs/core/development.md` — SSOT do processo de desenvolvimento
- [ ] Atualizar README.md seção "Desenvolvimento" — resumo breve + link para development.md
- [ ] Atualizar `docs/decisions/README.md` — adicionar ADR-031 e ADR-032 ao índice
- [x] Flatten: mover `cli/src/` → `src/`
- [x] Flatten: mover `cli/tests/` → `tests/`
- [x] Flatten: mover `cli/data/` → `data/`
- [x] Flatten: mover `cli/pyproject.toml` → `pyproject.toml`
- [x] Flatten: mover `cli/pytest.ini` → `pytest.ini`
- [x] Flatten: mover `cli/.ruff.toml` → `.ruff.toml`
- [x] Remover diretório `cli/` vazio
- [x] Atualizar `.gitlab-ci.yml` — remover `cd cli/` de todos os jobs
- [x] Atualizar `.github/workflows/ci.yml` — remover `cd cli/`
- [x] Atualizar `scripts/test-cicd.sh` — paths sem `cli/`
- [x] Atualizar `Dockerfile` e `Dockerfile.test` — paths sem `cli/`
- [x] Atualizar `README.md` — paths, nome do repo, instruções
- [x] Atualizar `CHANGELOG.md` — entrada v1.7.0-dev
- [x] Atualizar `mkdocs.yml` — paths sem `cli/`
- [x] Validar: `python -m pytest tests/ -v` passa a partir da raiz
- [x] Validar: `ruff check .` sem erros a partir da raiz
- [x] Validar: `mypy src/timeblock` sem erros a partir da raiz
- [x] Validar: pipeline CI/CD verde no GitLab e GitHub

---

### Sprint 1 — Foundation [DONE]

O Sprint 1 construiu a fundação arquitetural da TUI: o session helper que toda operação TUI utiliza, o tema visual Material-like com o widget Card reutilizável, e o entry point que detecta automaticamente se deve abrir TUI ou CLI. Entregue em feat/tui-phase1.

**Branch:** `feat/tui-phase1` (mergeado)

**BR-TUI-009: Compartilhamento da Service Layer**

- [x] Criar `src/timeblock/tui/__init__.py`
- [x] Criar `src/timeblock/tui/session.py` com context manager `get_session()`
- [x] Criar `tests/unit/test_tui/__init__.py`
- [x] Criar `tests/unit/test_tui/test_session.py`
- [x] Teste: `test_br_tui_009_session_provides_working_session`
- [x] Teste: `test_br_tui_009_session_commits_on_success`
- [x] Teste: `test_br_tui_009_session_rollbacks_on_error`
- [x] Validar: 3 testes verdes, `get_session()` funcional com services existentes

**BR-TUI-008: Consistência Visual (Material-like)**

- [x] Criar `src/timeblock/tui/styles/` com `__init__.py`
- [x] Criar `src/timeblock/tui/styles/theme.tcss` com paleta completa
- [x] Criar `src/timeblock/tui/widgets/__init__.py`
- [x] Criar `src/timeblock/tui/widgets/card.py` — widget Card reutilizável
- [x] Criar `tests/unit/test_tui/test_widgets/__init__.py`
- [x] Criar `tests/unit/test_tui/test_widgets/test_card.py`
- [x] Teste: `test_br_tui_008_theme_file_exists`
- [x] Teste: `test_br_tui_008_card_renders_title`
- [x] Teste: `test_br_tui_008_card_renders_content`
- [x] Validar: Card renderiza com estilo definido, tema carrega sem erros

**BR-TUI-001: Entry Point Detection**

- [x] Criar `src/timeblock/tui/app.py` — TimeBlockApp mínimo
- [x] Modificar `src/timeblock/main.py` — detecção `sys.argv`
- [x] Atualizar `pyproject.toml` — dependência opcional `[tui]`
- [x] Criar `tests/unit/test_tui/test_entry_point.py`
- [x] Teste: `test_br_tui_001_no_args_launches_tui`
- [x] Teste: `test_br_tui_001_with_args_launches_cli`
- [x] Teste: `test_br_tui_001_fallback_without_textual`
- [x] Validar: `atomvs` abre TUI, `atomvs --help` abre CLI

---

### Sprint 2 — Navegação [DONE]

O Sprint 2 implementou a estrutura de navegação completa da TUI: sidebar com indicador de screen ativa, keybindings globais (Ctrl+Q quit, ? help, Escape voltar) e status bar persistente no rodapé. Entregue em feat/tui-phase1 com 5 screens navegáveis e feedback visual completo.

**Branch:** `feat/tui-phase1` (mergeado)

**BR-TUI-002: Screen Navigation**

- [x] Criar `src/timeblock/tui/widgets/sidebar.py`
- [x] Criar `src/timeblock/tui/screens/__init__.py`
- [x] Criar 5 screens placeholder (dashboard.py, routines.py, habits.py, tasks.py, timer.py)
- [x] Atualizar `app.py` — compose sidebar + content area, bindings de navegação
- [x] Criar `tests/unit/test_tui/test_navigation.py`
- [x] Teste: `test_br_tui_002_initial_screen_is_dashboard`
- [x] Teste: `test_br_tui_002_numeric_keybinding_navigation`
- [x] Teste: `test_br_tui_002_mnemonic_keybinding_navigation`
- [x] Teste: `test_br_tui_002_sidebar_shows_active_screen`
- [x] Validar: navegação entre 5 screens via teclado funcional

**BR-TUI-004: Global Keybindings**

- [x] Implementar `Ctrl+Q` → quit (com modal de confirmação)
- [x] Implementar `?` → help overlay
- [x] Implementar `Escape` → fechar modal ou voltar ao Dashboard
- [x] Criar `tests/unit/test_tui/test_keybindings.py`
- [x] Teste: `test_br_tui_004_quit_requires_ctrl_q`
- [x] Teste: `test_br_tui_004_help_overlay`
- [x] Teste: `test_br_tui_004_escape_returns_to_dashboard`
- [x] Validar: `Ctrl+Q` fecha, `?` exibe help, `Escape` retorna ao Dashboard

**BR-TUI-007: Footer (implementação inicial)**

- [x] Criar `src/timeblock/tui/widgets/status_bar.py`
- [x] Integrar na composição do app (rodapé fixo)
- [x] Exibir hora atual (atualiza a cada minuto)
- [x] Criar `tests/unit/test_tui/test_widgets/test_status_bar.py`
- [x] Teste: `test_br_tui_007_shows_current_time`
- [x] Validar: status bar exibe hora

**Nota:** BR-TUI-007 revisada em 02/03/2026. Footer contextual implementado em Sprint 3.2c com on_descendant_focus. BR-DATA-001 adicionada em Sprint 3.2g.

---

### Sprint 3.1 — Dashboard Visual [DONE]

O Sprint 3.1 implementou o Dashboard visual com mock data, layout duas colunas (agenda + cards), sistema de cores semânticas Catppuccin Mocha, header bar com contexto resumido, e 28 testes específicos. Entregue em feat/tui-phase1 com 7 commits.

**Branch:** `feat/tui-phase1` (mergeado)

**Entregue:**

- [x] DashboardScreen com layout duas colunas (agenda + cards)
- [x] Agenda do Dia com régua de 30min e blocos proporcionais
- [x] Card Hábitos com 5 colunas (indicador, nome, horário, duração, barra)
- [x] Card Tarefas com indicador por prioridade + nome + data
- [x] Card Timer com display ativo/idle e keybindings visuais
- [x] Card Métricas com streak, completude 7d/30d, heatmap semanal
- [x] HeaderBar com border_title, rotina, progresso, timer
- [x] Helpers: \_format_duration, \_find_block_at, \_block_style, \_spaced_title
- [x] 28 testes específicos do dashboard (formatação, cores, mock data)
- [x] Placeholders para estado vazio com orientação ao usuário

---

### Sprint 3.2 — Dashboard Interativo + Dados Reais [DONE]

O Sprint 3.2 transformou o dashboard de showcase visual para ferramenta funcional. Conectou cards a dados reais via services, implementou navegação entre panels com Tab/Shift+Tab, footer contextual com keybindings dinâmicos, quick actions (Ctrl+Enter done, Ctrl+S skip, Ctrl+K complete), backup automático no shutdown (BR-DATA-001), e TCSS modularizado em 7 arquivos. Entregue em `feat/tui-dashboard-interactive`.

BR-TUI-013 (Placeholders editáveis) movida para Sprint 4 — depende de CRUD.

**Branch:** `feat/tui-dashboard-interactive`

**Critério de conclusão:** Dashboard funcional com dados reais, navegação entre panels, quick actions operacionais, footer contextual.

**3.2a — Dados reais (BR-TUI-009)**

- [x] Substituir mock data por chamadas reais via session-per-action
- [x] RoutineService, HabitInstanceService, TaskService, TimerService integrados
- [x] Refresh on focus (dados atualizados ao entrar na screen)

**3.2b — Navegação entre panels (BR-TUI-012)**

- [x] Tab avança, Shift+Tab volta (nativo Textual)
- [x] FocusablePanel com cursor interno (setas/j/k)
- [x] Item selecionado com fundo Surface0 (#313244)
- [x] Focus indicator: borda Text (#CDD6F4) no panel ativo
- [x] `border_subtitle` nativo do Textual
- [x] Esc deseleciona todos os panels
- [x] Inicia sem panel selecionado

**3.2c — Footer contextual (BR-TUI-007 revisada)**

- [x] Footer com 3 seções: rotina (esq), keybindings (centro), timer+hora (dir)
- [x] Keybindings mudam conforme panel focado via `on_descendant_focus`
- [x] Layout: left auto, center 1fr, right auto

**3.2d — Quick actions (BR-TUI-004 revisada)**

- [x] Ctrl+Enter marca hábito como done
- [x] Ctrl+S marca hábito como skip
- [x] Ctrl+K completa task
- [x] Refresh automático após quick action

**3.2e — Placeholders editáveis (BR-TUI-013)**

- [ ] Movido para Sprint 4 (depende de CRUD)

**3.2f — TCSS Modularização (BR-TUI-014)**

- [x] theme.tcss (479 linhas) decomposto em 7 módulos
- [x] CSS_PATH como lista tipada (ClassVar) em app.py
- [x] Testes visual_consistency e status_bar adaptados

**3.2g — Backup automático (BR-DATA-001)**

- [x] BackupService com rotação (MAX_BACKUPS = 10)
- [x] Formato: timeblock-YYYYMMDD-HHMMSS-{label}.db
- [x] Backup no shutdown da TUI

**Otimização CI/CD**

- [x] Timeout integration: 30m → 60m
- [x] pytest-xdist adicionado (pyproject.toml + CI)
- [x] Integration job usa `-n auto --dist=loadfile`

---

### Sprint 4 — Dashboard-first CRUD

O Sprint 4 implementa CRUD diretamente no dashboard via modais contextuais. O usuário cria, edita e deleta rotinas, hábitos e tarefas sem sair do dashboard — o panel focado determina o contexto da operação. Decisão formalizada em ADR-034. Screens dedicadas permanecem como visão expandida para sprints futuras.

O primeiro commit é infraestrutural: otimização das fixtures de integração com scope="session" e rollback transacional (ADR-033, BR-TEST-001), necessária para suportar o crescimento da suíte de testes sem estourar o limite de 10 minutos no pipeline.

**Branch:** `feat/tui-crud-dashboard`

**Critério de conclusão:** CRUD completo de rotinas, hábitos e tarefas funcional via dashboard com modais, dados persistidos, panels atualizados após cada operação.

**4.0 — Fixture Optimization (BR-TEST-001) [PRÉ-REQUISITO]**

- [x] Criar ADR-033 em `docs/decisions/`
- [x] Implementar `integration_engine` com `scope="session"`
- [x] Implementar `integration_session` com rollback transacional
- [x] Converter testes existentes: `commit()` → `flush()`
- [x] Validar: todos os testes de integração passam com novo conftest
- [x] CI: adicionar check de ausência de `session.commit()` em testes de integração
- [x] Teste: `test_br_test_001_rollback_isolates_tests`
- [x] Teste: `test_br_test_001_flush_materializes_data`

**4a — ConfirmDialog + FormModal (BR-TUI-019, BR-TUI-020)**

- [x] Criar `src/timeblock/tui/widgets/confirm_dialog.py`
- [x] Criar `src/timeblock/tui/widgets/form_modal.py`
- [x] ConfirmDialog: Enter confirma, Esc cancela, modal trap, foco retorna
- [x] FormModal: campos tipados (text, time, number, select), Tab navega, validação inline
- [x] Visual Catppuccin: ConfirmDialog borda Red, FormModal borda Blue, fundo Mantle
- [x] Criar `tests/unit/test_tui/test_confirm_dialog.py`
- [x] Criar `tests/unit/test_tui/test_form_modal.py`
- [x] Teste: `test_br_tui_019_enter_triggers_confirm`
- [x] Teste: `test_br_tui_019_esc_triggers_cancel`
- [x] Teste: `test_br_tui_019_modal_traps_focus`
- [x] Teste: `test_br_tui_020_tab_navigates_fields`
- [x] Teste: `test_br_tui_020_enter_submits_form`
- [x] Teste: `test_br_tui_020_required_field_validation`
- [x] Teste: `test_br_tui_020_edit_mode_prefilled`
- [x] Validar: modais funcionais em isolamento com foco correto

**4b — CRUD Rotinas via Dashboard (BR-TUI-016)**

- [x] DashboardScreen intercepta `n`/`e`/`x` quando header focado
- [x] `n` abre FormModal (campo: nome) → RoutineService.create
- [x] Rotina criada torna-se ativa automaticamente
- [x] `e` abre FormModal preenchido → RoutineService.update
- [x] `x` abre ConfirmDialog → RoutineService.delete
- [x] Sem rotina → header exibe hint `[Sem rotina] n criar`
- [x] `refresh_data()` após cada operação CRUD
- [x] Criar `tests/unit/test_tui/test_dashboard_crud_routines.py`
- [x] Teste: `test_br_tui_016_n_on_header_opens_routine_form`
- [x] Teste: `test_br_tui_016_created_routine_becomes_active`
- [x] Teste: `test_br_tui_016_x_on_header_opens_confirm_dialog`
- [x] Teste: `test_br_tui_016_no_routine_shows_hint`
- [x] Validar: CRUD de rotinas funcional via dashboard

**4c — CRUD Hábitos via Dashboard (BR-TUI-017)**

- [x] DashboardScreen intercepta `n`/`e`/`x` quando panel hábitos focado
- [x] `n` abre FormModal (campos: título, horário, duração, recorrência) → HabitService.create
- [x] Requer rotina ativa (mensagem de erro se nenhuma)
- [x] `e` abre FormModal preenchido → HabitService.update
- [x] `x` abre ConfirmDialog → HabitService.delete
- [x] Hábito criado aparece imediatamente no panel
- [x] Quick actions coexistem (Ctrl+Enter done, Ctrl+S skip)
- [x] Criar `tests/unit/test_tui/test_dashboard_crud_habits.py`
- [x] Teste: `test_br_tui_017_n_on_habits_opens_form`
- [x] Teste: `test_br_tui_017_n_without_routine_shows_error`
- [x] Teste: `test_br_tui_017_created_habit_appears_in_panel`
- [x] Teste: `test_br_tui_017_validation_title_required`
- [x] Teste: `test_br_tui_017_coexists_with_quick_actions`
- [x] Validar: CRUD de hábitos funcional via dashboard

**4d — CRUD Tarefas via Dashboard (BR-TUI-018)**

- [x] DashboardScreen intercepta `n`/`e`/`x` quando panel tarefas focado
- [x] `n` abre FormModal (campos: título, data, horário, prioridade) → TaskService.create
- [x] `e` abre FormModal preenchido → TaskService.update
- [x] `x` abre ConfirmDialog → TaskService.delete
- [x] Task criada aparece na posição correta (ordenação por proximidade)
- [x] Ctrl+Enter complete coexiste (ADR-035)
- [x] Criar `tests/unit/test_tui/test_dashboard_crud_tasks.py`
- [x] Teste: `test_br_tui_018_n_on_tasks_opens_form`
- [x] Teste: `test_br_tui_018_created_task_appears_in_panel`
- [x] Teste: `test_br_tui_018_task_ordered_by_proximity`
- [x] Teste: `test_br_tui_018_validation_title_required`
- [x] Teste: `test_br_tui_018_coexists_with_ctrl_enter`
- [x] Validar: CRUD de tarefas funcional via dashboard

**4e — Placeholders editáveis (BR-TUI-013)**

- [x] Enter em placeholder `---` abre FormModal contextual (tipo determinado pelo panel)
- [x] Placeholder transformado em item real ao confirmar
- [x] Teste: `test_br_tui_013_enter_on_placeholder_opens_form`
- [x] Teste: `test_br_tui_013_placeholder_becomes_real_item`
- [x] Validar: placeholders funcionais em todos os panels

**Refatorações fundamentadas em literatura (durante Sprint 4)**

As refatorações abaixo são derivadas de Fowler (2002) e Humble & Farley (2010), categorizadas por momento de aplicação. Cada item inclui referência bibliográfica específica e estado atual no projeto.

_Pré-requisito (4.0):_

- [x] R7. Isolamento de testes via rollback transacional (HUMBLE; FARLEY, 2010, p. 375) → BR-TEST-001, ADR-033

_Durante Sprint 4 (aplicar em cada arquivo tocado):_

- [x] R1. Dependency Injection nos widgets TUI (HUMBLE; FARLEY, 2010, p. 179) — widgets recebem dados prontos (listas de dicts), DashboardScreen orquestra, widgets renderizam. Formalizar para CRUD
- [x] R2. Mock services nos testes unitários TUI (HUMBLE; FARLEY, 2010, p. 180-183) — testes unitários de CRUD TUI devem mockar services. Testes de integração (TUI → service → DB) em tests/integration/
- [x] R3. Minimizar estado nos testes (HUMBLE; FARLEY, 2010, p. 183-184) — categorizar dados: test-specific (inline), test reference (fixtures), application reference (conftest). Reutilizar fixtures de referência
- [x] R5. Service Layer como boundary (FOWLER, 2002, p. 133) — TUI nunca acessa models diretamente (BR-TUI-009). DashboardScreen é a boundary para CRUD

_Monitoramento (durante Sprint 4):_

- [x] R8. Commit stage abaixo de 10 minutos (HUMBLE; FARLEY, 2010, p. 185) — monitorar tempo de pipeline. Se ultrapassar 10min, aplicar GitLab parallel: 2

_Sprint 5+ / v2.0 (futuro):_

- [x] R4. Abstração de tempo (HUMBLE; FARLEY, 2010, p. 184) — TimerPanel e StatusBar usam datetime.now() diretamente. Para timer live (Sprint 5), extrair wrapper injetável
- [x] R6. Repository como abstração de queries (FOWLER, 2002, p. 322) — centralizar queries duplicadas entre services. Avaliar Repository formal na v2.0 com Django ORM

**Refatoração incremental (código)**

- [x] Extrair constantes em constants.py (D-005 pendente)
- [x] Remover `spaced_title` não utilizado nos panels
- [x] Corrigir `@staticmethod` duplicado em dashboard.py (linhas 155-156)
- [x] Documentar itens em technical-debt.md
- [x] Manter funções <= 50 linhas, classes <= 300 linhas (BR-TUI-015)

---

### Sprint 4.5 — First Complete Loop [WIP]

O Sprint 4.5 implementa o menor conjunto de mudanças que conecta o fluxo completo de uso do ATOMVS no dashboard: criar rotina, criar hábito, ver na agenda, iniciar timer, pausar/retomar, parar timer (marca done), e ver resultado na agenda atualizada. Nenhuma feature é adicionada pela metade — o objetivo é que o usuário consiga completar um ciclo inteiro sem sair do dashboard.

A nomenclatura "4.5" reflete que este sprint é uma extensão direta da Sprint 4 (mesma branch `feat/tui-dashboard-timer`), não um sprint independente. O critério de conclusão é funcional: o happy path completo funciona de ponta a ponta, mesmo que com limitações visuais ou de polish.

**Branch:** `feat/tui-dashboard-timer` (continuação)

**Critério de conclusão:** Usuário executa o ciclo completo rotina → hábito → timer → done sem sair do dashboard.

**Happy path alvo:**

```plaintext
1. Criar rotina (n no agenda/header)
2. Criar hábito (n no panel hábitos)
3. Ver hábito na agenda + panel
4. Selecionar hábito, Shift+Enter → inicia timer
5. Ver elapsed atualizando em tempo real (1s)
6. Shift+Enter → pausa, Shift+Enter → retoma
7. Ctrl+Enter → stop timer, marca hábito como done
8. Agenda atualiza: bloco muda de running → done
```

**Commit 1: fix(loader): Corrige load_active_timer — elapsed MM:SS, nome do hábito (DT-016)**

- [x] Converter `elapsed_seconds` para string `MM:SS` no loader
- [x] Buscar nome do hábito via `HabitInstance` → `Habit.title`
- [x] Retornar dict compatível com TimerPanel (`elapsed`, `name`, `status`)
- [x] Teste: `test_load_active_timer_returns_formatted_elapsed`
- [x] Teste: `test_load_active_timer_returns_habit_name`

**Commit 2: feat(tui): Timer keybindings no dashboard (BR-TUI-021)**

- [x] TimerPanel ganha `on_key` com Shift+Enter (start/pause), Ctrl+Enter (stop), Ctrl+X (cancel)
- [x] Mensagens: `TimerStartRequest`, `TimerPauseRequest`, `TimerStopRequest`, `TimerCancelRequest`
- [x] DashboardScreen handlers despacham para TimerService
- [x] Shift+Enter em hábito running no HabitsPanel → delega start ao TimerPanel via coordinator
- [x] Ctrl+X abre ConfirmDialog antes de cancelar
- [x] Teste: `test_br_tui_021_shift_enter_starts_timer`
- [x] Teste: `test_br_tui_021_shift_enter_toggles_pause`
- [x] Teste: `test_br_tui_021_ctrl_enter_stops_timer`
- [x] Teste: `test_br_tui_021_ctrl_x_cancel_requires_confirm`

**Commit 3: feat(tui): Timer live update via set_interval (DT-015)**

- [x] DashboardScreen.on_mount adiciona `set_interval(1, self._tick_timer)`
- [x] `_tick_timer` recarrega timer do service e atualiza TimerPanel
- [x] StatusBar atualiza elapsed globalmente
- [ ] Teste: `test_timer_panel_updates_every_second` (mock time)

**Commit 4: feat(tui): Agenda auto-refresh a cada 60s (DT-015)**

- [x] DashboardScreen.on_mount adiciona `set_interval(60, self._refresh_agenda)`
- [x] `_refresh_agenda` recarrega instâncias e atualiza AgendaPanel + HabitsPanel
- [x] Marcador de hora atual se move com o relógio
- [ ] Teste: `test_agenda_refreshes_periodically`

**Commit 5: feat(tui): Ctrl+Enter em hábito running → stop + done**

- [x] HabitsPanel: Ctrl+Enter em item com status "running" emite `TimerStopAndDoneRequest`
- [x] DashboardScreen handler: para timer + marca instância como done
- [x] Agenda atualiza bloco de running → done
- [x] Teste: `test_ctrl_enter_on_running_habit_stops_and_marks_done`

**Commit 6: docs(sprints): Documenta First Complete Loop, atualiza tech-debt**

- [x] Atualizar sprints.md com progresso
- [x] Atualizar technical-debt.md (DT-015, DT-016 resolvidos)
- [ ] Atualizar roadmap.md com estado pós-Sprint 4.5

---

### Sprint 5.5 — Dashboard Integralmente Funcional [PLANNED]

O Sprint 5.5 resolve todos os gaps de aderência entre implementação e BRs revelados pela revisão de testes e2e (15/03/2026). O objetivo é que cada interação do dashboard funcione conforme as regras de negócio documentadas, com modais de interação consistentes e substatus corretamente gerenciados.

**Branch:** `fix/dashboard-quality` (continuação) + `docs/br-update`

**Critério de conclusão:** Todos os DTs CRÍTICA e ALTA resolvidos (DT-034 a DT-042), 1241+ testes passando, 0 violações de `validate_status_consistency()`.

**Decisão arquitetural:** ADR-038 (Dashboard Interaction Patterns)

**Fase 1: Fixes CRÍTICA (DT-034, DT-035)**

Branch: `fix/dashboard-quality`

- [ ] DT-034: `mark_completed` recebe `done_substatus` como parâmetro obrigatório
- [ ] DT-035: Handler undo limpa todos os campos (`skip_reason`, `skip_note`, `completion_percentage`)
- [ ] Teste: `test_br_habitinstance_007_undo_clears_all_substatus`
- [ ] Teste: `test_br_habitinstance_002_done_requires_substatus_via_tui`

**Fase 2: Modais de interação (DT-036, DT-037, DT-039)**

Branch: `feat/dashboard-modals`

- [ ] DT-037: `v` sem timer abre modal de DoneSubstatus (BR-TUI-022)
- [ ] DT-037: `v` com TimeLog existente abre modal de restauração (BR-HABITINSTANCE-007)
- [ ] DT-036: `v` com timer running abre modal de opções (BR-TUI-023)
- [ ] DT-039: `s` abre modal de SkipReason + nota (BR-TUI-024)
- [ ] Teste: `test_br_tui_022_v_without_timer_opens_modal`
- [ ] Teste: `test_br_tui_023_v_on_running_opens_modal`
- [ ] Teste: `test_br_tui_024_s_opens_skip_reason_modal`

**Fase 3: Postpone e Routine-first (DT-038, DT-040)**

Branch: `feat/dashboard-modals` (continuação)

- [ ] DT-038: `s` no tasks panel abre FormModal de edit (BR-TUI-018 + ADR-038 D5)
- [ ] DT-040: `n` sem rotina redireciona para criação com mensagem (BR-TUI-025)
- [ ] Teste: `test_br_tui_025_n_habits_no_routine_opens_routine_modal`
- [ ] Teste: `test_tasks_postpone_opens_edit_modal`

**Fase 4: Documentação (DT-041, DT-042)**

Branch: `docs/br-update`

- [ ] DT-041: Reescrever keybindings em BR-TUI-004, BR-TUI-017, BR-TUI-018, BR-TUI-021
- [ ] DT-042: Atualizar BR-HABITINSTANCE-001 com transição undo
- [ ] Adicionar BR-HABITINSTANCE-007, BR-TASK-011, BR-TUI-022 a BR-TUI-026
- [ ] ADR-038 commitado e referenciado

**Fase 5: Testes e2e fortalecidos**

Branch: `test/dashboard-complete`

- [ ] Fortalecer asserções: verificar substatus, skip_reason, completion_percentage
- [ ] Adicionar testes: Esc cancela FormModal, Esc cancela ConfirmDialog
- [ ] Adicionar testes: setas (up/down) equivalentes a j/i
- [ ] Adicionar teste: BR-TIMER-001 bloqueia segundo timer
- [ ] Remover workarounds dos testes existentes
- [ ] Validar: 1241+ testes passando, 0 xfail (exceto DT-026)

---

### Sprint 5 — Timer

O Sprint 5 implementa a screen mais interativa da TUI: o Timer com display live atualizado a cada segundo. Esta screen exige integração com `set_interval` do Textual para atualização contínua e com o TimerService existente para persistência de sessões. O timer ativo também passa a ser visível no footer de qualquer screen, completando a integração com BR-TUI-007.

**Branch:** `feat/tui-timer`

**Critério de conclusão:** Timer funcional com display live, pause/resume, sessão salva ao stop, timer visível no footer global.

**BR-TUI-006: Timer Screen Live Display**

- [ ] Implementar TimerScreen com display atualizado a cada segundo
- [ ] Keybindings: `Shift+Enter`=start/pause, `Ctrl+Enter`=stop, `Ctrl+X`=cancel [MODAL] (ADR-035)
- [ ] Integrar com TimerService existente
- [ ] Atualizar footer para exibir timer ativo globalmente
- [ ] Implementar confirmação ao sair com timer ativo (Ctrl+Q modal informa perda de sessão)
- [ ] Criar `tests/unit/test_tui/test_screens/test_timer.py`
- [ ] Teste: `test_br_tui_006_timer_display_updates`
- [ ] Teste: `test_br_tui_006_shift_enter_starts_timer`
- [ ] Teste: `test_br_tui_006_shift_enter_toggles_pause`
- [ ] Teste: `test_br_tui_006_ctrl_enter_stops_saves_session`
- [ ] Teste: `test_br_tui_006_ctrl_x_cancel_requires_confirmation`
- [ ] Teste: `test_br_tui_006_active_timer_in_footer`
- [ ] Validar: timer live funcional, sessão persistida, footer integrado

---

### Sprint 6 — Polimento e Release

O Sprint 6 fecha a v1.7.0 com revisão de cobertura, audit de qualidade de código (BR-TUI-015) e preparação do release. Nenhuma funcionalidade nova é adicionada — o foco é qualidade, documentação e empacotamento.

**Branch:** `release/v1.7.0`

**Critério de conclusão:** Tag v1.7.0 criada, pipeline verde, changelog completo, cobertura >= 80% em tui/.

**Cobertura e Revisão**

- [ ] Verificar cobertura do pacote `tui/` — meta 80%
- [ ] Adicionar testes faltantes para edge cases
- [ ] Executar `mypy src/timeblock --check-untyped-defs` — zero erros
- [ ] Executar `ruff check .` — zero warnings
- [ ] Testar regressão CLI — todos os testes existentes passam
- [ ] Audit de qualidade (BR-TUI-015): SOLID, Clean Code, complexidade ciclomática
- [ ] Validar: 80%+ cobertura em tui/, zero mypy, zero ruff, zero regressão

**Release v1.7.0**

- [ ] Atualizar `CHANGELOG.md` com todas as entregas
- [ ] Atualizar `pyproject.toml` — versão 1.7.0
- [ ] Atualizar `docs/core/roadmap.md` — marcar v1.7.0 como entregue
- [ ] Mover seção v1.7.0 concluída para `docs/core/sprints-archive.md`
- [ ] Criar tag `v1.7.0`
- [ ] Push GitLab + GitHub
- [ ] Validar: tag criada, pipeline verde, changelog completo

---

## Changelog do Documento

| Data       | Versão | Mudanças                                                    |
| ---------- | ------ | ----------------------------------------------------------- |
| 2026-02-05 | 1.0.0  | Criação inicial — planejamento v1.7.0 com 7 sprints         |
| 2026-03-02 | 2.0.0  | Sprint 0/1/2 marcados DONE, Sprint 3.1 DONE, 3.2 detalhado, |
|            |        | keybindings atualizados para Ctrl+, métricas atualizadas,   |
|            |        | BRs 012-015 adicionadas, footer contextual documentado      |
| 2026-03-10 | 4.0.0  | Sprint 4 marcada DONE (MR !27), Sprint 4.5 First            |
|            |        | Complete Loop planejado, keybindings ADR-035, DT-015        |
|            |        | a DT-020 documentados                                       |
| 2026-03-05 | 3.0.0  | Sprint 3.2 marcada DONE, Sprint 4 reescrita para            |
|            |        | dashboard-first CRUD (ADR-034), Sprint 4 CRUD Screens       |
|            |        | removida, BRs 016-020 + BR-TEST-001, métricas 1079 testes   |
| 2026-03-15 | 5.0.0  | Sprint 5.5 planejada (Dashboard Funcional), métricas        |
|            |        | 1241 testes, ADR-038, DT-034 a DT-042, BRs 022-026          |

---

**Próxima revisão:** Após Sprint 5.5 concluída

**Última atualização:** 15 de Março de 2026
