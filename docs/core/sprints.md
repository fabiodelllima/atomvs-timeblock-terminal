# Sprints

**Versão:** 2.0.0

**Status:** Single Source of Truth (SSOT)

---

## Visão Geral

Este documento acompanha as sprints ativas do projeto ATOMVS TimeBlock Terminal. Cada sprint representa um ciclo de entregas incrementais onde requisitos formalizados são decompostos em tarefas atômicas, validados e implementados com rastreabilidade completa. A metodologia de engenharia de requisitos, análise comportamental e implementação orientada por testes está documentada em `docs/core/development.md`.

O histórico de sprints concluídas (v1.0.0 a v1.6.0) está arquivado em `docs/core/sprints-archive.md`.

---

## v1.7.0 — TUI com Textual (Em Andamento)

A v1.7.0 marca a transição do ATOMVS TimeBlock de ferramenta CLI pura para uma aplicação interativa completa com interface TUI baseada em Textual. A CLI permanece como interface de automação e scripts, enquanto a TUI oferece navegação visual para uso diário interativo. O escopo inclui reestruturação do repositório (flatten de `cli/`, branding ATOMVS), implementação de 5 screens navegáveis (Dashboard, Routines, Habits, Tasks, Timer) com design Material-like e 15 business rules do domínio TUI (BR-TUI-001 a BR-TUI-015).

**Métricas de acompanhamento:**

| Métrica               | Início (v1.6.0) | Atual (02/03)   | Meta v1.7.0 |
| --------------------- | --------------- | --------------- | ----------- |
| Cobertura global      | 87%             | ~82%            | >= 80%      |
| Cobertura tui/        | 0%              | ~60% (parcial)  | >= 80%      |
| Testes totais         | 778             | ~1058           | 1000+       |
| Erros mypy            | 0               | 0               | 0           |
| BRs TUI especificadas | 0               | 15              | 15/15       |
| BRs TUI implementadas | 0               | 4 (001-004)     | 15/15       |
| Screens funcionais    | 0/5             | 1/5 (Dashboard) | 5/5         |

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

### Sprint 3.2 — Dashboard Interativo + Dados Reais

O Sprint 3.2 transforma o dashboard de showcase visual para ferramenta funcional. Conecta os cards a dados reais via services, implementa navegação entre panels com Tab, footer contextual com keybindings, quick actions com Ctrl+tecla, e placeholders editáveis. Ao final desta sprint, o usuário consegue gerenciar seu dia inteiro sem sair do dashboard.

**Branch:** `feat/tui-dashboard-interactive`

**Critério de conclusão:** Dashboard funcional com dados reais, navegação entre panels, quick actions operacionais, footer contextual.

**3.2a — Dados reais (BR-TUI-009)**

- [ ] Substituir mock data por chamadas reais via session-per-action
- [ ] RoutineService.get_active() → header + agenda
- [ ] HabitInstanceService.get_today_instances() → card hábitos
- [ ] TaskService.get_pending() → card tarefas
- [ ] TimerService.get_any_active_timer() → card timer
- [ ] Refresh on focus (dados atualizados ao entrar na screen)
- [ ] Testes de integração: dashboard com banco real

**3.2b — Navegação entre panels (BR-TUI-012)**

- [ ] Tab avança entre panels (Agenda → Hábitos → Tarefas → Timer → Agenda)
- [ ] Ctrl+Tab volta (ciclo reverso)
- [ ] Números 1-4 focam panel diretamente
- [ ] Setas / j/k navegam itens dentro do panel focado
- [ ] Item selecionado com fundo Surface0 #313244
- [ ] Scroll interno com j/k quando panel tem overflow
- [ ] Testes: test_br_tui_012_tab_cycles_panels
- [ ] Testes: test_br_tui_012_ctrl_tab_reverses
- [ ] Testes: test_br_tui_012_numbers_focus_panel
- [ ] Testes: test_br_tui_012_arrows_navigate_items

**3.2c — Footer contextual (BR-TUI-007 revisada)**

- [ ] Footer com 3 seções: rotina (esq), keybindings (centro), timer+hora (dir)
- [ ] Keybindings mudam conforme panel focado
- [ ] Timer elapsed atualiza a cada segundo quando ativo
- [ ] Hora HH:MM atualiza a cada minuto
- [ ] Testes: test_br_tui_007_footer_keybindings_change_on_focus

**3.2d — Quick actions (BR-TUI-004 revisada)**

- [ ] Ctrl+Enter → mark done (hábito, solicita duração)
- [ ] Ctrl+S → skip (hábito, solicita razão)
- [ ] Ctrl+K → complete task
- [ ] Ctrl+S → start timer / Ctrl+P → pause/resume
- [ ] Refresh automático após quick action
- [ ] Testes: test_br_tui_004_ctrl_enter_marks_done
- [ ] Testes: test_br_tui_004_ctrl_s_skips_habit
- [ ] Testes: test_br_tui_004_ctrl_k_completes_task

**3.2e — Placeholders editáveis (BR-TUI-013)**

- [ ] Enter em placeholder `---` abre edição inline
- [ ] Tipo do item determinado pelo panel (hábito, task)
- [ ] Placeholder transformado em item real ao confirmar
- [ ] N abre modal com campos completo (contextual ao panel)
- [ ] : abre barra de comando (power user)
- [ ] Testes: test_br_tui_013_enter_on_placeholder_edits
- [ ] Testes: test_br_tui_013_n_opens_contextual_modal
- [ ] Testes: test_br_tui_013_colon_opens_command_bar

**3.2f — Refatoração visual (BR-TUI-014)**

- [ ] Quebrar theme.tcss (479 linhas) em múltiplos arquivos por screen/widget
- [ ] Extrair constantes restantes em constants.py (D-005 pendente)
- [ ] Validar: zero regressão visual após split

---

### Sprint 4 — CRUD Screens

O Sprint 4 implementa as três screens de dados com operações CRUD completas: Routines, Habits e Tasks. Todas seguem o padrão consistente definido pela BR-TUI-005, com keybindings Ctrl+ para ações e formulários para criação/edição. A HabitsScreen tem complexidade adicional por incluir ações de instância (done/skip com substatus).

A RoutinesScreen é implementada primeiro porque é a mais simples e valida o padrão CRUD. A HabitsScreen vem em duas entregas (instâncias + CRUD do hábito) por ser a screen mais complexa. A TasksScreen fecha o sprint.

**Branch:** `feat/tui-crud-screens`

**Critério de conclusão:** CRUD completo em Routines, Habits e Tasks funcional via TUI, com validações e confirmações.

**BR-TUI-005 + RoutinesScreen**

- [ ] Criar `src/timeblock/tui/widgets/confirm_dialog.py`
- [ ] Implementar RoutinesScreen com lista, create, edit, delete, activate
- [ ] Keybindings: `N`=nova (modal), `Ctrl+E`=editar, `Ctrl+X`=deletar [MODAL], `Enter`=ativar
- [ ] Criar `tests/unit/test_tui/test_screens/test_routines.py`
- [ ] Teste: `test_br_tui_005_n_opens_create_modal`
- [ ] Teste: `test_br_tui_005_ctrl_x_requires_confirmation`
- [ ] Teste: `test_br_tui_005_successful_operation_refreshes_list`
- [ ] Validar: CRUD de rotinas funcional, confirmação de delete

**BR-TUI-010: HabitsScreen — Ações de Instância**

- [ ] Implementar HabitsScreen com lista de hábitos e instâncias do dia
- [ ] Exibir instâncias com status colorido (pending/done/not_done)
- [ ] Implementar ação Ctrl+Enter (done, solicita duração) e Ctrl+S (skip, solicita razão)
- [ ] Criar `tests/unit/test_tui/test_screens/test_habits.py`
- [ ] Teste: `test_br_tui_010_lists_today_instances`
- [ ] Teste: `test_br_tui_010_ctrl_enter_marks_done_asks_duration`
- [ ] Teste: `test_br_tui_010_ctrl_s_marks_skip_asks_reason`
- [ ] Teste: `test_br_tui_010_shows_substatus_color`
- [ ] Validar: instâncias marcáveis como done/skip com substatus

**HabitsScreen — CRUD de Hábitos**

- [ ] Adicionar create/edit/delete de hábitos na HabitsScreen
- [ ] N abre modal com campos (nome, duração, recorrência)
- [ ] Ctrl+E edita, Ctrl+X deleta com confirmação
- [ ] Integrar com HabitService
- [ ] Testes de CRUD para hábitos
- [ ] Validar: CRUD completo de hábitos funcional

**TasksScreen**

- [ ] Implementar TasksScreen com lista, create, edit, delete, marcar completa
- [ ] N abre modal, Ctrl+E edita, Ctrl+X deleta, Ctrl+K completa
- [ ] Integrar com TaskService
- [ ] Criar `tests/unit/test_tui/test_screens/test_tasks.py`
- [ ] Testes de CRUD para tarefas
- [ ] Validar: CRUD completo de tarefas funcional

---

### Sprint 5 — Timer

O Sprint 5 implementa a screen mais interativa da TUI: o Timer com display live atualizado a cada segundo. Esta screen exige integração com `set_interval` do Textual para atualização contínua e com o TimerService existente para persistência de sessões. O timer ativo também passa a ser visível no footer de qualquer screen, completando a integração com BR-TUI-007.

**Branch:** `feat/tui-timer`

**Critério de conclusão:** Timer funcional com display live, pause/resume, sessão salva ao stop, timer visível no footer global.

**BR-TUI-006: Timer Screen Live Display**

- [ ] Implementar TimerScreen com display atualizado a cada segundo
- [ ] Keybindings: `Ctrl+S`=start, `Ctrl+P`=pause/resume, `Ctrl+Enter`=stop, `Ctrl+W`=cancel [MODAL]
- [ ] Integrar com TimerService existente
- [ ] Atualizar footer para exibir timer ativo globalmente
- [ ] Implementar confirmação ao sair com timer ativo (Ctrl+Q modal informa perda de sessão)
- [ ] Criar `tests/unit/test_tui/test_screens/test_timer.py`
- [ ] Teste: `test_br_tui_006_timer_display_updates`
- [ ] Teste: `test_br_tui_006_ctrl_s_starts_timer`
- [ ] Teste: `test_br_tui_006_ctrl_p_toggles_pause`
- [ ] Teste: `test_br_tui_006_ctrl_enter_stops_saves_session`
- [ ] Teste: `test_br_tui_006_ctrl_w_cancel_requires_confirmation`
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

---

**Próxima revisão:** Após Sprint 3.2 concluído

**Última atualização:** 4 de Março de 2026
