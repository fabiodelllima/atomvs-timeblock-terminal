# Technical Debt

**Versão:** 2.7.0

**Status:** SSOT

**Documentos Relacionados:** roadmap.md, quality-metrics.md, sprint-4-code-review.md

---

## 1. Inventário

| ID    | Descrição                                      | Severidade | Status    | Resolvido em | Sprint planejado         |
| ----- | ---------------------------------------------- | ---------- | --------- | ------------ | ------------------------ |
| DT001 | 156 erros mypy                                 | CRÍTICA    | RESOLVIDO | Jan/2026     | v1.4.0 S1-S3             |
| DT002 | 15 testes skipped                              | ALTA       | RESOLVIDO | Jan/2026     | v1.4.0 S4                |
| DT003 | Cobertura abaixo de 80%                        | ALTA       | RESOLVIDO | Mar/2026     | v1.6.0                   |
| DT004 | EventReordering parcial (61%)                  | MÉDIA      | RESOLVIDO | Fev/2026     | -                        |
| DT005 | Código morto                                   | BAIXA      | RESOLVIDO | Fev/2026     | -                        |
| DT006 | Idioma misto EN/PT em CLI                      | MÉDIA      | RESOLVIDO | Fev/2026     | v1.5.0                   |
| DT007 | migration_001 sem cobertura                    | BAIXA      | ACEITO    | -            | -                        |
| DT008 | GitHub Actions --fail-under divergente         | MÉDIA      | RESOLVIDO | Mar/2026     | v1.7.0                   |
| DT009 | FocusablePanel: C_HIGHLIGHT na base            | ALTA       | PENDENTE  | -            | v1.7.0                   |
| DT010 | FocusablePanel: flag \_showing_placehold.      | ALTA       | PENDENTE  | -            | v1.7.0                   |
| DT011 | FocusablePanel: count em dois lugares          | ALTA       | PENDENTE  | -            | v1.7.0                   |
| DT012 | DI inconsistente entre services                | MÉDIA      | PENDENTE  | -            | v2.0                     |
| DT013 | \_parse_time duplicado (crud_habits/tasks)     | BAIXA      | PENDENTE  | -            | v1.7.0                   |
| DT014 | Keybindings divergentes BR vs código           | ALTA       | RESOLVIDO | Mar/2026     | feat/tui-dashboard-timer |
| DT015 | AgendaPanel sem auto-refresh (set_interval)    | MÉDIA      | RESOLVIDO | Mar/2026     | feat/tui-dashboard-timer |
| DT016 | load_active_timer: elapsed int vs str MM:SS    | ALTA       | RESOLVIDO | Mar/2026     | feat/tui-dashboard-timer |
| DT017 | MetricsPanel stub — load_metrics não existe    | MÉDIA      | RESOLVIDO | Mar/2026     | feat/metrics-panel       |
| DT018 | load_tasks omite completed/cancelled           | BAIXA      | RESOLVIDO | Mar/2026     | feat/task-lifecycle      |
| DT019 | command_bar.py stub vazio (0 bytes)            | BAIXA      | PENDENTE  | -            | Sprint 6+                |
| DT020 | Agenda: viewport cortada, sem auto-scroll      | BAIXA      | RESOLVIDO | Mar/2026     | feat/agenda-viewport     |
| DT021 | Loaders/CRUDs: ORM fora da sessão (frágil)     | MÉDIA      | RESOLVIDO | Mar/2026     | feat/tui-dashboard-timer |
| DT022 | Logging: adoção zero fora de habit_inst_svc    | MÉDIA      | RESOLVIDO | Mar/2026     | feat/structured-logging  |
| DT023 | Instâncias diárias: geração manual obrigatória | ALTA       | RESOLVIDO | Mar/2026     | feat/tui-dashboard-timer |
| DT024 | Keybindings Ctrl+N inoperantes em VTE/GNOME    | ALTA       | RESOLVIDO | Mar/2026     | feat/tui-dashboard-timer |
| DT025 | Pyright como job CI complementar               | BAIXA      | PENDENTE  | -            | Sprint futuro            |
| DT034 | mark_completed sem done_substatus              | CRITICA    | PENDENTE  | -            | fix/dashboard-quality    |
| DT035 | Undo handler nao limpa skip_reason/skip_note   | CRITICA    | PENDENTE  | -            | fix/dashboard-quality    |
| DT036 | TimerStopAndDoneRequest sem handler             | ALTA       | PENDENTE  | -            | fix/dashboard-quality    |
| DT037 | v (done) deveria abrir modal de substatus      | ALTA       | PENDENTE  | -            | fix/dashboard-quality    |
| DT038 | s (postpone) deveria abrir FormModal de edit   | MEDIA      | PENDENTE  | -            | fix/dashboard-quality    |
| DT039 | s (skip) deveria abrir modal de SkipReason     | MEDIA      | PENDENTE  | -            | fix/dashboard-quality    |
| DT040 | n sem rotina: silent no-op ao inves de modal   | MEDIA      | PENDENTE  | -            | fix/dashboard-quality    |
| DT041 | BR-TUI-004/017/018/021 keybindings obsoletos   | ALTA       | PENDENTE  | -            | docs/br-update           |
| DT042 | BR-HABITINSTANCE-001 nao documenta undo        | ALTA       | PENDENTE  | -            | docs/br-update           |

## 1b. Quick Status

- [x] DT001 — 156 erros mypy
- [x] DT002 — 15 testes skipped
- [x] DT003 — Cobertura abaixo de 80%
- [x] DT004 — EventReordering parcial
- [x] DT005 — Código morto
- [x] DT006 — Idioma misto EN/PT
- [x] DT007 — migration_001 sem cobertura (ACEITO)
- [x] DT008 — GitHub Actions divergente
- [ ] DT009 — FocusablePanel: C_HIGHLIGHT na base
- [ ] DT010 — FocusablePanel: flag \_showing_placeholders
- [ ] DT011 — FocusablePanel: count em dois lugares
- [ ] DT012 — DI inconsistente entre services
- [x] DT013 — _parse_time consolidado em validators
- [x] DT014 — Keybindings divergentes
- [x] DT015 — AgendaPanel sem auto-refresh
- [x] DT016 — load_active_timer elapsed/name
- [x] DT017 — MetricsPanel stub
- [x] DT018 — load_tasks omite completed/cancelled
- [ ] DT019 — command_bar.py vazio
- [x] DT020 — Agenda viewport cortada
- [x] DT021 — Loaders/CRUDs: ORM fora da sessão
- [x] DT022 — Logging: adoção zero fora de habit_instance_service
- [x] DT023 — Instâncias diárias: geração manual obrigatória
- [x] DT024 — Keybindings Ctrl+Números inoperantes em VTE/GNOME
- [ ] DT025 — Pyright como job CI complementar ao mypy e ruff
- [ ] DT026 — load_metrics sem filtro de rotina ativa
- [ ] DT034 — mark_completed sem done_substatus (CRITICA)
- [ ] DT035 — Undo handler nao limpa skip_reason/skip_note (CRITICA)
- [ ] DT036 — TimerStopAndDoneRequest sem handler
- [ ] DT037 — v (done) deveria abrir modal de substatus
- [ ] DT038 — s (postpone) deveria abrir FormModal de edit
- [ ] DT039 — s (skip) deveria abrir modal de SkipReason
- [ ] DT040 — n sem rotina: silent no-op ao inves de modal
- [ ] DT041 — BR-TUI-004/017/018/021 keybindings obsoletos
- [ ] DT042 — BR-HABITINSTANCE-001 nao documenta undo
- [x] DT027 — FormModal sem suporte a campo select (recorrencia)
- [x] DT028 — Enter sem ação em habit selecionado (ADR-037)
- [x] DT029 — Conflitos de horario detectados no CRUD habits
- [x] DT030 — Help overlay completo (ADR-037)
- [x] DT031 — Auto-scroll desabilitado (call_later travava TUI)
- [x] DT032 — Migração de banco manual para Task lifecycle
- [x] DT033 — 3 testes CRUD routines quebrados por VerticalScroll

**Resolvidos:** 27/42 | **Pendentes:** 15/42 | **Aceitos:** 1/42

---


## 1c. Detalhamento de Itens Pendentes (Novos)

### DT-034: mark_completed sem done_substatus (CRITICA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** `HabitInstanceService.mark_completed()` seta `status=DONE` sem setar `done_substatus`. Viola BR-HABITINSTANCE-002 regra 1.
- **Correcao:** Abrir modal de substatus ao pressionar `v` (ADR-038 D3).
- **BRs afetadas:** BR-HABITINSTANCE-002, BR-TUI-004

### DT-035: Undo handler nao limpa skip_reason/skip_note (CRITICA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** Handler undo limpa `done_substatus` e `not_done_substatus` mas nao limpa `skip_reason`, `skip_note`, `completion_percentage`. Viola `validate_status_consistency()`.
- **Correcao:** Limpar todos os campos no undo.
- **BRs afetadas:** BR-SKIP-002, BR-HABITINSTANCE-002

### DT-036: TimerStopAndDoneRequest sem handler (ALTA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** `v` em habito com timer ativo e silenciosamente ignorado.
- **Correcao:** Implementar handler com modal de opcoes (ADR-038 D4).
- **BRs afetadas:** BR-TUI-021

### DT-037: v (done) deveria abrir modal de substatus (ALTA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** `v` marca done sem substatus. Viola BR-HABITINSTANCE-002.
- **Correcao:** Abrir modal com Select de DoneSubstatus (ADR-038 D3).
- **BRs afetadas:** BR-HABITINSTANCE-002, BR-HABITINSTANCE-003

### DT-038: s (postpone) deveria abrir FormModal de edit (MEDIA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** Handler chama `update_task` sem parametros. Nenhuma acao visivel.
- **Correcao:** `s` abre mesmo FormModal que `e` (ADR-038 D5).
- **BRs afetadas:** BR-TASK-008, BR-TUI-018

### DT-039: s (skip) deveria abrir modal de SkipReason (MEDIA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** `s` aplica `SkipReason.OTHER` hardcoded. Viola BR-SKIP-001.
- **Correcao:** Abrir modal com Select de SkipReason (ADR-038 D6).
- **BRs afetadas:** BR-SKIP-001, BR-SKIP-004

### DT-040: n sem rotina: silent no-op no habits panel (MEDIA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** `n` com habits focado e sem rotina nao faz nada.
- **Correcao:** Redirecionar para criacao de rotina (ADR-038 D9).
- **BRs afetadas:** BR-TUI-017

### DT-041: BR-TUI-004/017/018/021 keybindings obsoletos (ALTA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** BRs documentam Ctrl+Enter, Ctrl+S, Shift+Enter. Codigo usa v, s, space, c (ADR-037).
- **Correcao:** Reescrever secoes de keybindings nas 4 BRs.
- **BRs afetadas:** BR-TUI-004, BR-TUI-017, BR-TUI-018, BR-TUI-021

### DT-042: BR-HABITINSTANCE-001 nao documenta undo (ALTA)

- **Descoberto:** 15/03/2026 (revisao de testes e2e)
- **Impacto:** BR define DONE e NOT_DONE como [FINAL]. Codigo implementa undo.
- **Correcao:** Adicionar transicao undo + BR-HABITINSTANCE-007 (ADR-038 D1).
- **BRs afetadas:** BR-HABITINSTANCE-001

---

## 2. Detalhamento de Itens Resolvidos

### DT-001: Erros Mypy (RESOLVIDO)

- **Descoberto:** 16/01/2026
- **Resolvido:** Jan/2026
- **Impacto original:** 156 erros em modo strict, commands não passavam no type checker
- **Resolução:** Instalação de stubs, correção de Session.exec, correção de SQLAlchemy datetime comparisons, completude do Service Layer, null checks em commands
- **Estado final:** 0 erros em 45 arquivos fonte

### DT-002: Testes Skipped (RESOLVIDO)

- **Descoberto:** 16/01/2026
- **Resolvido:** Jan/2026
- **Impacto original:** 15 testes marcados como skip (stubs vazios, timer API v1, migrations)
- **Resolução:** Implementação dos stubs, atualização para API v2, remoção de testes obsoletos
- **Estado final:** 0 testes skipped, 618 passando

### DT-003: Cobertura Abaixo de 80% (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Mar/2026
- **Cobertura original:** 76%
- **Cobertura atual:** ~81% (threshold 80%)
- **Resolução:** Sprint 3.2 e Sprint 4 adicionaram ~300 testes TUI

### DT-004: EventReordering Parcial (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Cobertura original:** 61%
- **Cobertura atual:** 86%
- **Resolução:** Testes de integração cobrindo cenários de reorganização

### DT-005: Código Morto (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Verificação:** `ruff check src/timeblock --select F401,F841` retorna 0 issues
- **Resolução:** Limpeza gradual durante refatorações

### DT-006: Idioma Misto EN/PT (RESOLVIDO)

- **Descoberto:** Jan/2026
- **Resolvido:** Fev/2026
- **Referência:** ADR-018 (Language Standards)
- **Resolução:** Tradução de mensagens CLI para PT-BR, criação de script lint-i18n.py
- **Verificação:** `python scripts/lint-i18n.py` retorna 0 inconsistências

---

## 3. Detalhamento de Itens Pendentes

### DT-007: migration_001 Sem Cobertura (ACEITO)

- **Cobertura:** 0%
- **Justificativa:** Migração one-shot já executada em produção. Custo de testar supera benefício. Será removida quando migração definitiva for criada (v2.0.0).
- **Decisão:** Aceitar o débito. Não investir esforço em cobertura.

### DT-008: GitHub Actions --fail-under Divergente

- **Descoberto:** 08/03/2026
- **Impacto:** Job `CI / test (push)` falha no GitHub com `--fail-under=85` enquanto GitLab usa 80%. GitHub Actions também usa Python 3.13 enquanto projeto roda em 3.14.
- **Arquivo:** `.github/workflows/ci.yml`
- **Ação:** Alinhar `--fail-under=80` e `python-version: "3.14"` com GitLab CI.
- **Sprint:** feat/tui-dashboard-timer ou próximo commit de CI.

### DT-009: C_HIGHLIGHT Acoplado na Classe Base FocusablePanel (CRITICAL-001)

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** FocusablePanel importa `C_HIGHLIGHT` de `colors.py` e aplica highlight em `_build_empty_state`. Classe base conhece e decide cor de cursor — responsabilidade de apresentação que pertence às subclasses ou ao TCSS.
- **Arquivo:** `src/timeblock/tui/widgets/focusable_panel.py` linha 11
- **Ação:** Extrair highlight para método `_apply_cursor_highlight` sobrescrevível, ou usar classes CSS do Textual.
- **Referência:** sprint-4-code-review.md CRITICAL-001
- **Sprint:** v1.7.0 (pré-release)

### DT-010: \_showing_placeholders Como Flag Booleano Solto (CRITICAL-002)

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** Booleano gerenciado manualmente em `update_data()` de cada subclasse. Estado duplicado — pode ser derivado da ausência de dados reais. Bug silencioso se subclasse esquecer de setar o flag.
- **Arquivos:** `focusable_panel.py` linha 30, `habits_panel.py` linhas 35-39, `tasks_panel.py` linhas 38-42
- **Ação:** Transformar em propriedade derivada ou encapsular em método `_set_placeholder_mode(count)`.
- **Referência:** sprint-4-code-review.md CRITICAL-002
- **Sprint:** v1.7.0 (pré-release)

### DT-011: Count Definido em Dois Lugares Divergentes (CRITICAL-003)

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** `update_data` define `_set_item_count(N)` e `_build_empty_state(..., count=N)` recebe N separadamente. Se divergirem, cursor aceita posições invisíveis. Já aconteceu durante a Sprint 4.
- **Arquivos:** `tasks_panel.py` linhas 41 e 100
- **Ação:** Unificar em método único `_enter_placeholder_mode(placeholder, hint, count)` que seta count e retorna linhas.
- **Referência:** sprint-4-code-review.md CRITICAL-003
- **Sprint:** v1.7.0 (pré-release)

### DT-012: DI Inconsistente Entre Services

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** Três padrões de DI coexistem: `RoutineService(s)` (constructor), `HabitInstanceService().method(session=s)` (parameter + instance), `TaskService.method(session=s)` (static + parameter). Confuso para contribuidores.
- **Arquivo:** `src/timeblock/tui/screens/dashboard/loader.py`
- **Ação:** Unificar na v2.0 com Application Layer e Repository Pattern.
- **Referência:** sprint-4-code-review.md WARNING-001
- **Sprint:** v2.0

### DT-013: \_parse_time Duplicado em Dois Módulos

- **Descoberto:** 08/03/2026 (Sprint 4 Code Review)
- **Impacto:** Mesma função `_parse_time(value: str) -> time` em `crud_habits.py` e `crud_tasks.py`. Bug fix em um não propaga para o outro.
- **Ação:** Mover para `src/timeblock/tui/utils.py` ou reutilizar `validators.py`.
- **Referência:** sprint-4-code-review.md WARNING-006
- **Sprint:** v1.7.0

### DT-014: Keybindings Divergentes Entre BR-TUI-004 e Código

- **Descoberto:** 08/03/2026
- **Impacto:** BR-TUI-004 especifica `Ctrl+K`, `Ctrl+P`, `Ctrl+W`, `Ctrl+E`, `d/r/h/t/m`. Código usa `n/e/x` sem Ctrl, `Ctrl+K`, `q` sem Ctrl. ADR-035 define mapa definitivo que difere de ambos.
- **Ação:** Alinhar código com ADR-035 e atualizar BR-TUI-004. Remover `d/r/h/t/m` e `Ctrl+K` do app.py e screen.py. Implementar `Ctrl+1..5`, `Ctrl+Q`, `Shift+Enter`, `Ctrl+X`.
- **Referência:** ADR-035 (Keybindings Standardization)
- **Sprint:** feat/tui-dashboard-timer (primeiro commit)

---

## 3b. Detalhamento de Itens Adicionados (10/03/2026)

### DT-015: AgendaPanel Sem Auto-Refresh

- **Descoberto:** 10/03/2026
- **Impacto:** O marcador de hora atual (▸) calcula `datetime.now()` apenas quando `_build_lines()` executa. Sem `set_interval`, o marcador congela até próxima operação CRUD. Usuário observando o dashboard por 30 minutos vê hora desatualizada.
- **Arquivo:** `src/timeblock/tui/widgets/agenda_panel.py`
- **Ação:** Adicionar `set_interval(60, self._refresh_content)` no `on_mount` do AgendaPanel ou no DashboardScreen.
- **Sprint:** feat/tui-dashboard-timer (First Complete Loop)

### DT-016: load_active_timer Retorna elapsed_seconds (int), TimerPanel Espera elapsed (str)

- **Descoberto:** 10/03/2026
- **Impacto:** `loader.load_active_timer()` retorna `elapsed_seconds: int` e omite `name` e `elapsed` formatado. `TimerPanel._build_active_lines()` lê `info.get("elapsed", "00:00")` e `info.get("name", "")`. Resultado: timer ativo mostra "00:00" com nome vazio.
- **Arquivo:** `src/timeblock/tui/screens/dashboard/loader.py` linhas 120-139
- **Ação:** Converter `elapsed_seconds` para string `MM:SS`, buscar nome do hábito via `HabitInstance.habit.title`.
- **Sprint:** feat/tui-dashboard-timer (First Complete Loop, commit 1)

### DT-017: MetricsPanel Stub — load_metrics Não Existe

- **Descoberto:** 10/03/2026
- **Impacto:** `screen.py` linha 201 passa `{}` para MetricsPanel. Não existe `load_metrics()` no loader. O panel renderiza streak 0, barras 0%, "Sem dados de atividade".
- **Ação:** Criar `load_metrics()` no loader com queries de streak, completude 7d/30d, e heatmap semanal.
- **Sprint:** Sprint 5

### DT-018: load_tasks Omite Tasks Completed/Cancelled

- **Descoberto:** 10/03/2026
- **Impacto:** `load_tasks()` chama `list_pending_tasks` que filtra por `completed_datetime is None`. O TasksPanel tem formatadores para completed/cancelled (strikethrough) mas nunca recebe esses status. O modelo Task não tem campo `status` — a derivação depende de `completed_datetime`.
- **Ação:** Enriquecer loader para incluir tasks recém-concluídas (últimas 24h) com status derivado.
- **Sprint:** Sprint 5

### DT-019: command_bar.py Stub Vazio

- **Descoberto:** 10/03/2026
- **Impacto:** Arquivo de 0 bytes em `src/timeblock/tui/widgets/command_bar.py`. Nenhum mecanismo de barra de comandos (`/task`, `/habit`, etc.) implementado.
- **Ação:** Implementar command bar com prefixo `/` ou atalho `Ctrl+P`. Feature planejada para sprint futura.
- **Sprint:** Sprint 6+

### DT-020: Régua Fixa 06:00-22:00, Sem Auto-Scroll (BR-TUI-003-R15)

- **Descoberto:** 10/03/2026
- **Impacto:** `AgendaPanel._build_lines()` itera `range(12, 45)` — régua gera slots de 06:00 a 22:00 mas a viewport do TCSS corta a visualização. Docstring menciona "auto-scroll na hora atual" (BR-TUI-003-R15) mas não está implementado. Hábitos antes das 06:00 ou após 22:00 são invisíveis.
- **Ação:** Implementar viewport adaptativa que centraliza na hora atual ao carregar.
- **Sprint:** Sprint 5

### DT-021: Loaders/CRUDs Acessam ORM Objects Fora da Sessão (RESOLVIDO)

- **Descoberto:** 11/03/2026 (Auditoria pós-fix DetachedInstanceError)
- **Resolvido:** 11/03/2026
- **Impacto:** `load_active_routine` e `load_tasks` retornavam ORM objects do callback `service_action` e acessavam atributos fora da sessão. `crud_habits.open_create_habit` acessava `result.id` (escalar de Habit desanexado) fora da sessão. Com `expire_on_commit=False`, escalares sobrevivem — sem bug hoje. Porém, qualquer acesso futuro a relationships (ex: `result.habits`, `task.tag`) quebraria silenciosamente (DetachedInstanceError engolido por `except Exception`).
- **Arquivos:** `loader.py` (load_active_routine, load_tasks), `crud_habits.py` (on_submit)
- **Resolução:** Alinhamento ao padrão `_load(s: Session) -> dict/tuple` já usado em `load_instances` e `load_active_timer`. Toda extração de dados acontece dentro do callback; apenas tipos primitivos (dict, tuple, int) saem da sessão.
- **Commits:** `c546b42`, `195bf0e`

### DT-022: Logging Estruturado — Adoção Zero Fora de habit_instance_service (RESOLVIDO)

- **Descoberto:** 11/03/2026 (Auditoria de observabilidade)
- **Impacto:** Infraestrutura de logging existe (`utils/logger.py` com `setup_logger`, `get_logger`, `RotatingFileHandler`, níveis, toggle para testes), mas apenas `habit_instance_service.py` usa (20 chamadas). Os demais 8 services, toda a camada TUI e todos os commands têm zero instrumentação. Erros em `timer_service`, `routine_service`, `task_service` e no dashboard são invisíveis — `except Exception` engole silenciosamente sem rastro. Bugs como o DetachedInstanceError (DT-021) foram detectados apenas por inspeção manual de código.
- **Escopo da resolução:**
  - Formato dual: texto no console (legibilidade dev), JSON Lines no arquivo (análise programática)
  - Localização dos logs: `~/.local/share/atomvs/logs/atomvs.jsonl` (XDG Base Directory)
  - Dependência: `python-json-logger` (JsonFormatter para stdlib logging)
  - Instrumentar: 8 services (timer, routine, task, tag, habit, event_reordering, backup, habit_instance_service já feito), camada TUI (session.py, loader.py, screen.py), commands
  - Níveis: ERROR (exceções, I/O), WARNING (degradação), INFO (operações de negócio), DEBUG (queries, refresh cycles)
  - Correlation ID por ação do usuário (equivalente local de distributed tracing)
- **Ferramentas de análise:** `jq` (filtros CLI), `lnav` (TUI para logs), `tail -f | jq` (live stream). Possibilidade futura de ferramenta própria de análise integrada ao ecossistema ATOMVS.
- **Resolvido:** 13/03/2026
- **Resolução:** MR !31 (feat/structured-logging). `logger.py` refatorado com formato dual (texto console + JSON Lines arquivo), XDG paths, `python-json-logger>=3.0.0`, `configure_logging()` idempotente. Instrumentação completa: 8 services (info em operações de negócio), camada TUI (session, loader, screen), 8 commands (warning/exception em todos os except). Imagem CI reconstruída com dependência.
- **Commits:** `93b9843` a `b5da37b` (14 commits na branch)
- **Sprint:** feat/structured-logging

---

### DT-023: Instâncias Diárias — Geração Manual Obrigatória (RESOLVIDO)

- **Descoberto:** 11/03/2026
- **Resolvido:** 11/03/2026
- **Impacto:** Sem `ensure_today_instances()`, o usuário precisava executar `atomvs habit atom generate` manualmente todo dia antes de abrir a TUI. Caso contrário, o dashboard mostrava agenda vazia mesmo com hábitos configurados.
- **Arquivos:** `loader.py` (novo `ensure_today_instances`), `screen.py` (chamada em `on_mount` e `_refresh_agenda`)
- **Resolução:** Função idempotente no loader que gera instâncias para hábitos aplicáveis ao dia, filtrada por rotina ativa e recurrence. Chamada no startup e na detecção de virada de dia.
- **Commits:** `661f361`, `fcd670c`

### DT-024: Keybindings Ctrl+N Inoperantes em VTE/GNOME Terminal (RESOLVIDO)

- **Descoberto:** 12/03/2026
- **Resolvido:** 12/03/2026
- **Impacto:** `Ctrl+1..5` para navegação de telas não funcionava em terminais VTE (GNOME Terminal, Tilix, Terminator). O VTE não emite sequências de escape para `Ctrl+digit`, tornando a navegação inacessível nesses terminais.
- **Arquivos:** `app.py`, `help_overlay.py`, 4 arquivos de teste
- **Resolução:** Substituição de `Ctrl+1..5` por números puros `1..5` (padrão lazygit), que funciona universalmente em todos os emuladores de terminal.
- **Commits:** `92da23a`, `1fbe90b`, `b4d2fe1`

---

### DT-025: Pyright como Job CI Complementar

- **Descoberto:** 13/03/2026
- **Impacto:** O projeto usa mypy (`--check-untyped-defs`) como único type checker. Pyright oferece análise complementar — detecta categorias de erros que o mypy ignora (narrowing de unions, reachability, import resolution) e é significativamente mais rápido. A adição como job CI não-bloqueante (`allow_failure: true`) amplia a cobertura de type safety sem risco de quebrar pipelines.
- **Ação:** Adicionar job `pyright` no `.gitlab-ci.yml` com `allow_failure: true`. Configurar `pyrightconfig.json` com `typeCheckingMode: "basic"` inicialmente, evoluir para `"standard"` conforme erros forem resolvidos.
- **Sprint:** Sprint futuro

---

## 4. Política de Gestão

Novos débitos técnicos devem ser registrados aqui com ID sequencial (DT-XXX), severidade e sprint planejado para resolução. O inventário é revisado a cada release.

**Severidades:**

- **CRÍTICA:** Bloqueia desenvolvimento ou deploy
- **ALTA:** Impacta qualidade ou manutenibilidade significativamente
- **MÉDIA:** Degradação gradual, deve ser resolvido no próximo release
- **BAIXA:** Cosmético ou preferencial, resolver quando conveniente
- **ACEITO:** Débito consciente com justificativa documentada

---

## 5. Changelog do Documento

| Data       | Versão | Mudanças                                                |
| ---------- | ------ | ------------------------------------------------------- |
| 2026-03-14 | 2.6.0  | DT-017/018/020 resolvidos. Registra DT-026 a 033        |
|            |        | (bugs TUI encontrados em teste manual)                  |
| 2026-03-13 | 2.5.0  | DT-022 resolvido (feat/structured-logging mergeado).    |
|            |        | Adicionado DT-025 (Pyright CI complementar)             |
| 2026-03-12 | 2.4.0  | Adicionados DT-023 e DT-024 (resolvidos): auto-geração  |
|            |        | de instâncias diárias e keybindings VTE/GNOME           |
| 2026-03-11 | 2.3.0  | Adicionado DT-022 (logging estruturado: escopo,         |
|            |        | formato, ferramentas, plano de instrumentação)          |
| 2026-03-11 | 2.2.0  | Adicionado DT-021 (loaders/CRUDs ORM fora da sessão),   |
|            |        | resolvido na mesma sessão via auditoria preventiva      |
| 2026-03-10 | 2.1.0  | DT-014 resolvido. Adicionados DT-015 a DT-020 (gaps de  |
|            |        | integração: timer, agenda, métricas, command bar)       |
| 2026-03-08 | 2.0.0  | DT-003 resolvido. Adicionados DT-008 a DT-014 (Sprint 4 |
|            |        | Code Review + GitHub CI + keybindings divergentes)      |
| 2026-02-03 | 1.1.0  | Atualiza status: DT-004, DT-005, DT-006 resolvidos      |
| 2026-02-01 | 1.0.0  | Extração do roadmap.md para documento dedicado          |

---

**Próxima Revisão:** Release v1.7.0

**Última atualização:** 14 de Março de 2026
