# Sprints

- **Versão:** 1.0.0
- **Data:** 5 de Fevereiro de 2026
- **Status:** Single Source of Truth (SSOT)

---

## Visão Geral

Este documento acompanha as sprints ativas do projeto ATOMVS TimeBlock Terminal. Cada sprint representa um ciclo de entregas incrementais onde requisitos formalizados são decompostos em tarefas atômicas, validados e implementados com rastreabilidade completa. A metodologia de engenharia de requisitos, análise comportamental e implementação orientada por testes está documentada na seção "Desenvolvimento" do README.md.

O histórico de sprints concluídas (v1.0.0 a v1.6.0) está arquivado em `docs/core/sprints-archive.md`.

---

## v1.7.0 — TUI com Textual (Em Andamento)

A v1.7.0 marca a transição do ATOMVS TimeBlock de ferramenta CLI pura para uma aplicação interativa completa com interface TUI baseada em Textual. A CLI permanece como interface de automação e scripts, enquanto a TUI oferece navegação visual para uso diário interativo. O escopo inclui reestruturação do repositório (flatten de `cli/`, branding ATOMVS), implementação de 5 screens navegáveis (Dashboard, Routines, Habits, Tasks, Timer) com design Material-like e 10 business rules novas do domínio TUI.

**Métricas de acompanhamento:**

| Métrica               | Início (v1.6.0) | Meta v1.7.0 |
| --------------------- | --------------- | ----------- |
| Cobertura global      | 87%             | >= 85%      |
| Cobertura tui/        | 0%              | >= 80%      |
| Testes totais         | 778             | 830+        |
| Erros mypy            | 0               | 0           |
| BRs TUI implementadas | 0/10            | 10/10       |
| Screens funcionais    | 0/5             | 5/5         |

---

### Sprint 0 — Reestruturação e Branding

O Sprint 0 prepara a infraestrutura do repositório para receber a TUI. Inclui a adoção do branding ATOMVS (ADR-032), o rename de `docs/ssot/` para `docs/core/`, a documentação arquitetural da TUI (ADR-031), as Business Rules do domínio TUI, o flatten do diretório `cli/` para a raiz, e a atualização de toda a cadeia CI/CD e documentação. Nenhum código de aplicação é modificado nesta sprint — apenas estrutura, configuração e documentação.

A decisão de incluir branding e reestruturação na mesma sprint reflete que ambos são pré-requisitos organizacionais: o flatten elimina o `cd cli/` de todos os workflows, e o branding ATOMVS estabelece o namespace definitivo antes de criar novos pacotes.

**Branch:** `docs/branding` → merge em `develop`

**Critério de conclusão:** Pipeline CI/CD verde, `pytest` executável a partir da raiz, referências internas atualizadas, zero menção a `docs/ssot/` ou paths com `cli/`.

- [x] ADR-032: Branding ATOMVS + namespace `atomvs-timeblock-*`
- [x] Atualizar `docs/core/architecture.md` — nomenclatura repos seção 13.1
- [x] Atualizar `docs/core/roadmap.md` — sumário executivo com branding
- [x] Renomear `docs/ssot/` → `docs/core/`
- [x] Atualizar referências internas `docs/ssot/` → `docs/core/` em todos os .md
- [x] ADR-031: Implementação TUI com Textual
- [ ] Seção BR-TUI (BR-TUI-001 a BR-TUI-010) em `docs/core/business-rules.md`
- [ ] Criar `docs/core/sprints.md` (este documento)
- [ ] Criar `docs/core/sprints-archive.md` (histórico v1.0.0 a v1.6.0)
- [ ] Adicionar parágrafos introdutórios nas seções do `docs/core/business-rules.md`
- [ ] Adicionar parágrafos introdutórios nas seções do `docs/core/architecture.md`
- [ ] Criar `docs/core/development.md` — SSOT do processo de desenvolvimento
- [ ] Atualizar README.md seção "Desenvolvimento" — resumo breve + link para development.md
- [ ] Atualizar `docs/decisions/README.md` — adicionar ADR-031 e ADR-032 ao índice
- [ ] Flatten: mover `cli/src/` → `src/`
- [ ] Flatten: mover `cli/tests/` → `tests/`
- [ ] Flatten: mover `cli/data/` → `data/`
- [ ] Flatten: mover `cli/pyproject.toml` → `pyproject.toml`
- [ ] Flatten: mover `cli/pytest.ini` → `pytest.ini`
- [ ] Flatten: mover `cli/.ruff.toml` → `.ruff.toml`
- [ ] Remover diretório `cli/` vazio
- [ ] Atualizar `.gitlab-ci.yml` — remover `cd cli/` de todos os jobs
- [ ] Atualizar `.github/workflows/ci.yml` — remover `cd cli/`
- [ ] Atualizar `scripts/test-cicd.sh` — paths sem `cli/`
- [ ] Atualizar `Dockerfile` e `Dockerfile.test` — paths sem `cli/`
- [ ] Atualizar `README.md` — paths, nome do repo, instruções
- [ ] Atualizar `CHANGELOG.md` — entrada v1.7.0-dev
- [ ] Atualizar `mkdocs.yml` — paths sem `cli/`
- [ ] Validar: `python -m pytest tests/ -v` passa a partir da raiz
- [ ] Validar: `ruff check .` sem erros a partir da raiz
- [ ] Validar: `mypy src/timeblock` sem erros a partir da raiz
- [ ] Validar: pipeline CI/CD verde no GitLab e GitHub

---

### Sprint 1 — Foundation

O Sprint 1 constrói a fundação arquitetural da TUI: o session helper que toda operação TUI utilizará, o tema visual Material-like com o widget Card reutilizável, e o entry point que detecta automaticamente se deve abrir TUI ou CLI. Estas três entregas são pré-requisitos para qualquer screen funcional.

A ordem das entregas é deliberada: o session helper (BR-TUI-009) vem primeiro porque define o padrão de acesso a dados que todas as screens consumirão. O tema (BR-TUI-008) vem segundo porque os widgets de UI precisam do TCSS definido. O entry point (BR-TUI-001) vem por último porque depende do `app.py` que usa tema e widgets.

**Branch:** `feat/tui-foundation`

**Critério de conclusão:** `timeblock` sem args abre TUI mínima com tema aplicado, `timeblock --help` abre CLI, session helper funcional.

**BR-TUI-009: Compartilhamento da Service Layer**

- [ ] Criar `src/timeblock/tui/__init__.py`
- [ ] Criar `src/timeblock/tui/session.py` com context manager `get_session()`
- [ ] Criar `tests/unit/test_tui/__init__.py`
- [ ] Criar `tests/unit/test_tui/test_session.py`
- [ ] Teste: `test_br_tui_009_session_provides_working_session`
- [ ] Teste: `test_br_tui_009_session_commits_on_success`
- [ ] Teste: `test_br_tui_009_session_rollbacks_on_error`
- [ ] Validar: 3 testes verdes, `get_session()` funcional com services existentes

**BR-TUI-008: Consistência Visual (Material-like)**

- [ ] Criar `src/timeblock/tui/styles/` com `__init__.py`
- [ ] Criar `src/timeblock/tui/styles/theme.tcss` com paleta completa
- [ ] Criar `src/timeblock/tui/widgets/__init__.py`
- [ ] Criar `src/timeblock/tui/widgets/card.py` — widget Card reutilizável
- [ ] Criar `tests/unit/test_tui/test_widgets/__init__.py`
- [ ] Criar `tests/unit/test_tui/test_widgets/test_card.py`
- [ ] Teste: `test_br_tui_008_theme_file_exists`
- [ ] Teste: `test_br_tui_008_card_renders_title`
- [ ] Teste: `test_br_tui_008_card_renders_content`
- [ ] Validar: Card renderiza com estilo definido, tema carrega sem erros

**BR-TUI-001: Entry Point Detection**

- [ ] Criar `src/timeblock/tui/app.py` — TimeBlockApp mínimo (tela com título)
- [ ] Modificar `src/timeblock/main.py` — detecção `sys.argv`
- [ ] Atualizar `pyproject.toml` — dependência opcional `[tui]`
- [ ] Criar `tests/unit/test_tui/test_entry_point.py`
- [ ] Teste: `test_br_tui_001_no_args_launches_tui`
- [ ] Teste: `test_br_tui_001_with_args_launches_cli`
- [ ] Teste: `test_br_tui_001_fallback_without_textual`
- [ ] Validar: `timeblock` abre TUI, `timeblock --help` abre CLI

---

### Sprint 2 — Navegação

O Sprint 2 implementa a estrutura de navegação completa da TUI: sidebar com indicador de screen ativa, keybindings globais (quit, help, escape) e status bar persistente no rodapé. Ao final desta sprint, a TUI tem o esqueleto navegável com 5 screens placeholder e feedback visual completo.

A sidebar e os keybindings definem o contrato de interação que todas as screens seguirão. A status bar fornece contexto persistente (rotina ativa, timer, hora) independente da screen em foco.

**Branch:** `feat/tui-navigation`

**Critério de conclusão:** Navegação funcional entre 5 screens via teclado, sidebar indica screen ativa, status bar exibe rotina e hora, `q` fecha, `?` mostra help.

**BR-TUI-002: Screen Navigation**

- [ ] Criar `src/timeblock/tui/widgets/sidebar.py`
- [ ] Criar `src/timeblock/tui/screens/__init__.py`
- [ ] Criar 5 screens placeholder (dashboard.py, routines.py, habits.py, tasks.py, timer.py)
- [ ] Atualizar `app.py` — compose sidebar + content area, bindings de navegação
- [ ] Criar `tests/unit/test_tui/test_navigation.py`
- [ ] Teste: `test_br_tui_002_initial_screen_is_dashboard`
- [ ] Teste: `test_br_tui_002_numeric_keybinding_navigation`
- [ ] Teste: `test_br_tui_002_mnemonic_keybinding_navigation`
- [ ] Teste: `test_br_tui_002_sidebar_shows_active_screen`
- [ ] Validar: navegação entre 5 screens via teclado funcional

**BR-TUI-004: Global Keybindings**

- [ ] Implementar `q` → quit
- [ ] Implementar `?` → help overlay
- [ ] Implementar `escape` → fechar modal ou voltar ao Dashboard
- [ ] Criar `tests/unit/test_tui/test_keybindings.py`
- [ ] Teste: `test_br_tui_004_quit_keybinding`
- [ ] Teste: `test_br_tui_004_help_overlay`
- [ ] Teste: `test_br_tui_004_escape_returns_to_dashboard`
- [ ] Validar: `q` fecha, `?` exibe help, `escape` retorna ao Dashboard

**BR-TUI-007: Status Bar**

- [ ] Criar `src/timeblock/tui/widgets/status_bar.py`
- [ ] Integrar na composição do app (rodapé fixo)
- [ ] Consultar RoutineService para rotina ativa
- [ ] Exibir hora atual (atualiza a cada minuto)
- [ ] Criar `tests/unit/test_tui/test_widgets/test_status_bar.py`
- [ ] Teste: `test_br_tui_007_shows_active_routine`
- [ ] Teste: `test_br_tui_007_shows_current_time`
- [ ] Teste: `test_br_tui_007_shows_no_routine_message`
- [ ] Validar: status bar exibe rotina ativa (ou "[Sem rotina]") e hora

---

### Sprint 3 — Dashboard

O Sprint 3 transforma o placeholder do Dashboard em uma screen funcional com dados reais do banco. É a primeira screen a consumir services via session-per-action, servindo como validação do padrão arquitetural definido no Sprint 1. Os cards exibem resumo do dia: hábitos com status, tarefas pendentes e timer ativo.

**Branch:** `feat/tui-dashboard`

**Critério de conclusão:** Dashboard exibe dados reais do banco em cards formatados, atualiza ao receber foco.

**BR-TUI-003: Dashboard Screen**

- [ ] Implementar DashboardScreen com 3 cards (Hábitos Hoje, Tarefas, Timer)
- [ ] Integrar com RoutineService, HabitInstanceService, TaskService
- [ ] Usar session-per-action para carregar dados
- [ ] Implementar refresh on focus
- [ ] Criar `tests/unit/test_tui/test_screens/__init__.py`
- [ ] Criar `tests/unit/test_tui/test_screens/test_dashboard.py`
- [ ] Teste: `test_br_tui_003_shows_active_routine_name`
- [ ] Teste: `test_br_tui_003_shows_no_routine_message`
- [ ] Teste: `test_br_tui_003_shows_today_habits_with_status`
- [ ] Teste: `test_br_tui_003_shows_pending_tasks`
- [ ] Teste: `test_br_tui_003_refreshes_on_focus`
- [ ] Validar: Dashboard exibe dados reais, cards formatados com cores de status

---

### Sprint 4 — CRUD Screens

O Sprint 4 implementa as três screens de dados com operações CRUD completas: Routines, Habits e Tasks. Todas seguem o padrão consistente definido pela BR-TUI-005 (keybindings `n`/`e`/`x`/`enter`, confirmação de delete, refresh após operação). A HabitsScreen tem complexidade adicional por incluir ações de instância (done/skip com substatus).

A RoutinesScreen é implementada primeiro porque é a mais simples e valida o padrão CRUD. A HabitsScreen vem em duas entregas (instâncias + CRUD do hábito) por ser a screen mais complexa. A TasksScreen fecha o sprint.

**Branch:** `feat/tui-crud-screens`

**Critério de conclusão:** CRUD completo em Routines, Habits e Tasks funcional via TUI, com validações e confirmações.

**BR-TUI-005 + RoutinesScreen**

- [ ] Criar `src/timeblock/tui/widgets/confirm_dialog.py`
- [ ] Implementar RoutinesScreen com lista, create, edit, delete, activate
- [ ] Keybindings: `n`=nova, `e`=editar, `x`=deletar, `enter`=ativar
- [ ] Criar `tests/unit/test_tui/test_screens/test_routines.py`
- [ ] Teste: `test_br_tui_005_create_opens_form`
- [ ] Teste: `test_br_tui_005_delete_requires_confirmation`
- [ ] Teste: `test_br_tui_005_successful_operation_refreshes_list`
- [ ] Validar: CRUD de rotinas funcional, confirmação de delete

**BR-TUI-010: HabitsScreen — Ações de Instância**

- [ ] Implementar HabitsScreen com lista de hábitos e instâncias do dia
- [ ] Exibir instâncias com status colorido (pending/done/not_done)
- [ ] Implementar ação Done (solicita duração) e Skip (solicita razão)
- [ ] Criar `tests/unit/test_tui/test_screens/test_habits.py`
- [ ] Teste: `test_br_tui_010_lists_today_instances`
- [ ] Teste: `test_br_tui_010_mark_done_asks_duration`
- [ ] Teste: `test_br_tui_010_mark_skip_asks_reason`
- [ ] Teste: `test_br_tui_010_shows_substatus_color`
- [ ] Validar: instâncias marcáveis como done/skip com substatus

**HabitsScreen — CRUD de Hábitos**

- [ ] Adicionar create/edit/delete de hábitos na HabitsScreen
- [ ] Formulário com nome, duração, recorrência
- [ ] Integrar com HabitService
- [ ] Testes de CRUD para hábitos
- [ ] Validar: CRUD completo de hábitos funcional

**TasksScreen**

- [ ] Implementar TasksScreen com lista, create, edit, delete, marcar completa
- [ ] Integrar com TaskService
- [ ] Criar `tests/unit/test_tui/test_screens/test_tasks.py`
- [ ] Testes de CRUD para tarefas
- [ ] Validar: CRUD completo de tarefas funcional

---

### Sprint 5 — Timer

O Sprint 5 implementa a screen mais interativa da TUI: o Timer com display live atualizado a cada segundo. Esta screen exige integração com `set_interval` do Textual para atualização contínua e com o TimerService existente para persistência de sessões. O timer ativo também passa a ser visível na status bar de qualquer screen, completando a integração com BR-TUI-007.

**Branch:** `feat/tui-timer`

**Critério de conclusão:** Timer funcional com display live, pause/resume, sessão salva ao stop, timer visível na status bar global.

**BR-TUI-006: Timer Screen Live Display**

- [ ] Implementar TimerScreen com display atualizado a cada segundo
- [ ] Keybindings: `s`=start, `p`=pause/resume, `enter`=stop, `c`=cancel
- [ ] Integrar com TimerService existente
- [ ] Atualizar StatusBar para exibir timer ativo globalmente
- [ ] Implementar confirmação ao sair com timer ativo (complemento BR-TUI-004)
- [ ] Criar `tests/unit/test_tui/test_screens/test_timer.py`
- [ ] Teste: `test_br_tui_006_timer_display_updates`
- [ ] Teste: `test_br_tui_006_start_keybinding`
- [ ] Teste: `test_br_tui_006_pause_resume_toggle`
- [ ] Teste: `test_br_tui_006_stop_saves_session`
- [ ] Teste: `test_br_tui_006_cancel_requires_confirmation`
- [ ] Teste: `test_br_tui_006_active_timer_in_status_bar`
- [ ] Validar: timer live funcional, sessão persistida, status bar integrada

---

### Sprint 6 — Polimento e Release

O Sprint 6 fecha a v1.7.0 com revisão de cobertura, validação completa de regressão e preparação do release. Nenhuma funcionalidade nova é adicionada — o foco é qualidade, documentação e empacotamento.

**Branch:** `release/v1.7.0`

**Critério de conclusão:** Tag v1.7.0 criada, pipeline verde, changelog completo, cobertura >= 80% em tui/.

**Cobertura e Revisão**

- [ ] Verificar cobertura do pacote `tui/` — meta 80%
- [ ] Adicionar testes faltantes para edge cases
- [ ] Executar `mypy src/timeblock --check-untyped-defs` — zero erros
- [ ] Executar `ruff check .` — zero warnings
- [ ] Testar regressão CLI — todos os testes existentes passam
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

| Data       | Versão | Mudanças                                            |
| ---------- | ------ | --------------------------------------------------- |
| 2026-02-05 | 1.0.0  | Criação inicial — planejamento v1.7.0 com 7 sprints |

---

**Próxima revisão:** Após Sprint 0 concluído

**Última atualização:** 5 de Fevereiro de 2026
