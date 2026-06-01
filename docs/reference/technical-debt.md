# Technical Debt

**Versão:** 2.37.0

**Status:** SSOT

**Documentos Relacionados:** roadmap.md, quality-metrics.md, sprint-4-code-review.md

---

## 1. Inventário

| ID    | Descrição                                                 | Severidade | Status       | Resolvido em | Sprint planejado            |
| ----- | --------------------------------------------------------- | ---------- | ------------ | ------------ | --------------------------- |
| DT001 | 156 erros mypy                                            | CRÍTICA    | RESOLVIDO    | 2026-01      | v1.4.0 S1-S3                |
| DT002 | 15 testes skipped                                         | ALTA       | RESOLVIDO    | 2026-01      | v1.4.0 S4                   |
| DT003 | Cobertura abaixo de 80%                                   | ALTA       | RESOLVIDO    | 2026-03      | v1.6.0                      |
| DT004 | EventReordering parcial (61%)                             | MÉDIA      | RESOLVIDO    | 2026-02      | -                           |
| DT005 | Código morto                                              | BAIXA      | RESOLVIDO    | 2026-02      | -                           |
| DT006 | Idioma misto EN/PT em CLI                                 | MÉDIA      | RESOLVIDO    | 2026-02      | v1.5.0                      |
| DT007 | migration_001 sem cobertura                               | BAIXA      | ACEITO       | -            | -                           |
| DT008 | GitHub Actions --fail-under divergente                    | MÉDIA      | RESOLVIDO    | 2026-03      | v1.7.0                      |
| DT009 | FocusablePanel: C_HIGHLIGHT na base                       | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT010 | FocusablePanel: flag \_showing_placehold.                 | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT011 | FocusablePanel: count em dois lugares                     | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT012 | DI inconsistente entre services                           | MÉDIA      | PENDENTE     | -            | v2.0                        |
| DT013 | \_parse_time duplicado (crud_habits/tasks)                | BAIXA      | RESOLVIDO    | 2026-03      | fix/quick-dts               |
| DT014 | Keybindings divergentes BR vs código                      | ALTA       | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT015 | AgendaPanel sem auto-refresh (set_interval)               | MÉDIA      | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT016 | load_active_timer: elapsed int vs str MM:SS               | ALTA       | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT017 | MetricsPanel stub — load_metrics não existe               | MÉDIA      | RESOLVIDO    | 2026-03      | feat/metrics-panel          |
| DT018 | load_tasks omite completed/cancelled                      | BAIXA      | RESOLVIDO    | 2026-03      | feat/task-lifecycle         |
| DT019 | command_bar.py stub vazio (0 bytes)                       | BAIXA      | PENDENTE     | -            | Sprint 6+                   |
| DT020 | Agenda: viewport cortada, sem auto-scroll                 | BAIXA      | RESOLVIDO    | 2026-03      | feat/agenda-viewport        |
| DT021 | Loaders/CRUDs: ORM fora da sessão (frágil)                | MÉDIA      | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT022 | Logging: adoção zero fora de habit_inst_svc               | MÉDIA      | RESOLVIDO    | 2026-03      | feat/structured-logging     |
| DT023 | Instâncias diárias: geração manual obrigatória            | ALTA       | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT024 | Keybindings Ctrl+N inoperantes em VTE/GNOME               | ALTA       | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT025 | Pyright como job CI complementar                          | BAIXA      | PENDENTE     | -            | v2.0                        |
| DT026 | load_metrics sem filtro de rotina ativa                   | MÉDIA      | RESOLVIDO    | 2026-03      | feat/metrics-panel          |
| DT027 | FormModal sem suporte a campo select                      | ALTA       | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT028 | Enter sem ação em habit selecionado (ADR-037)             | MÉDIA      | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT029 | Conflitos de horário detectados no CRUD habits            | ALTA       | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT030 | Help overlay incompleto (ADR-037)                         | MÉDIA      | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT031 | Auto-scroll call_later travava TUI                        | ALTA       | RESOLVIDO    | 2026-03      | feat/tui-dashboard-timer    |
| DT032 | Migração de banco manual para Task lifecycle              | MÉDIA      | RESOLVIDO    | 2026-03      | feat/task-lifecycle         |
| DT033 | 3 testes CRUD routines quebrados por VerticalScroll       | MÉDIA      | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT034 | mark_completed sem done_substatus                         | CRITICA    | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT035 | Undo handler nao limpa skip_reason/skip_note              | CRITICA    | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT036 | TimerStopAndDoneRequest sem handler                       | ALTA       | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT037 | v (done) deveria abrir modal de substatus                 | ALTA       | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT038 | s (postpone) deveria abrir FormModal de edit              | MEDIA      | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT039 | s (skip) deveria abrir modal de SkipReason                | MEDIA      | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT040 | n sem rotina: silent no-op ao inves de modal              | MEDIA      | RESOLVIDO    | 2026-03      | fix/dashboard-quality       |
| DT041 | BR-TUI-004/017/018/021 keybindings obsoletos              | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT042 | BR-HABITINSTANCE-001 nao documenta undo                   | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT043 | DEFAULT_CSS inline no FormModal                           | BAIXA      | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT044 | basedpyright strict: ~647 warnings (bulk libs)            | MEDIA      | PENDENTE     | -            | v2.0                        |
| DT045 | Blocos sobrepostos sem distinção na Agenda                | ALTA       | RESOLVIDO    | 2026-03      | feat/agenda-blocks          |
| DT046 | Troca de rotina não atualiza Habits/Tasks                 | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT047 | Sem mecanismo de seleção entre rotinas                    | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT048 | Deleção de rotina não carrega outra nem limpa             | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT049 | Habit criado sem vínculo com rotina ativa                 | CRITICA    | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT050 | FormModal de habit sem Select de recorrência              | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT051 | Edit habit não atualiza render frontend                   | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT052 | Skip habit não atualiza render frontend                   | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT053 | Timer start não muda visual do bloco/habit                | ALTA       | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT054 | Timer pause não para contagem (só muda status)            | CRITICA    | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT055 | v em hábito running não abre ConfirmDialog                | CRITICA    | RESOLVIDO    | 2026-03      | fix/loader-critical         |
| DT056 | TUI conecta a banco sem tabelas — falha silenciosa        | CRITICA    | RESOLVIDO    | 2026-03      | fix/dt056-xdg               |
| DT057 | Delete de rotina falha silenciosamente na TUI             | ALTA       | RESOLVIDO    | 2026-03      | fix/quick-dts               |
| DT058 | Logging ausente na CLI — apenas TUI loga                  | MEDIA      | RESOLVIDO    | 2026-04      | MR !73                      |
| DT059 | Mensagens de migração visíveis no stdout da TUI           | MEDIA      | RESOLVIDO    | 2026-04      | fix/cherry-pick-code-review |
| DT060 | Sidebar ocupa ~15 cols desnecessariamente                 | MEDIA      | PENDENTE     | -            | Sprint futuro               |
| DT061 | AgendaPanel sem scroll horizontal                         | ALTA       | RESOLVIDO    | 2026-03      | feat/agenda-blocks          |
| DT062 | Linhas horizontais cortam blocos de tempo                 | ALTA       | RESOLVIDO    | 2026-03      | feat/agenda-blocks          |
| DT063 | Agenda limitada ao dia atual (sem paginação)              | MEDIA      | PENDENTE     | -            | Sprint futuro               |
| DT064 | CVE-2026-4539 pygments sem fix disponível                 | BAIXA      | RESOLVIDO    | Sprint 6     | Pygments 2.20.0             |
| DT065 | Responsividade em terminal 80x24                          | MEDIA      | PENDENTE     | -            | v1.7.1                      |
| DT066 | Placeholders truncados nos panels                         | BAIXA      | RESOLVIDO    | 2026-04      | MR !64                      |
| DT067 | README sem links para diagramas (~16 desatualizados)      | MEDIA      | RESOLVIDO    | 2026-04      | MR !72                      |
| DT068 | Habits não ordenados por scheduled_start                  | MEDIA      | RESOLVIDO    | 2026-03      | fix/habit-sort-dt068        |
| DT069 | Tela de configurações não documentada/planejada           | BAIXA      | PENDENTE     | -            | Sprint futuro               |
| DT070 | 47 ADRs padronizados (headers, títulos, datas)            | BAIXA      | RESOLVIDO    | 2026-04      | chore/v1.7.1-snapshot       |
| DT071 | Sem padrão de header/footer em documentação               | BAIXA      | PENDENTE     | -            | Sprint futuro               |
| DT072 | Job sync:github substituído por GitLab Push Mirroring     | BAIXA      | RESOLVIDO    | 2026-04      | chore/replace-sync-job      |
| DT073 | `__pycache__` com paths absolutos impede portabilidade    | BAIXA      | PENDENTE     | -            | v1.7.1                      |
| DT074 | BRs e Humble Objects com testes intencionados ausentes    | ALTA       | RESOLVIDO    | 2026-04      | v1.7.2 (MR caracterização)  |
| DT075 | BR fantasma BR-EVENT-002 vs nomenclatura BR-REORDER-XXX   | BAIXA      | RESOLVIDO    | 2026-05      | v1.7.5 (issue #42 vizinha)  |
| DT076 | TimerScreen é placeholder com cinco TODOs ao TimerService | MEDIA      | PENDENTE     | -            | v1.8.0                      |
| DT077 | Drift histórico **version** 0.1.0 vs pyproject.toml       | BAIXA      | RESOLVIDO    | 2026-05      | v1.7.3                      |
| DT078 | Testes de integração sem guarda global de banco isolado   | BAIXA      | RESOLVIDO    | 2026-05      | v1.7.5                      |

## 1b. Quick Status

- [x] DT001 — 156 erros mypy
- [x] DT002 — 15 testes skipped
- [x] DT003 — Cobertura abaixo de 80%
- [x] DT004 — EventReordering parcial
- [x] DT005 — Código morto
- [x] DT006 — Idioma misto EN/PT
- [x] DT007 — migration_001 sem cobertura (ACEITO)
- [x] DT008 — GitHub Actions divergente
- [x] DT009 — FocusablePanel: C_HIGHLIGHT na base
- [x] DT010 — FocusablePanel: flag \_showing_placeholders
- [x] DT011 — FocusablePanel: count em dois lugares
- [ ] DT012 — DI inconsistente entre services
- [x] DT013 — \_parse_time consolidado em validators
- [x] DT014 — Keybindings divergentes
- [x] DT015 — AgendaPanel sem auto-refresh
- [x] DT016 — load_active_timer elapsed/name
- [x] DT017 — MetricsPanel stub
- [x] DT018 — load_tasks omite completed/cancelled
- [→] DT019 — command_bar.py vazio (→ roadmap v1.8.0)
- [x] DT020 — Agenda viewport cortada
- [x] DT021 — Loaders/CRUDs: ORM fora da sessão
- [x] DT022 — Logging: adoção zero fora de habit_instance_service
- [x] DT023 — Instâncias diárias: geração manual obrigatória
- [x] DT024 — Keybindings Ctrl+Números inoperantes em VTE/GNOME
- [ ] DT025 — Pyright como job CI complementar ao mypy e ruff
- [x] DT026 — load_metrics sem filtro de rotina ativa
- [x] DT027 — FormModal sem suporte a campo select (recorrencia)
- [x] DT028 — Enter sem ação em habit selecionado (ADR-037)
- [x] DT029 — Conflitos de horario detectados no CRUD habits
- [x] DT030 — Help overlay completo (ADR-037)
- [x] DT031 — Auto-scroll desabilitado (call_later travava TUI)
- [x] DT032 — Migração de banco manual para Task lifecycle
- [x] DT033 — 3 testes CRUD routines quebrados por VerticalScroll
- [x] DT034 — mark_completed sem done_substatus (CRITICA)
- [x] DT035 — Undo handler nao limpa skip_reason/skip_note (CRITICA)
- [x] DT036 — TimerStopAndDoneRequest sem handler
- [x] DT037 — v (done) deveria abrir modal de substatus
- [x] DT038 — s (postpone) deveria abrir FormModal de edit
- [x] DT039 — s (skip) deveria abrir modal de SkipReason
- [x] DT040 — n sem rotina: silent no-op ao inves de modal
- [x] DT041 — BR-TUI-004/017/018/021 keybindings obsoletos
- [x] DT042 — BR-HABITINSTANCE-001 não documenta undo
- [x] DT043 — DEFAULT_CSS inline no FormModal
- [ ] DT044 — basedpyright standard: ~190 warnings
- [x] DT045 — Blocos sobrepostos sem distinção visual na Agenda
- [x] DT046 — Troca de rotina não atualiza Habits/Tasks
- [x] DT047 — Sem mecanismo de seleção entre rotinas
- [x] DT048 — Deleção de rotina não carrega outra rotina e nem limpa panels
- [x] DT049 — Habit criado sem vínculo com rotina ativa
- [x] DT050 — FormModal de habit sem Select de recorrência
- [x] DT051 — Edit habit não atualiza renderização no frontend
- [x] DT052 — Skip habit não atualiza renderização no frontend
- [x] DT053 — Timer start não muda visual do bloco/habit
- [x] DT054 — Timer pause não para contagem (só muda status e cor)
- [x] DT055 — v em hábito running não abre ConfirmDialog
- [x] DT056 — TUI conecta a banco sem tabelas — falha silenciosa total
- [x] DT057 — Delete de rotina falha silenciosamente na TUI
- [x] DT058 — Logging completo: CLI, TUI, widgets, excepthook global (MR !73)
- [x] DT059 — Mensagens de migração visíveis no stdout da TUI
- [→] DT060 — Sidebar redesign (→ roadmap v1.8.0)
- [x] DT061 — AgendaPanel sem scroll horizontal (bloqueador de multi-coluna)
- [x] DT062 — Linhas horizontais cortam blocos de tempo coloridos
- [→] DT063 — Paginação de dias (→ roadmap v1.8.0)
- [x] DT064 — CVE-2026-4539 pygments sem fix disponível (Pygments 2.20.0)
- [→] DT065 — Layout adaptativo (→ roadmap v1.8.0)
- [x] DT066 — Placeholders truncados nos panels (MR !64)
- [x] DT067 — Diagramas auditados (14) + README atualizado (MR !72)
- [x] DT068 — Habits não ordenados por scheduled_start no dashboard
- [→] DT069 — Settings screen (→ roadmap v1.8.0)
- [x] DT070 — 47 ADRs padronizados (headers, títulos, datas em PT-BR/ISO)
- [ ] DT071 — Sem padrão de header/footer em documentação (datas, versão, status)
- [x] DT072 — Job sync:github substituído por GitLab Push Mirroring nativo
- [ ] DT073 — `__pycache__` com paths absolutos impede portabilidade
- [x] DT074 — BRs e Humble Objects com testes intencionados ausentes
- [x] DT075 — BR fantasma BR-EVENT-002 vs nomenclatura BR-REORDER-XXX
- [ ] DT076 — TimerScreen é placeholder (cinco TODOs ao TimerService)
- [x] DT077 — Drift histórico **version** 0.1.0 vs pyproject.toml
- [x] DT078 — Testes de integração sem guarda global de banco isolado

**Resolvidos:** 63/74 | **Pendentes:** 5/74 | **Em resolução:** 0/74 | **Aceitos:** 1/74 | **Reclassificados:** 5/74

---

## 2. Detalhamento

### DT-001: Erros Mypy (RESOLVIDO)

- **Descoberto:** 2026-01-16
- **Resolvido:** 2026-01
- **Impacto original:** 156 erros em modo strict, commands não passavam no type checker
- **Resolução:** Instalação de stubs, correção de Session.exec, correção de SQLAlchemy datetime comparisons, completude do Service Layer, null checks em commands
- **Estado final:** 0 erros em 45 arquivos fonte

### DT-002: Testes Skipped (RESOLVIDO)

- **Descoberto:** 2026-01-16
- **Resolvido:** 2026-01
- **Impacto original:** 15 testes marcados como skip (stubs vazios, timer API v1, migrations)
- **Resolução:** Implementação dos stubs, atualização para API v2, remoção de testes obsoletos
- **Estado final:** 0 testes skipped, 618 passando

### DT-003: Cobertura Abaixo de 80% (RESOLVIDO)

- **Descoberto:** 2026-01 (Sprint 1)
- **Resolvido:** 2026-03
- **Cobertura original:** 76%
- **Cobertura atual:** ~81% (threshold 80%)
- **Resolução:** Sprint 3.2 e Sprint 4 adicionaram ~300 testes TUI

### DT-004: EventReordering Parcial (RESOLVIDO)

- **Descoberto:** 2026-01 (Sprint 1)
- **Resolvido:** 2026-02
- **Cobertura original:** 61%
- **Cobertura atual:** 86%
- **Resolução:** Testes de integração cobrindo cenários de reorganização

### DT-005: Código Morto (RESOLVIDO)

- **Descoberto:** 2026-01 (Sprint 1)
- **Resolvido:** 2026-02
- **Verificação:** `ruff check src/timeblock --select F401,F841` retorna 0 issues
- **Resolução:** Limpeza gradual durante refatorações

### DT-006: Idioma Misto EN/PT (RESOLVIDO)

- **Descoberto:** 2026-01 (Sprint 1)
- **Resolvido:** 2026-02
- **Referência:** ADR-018 (Language Standards)
- **Resolução:** Tradução de mensagens CLI para PT-BR, criação de script lint-i18n.py
- **Verificação:** `python scripts/lint-i18n.py` retorna 0 inconsistências

### DT-007: migration_001 Sem Cobertura (ACEITO)

- **Cobertura:** 0%
- **Justificativa:** Migração one-shot já executada em produção. Custo de testar supera benefício. Será removida quando migração definitiva for criada (v2.0.0).
- **Decisão:** Aceitar o débito. Não investir esforço em cobertura.

### DT-008: GitHub Actions --fail-under Divergente

- **Descoberto:** 2026-03-08
- **Impacto:** Job `CI / test (push)` falha no GitHub com `--fail-under=85` enquanto GitLab usa 80%. GitHub Actions também usa Python 3.13 enquanto projeto roda em 3.14.
- **Arquivo:** `.github/workflows/ci.yml`
- **Ação:** Alinhar `--fail-under=80` e `python-version: "3.14"` com GitLab CI.
- **Sprint:** feat/tui-dashboard-timer ou próximo commit de CI.
- **Resolvido em:** 2026-03 (v1.7.0)

### DT-009: C_HIGHLIGHT Acoplado na Classe Base FocusablePanel (CRITICAL-001)

- **Descoberto:** 2026-03-08 (Sprint 4 Code Review)
- **Impacto:** FocusablePanel importa `C_HIGHLIGHT` de `colors.py` e aplica highlight em `_build_empty_state`. Classe base conhece e decide cor de cursor — responsabilidade de apresentação que pertence às subclasses ou ao TCSS.
- **Arquivo:** `src/timeblock/tui/widgets/focusable_panel.py` linha 11
- **Ação:** Extrair highlight para método `_apply_cursor_highlight` sobrescrevível, ou usar classes CSS do Textual.
- **Referência:** sprint-4-code-review.md CRITICAL-001
- **Sprint:** v1.7.0 (pré-release)
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-010: \_showing_placeholders Como Flag Booleano Solto (CRITICAL-002)

- **Descoberto:** 2026-03-08 (Sprint 4 Code Review)
- **Impacto:** Booleano gerenciado manualmente em `update_data()` de cada subclasse. Estado duplicado — pode ser derivado da ausência de dados reais. Bug silencioso se subclasse esquecer de setar o flag.
- **Arquivos:** `focusable_panel.py` linha 30, `habits_panel.py` linhas 35-39, `tasks_panel.py` linhas 38-42
- **Ação:** Transformar em propriedade derivada ou encapsular em método `_set_placeholder_mode(count)`.
- **Referência:** sprint-4-code-review.md CRITICAL-002
- **Sprint:** v1.7.0 (pré-release)
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-011: Count Definido em Dois Lugares Divergentes (CRITICAL-003)

- **Descoberto:** 2026-03-08 (Sprint 4 Code Review)
- **Impacto:** `update_data` define `_set_item_count(N)` e `_build_empty_state(..., count=N)` recebe N separadamente. Se divergirem, cursor aceita posições invisíveis. Já aconteceu durante a Sprint 4.
- **Arquivos:** `tasks_panel.py` linhas 41 e 100
- **Ação:** Unificar em método único `_enter_placeholder_mode(placeholder, hint, count)` que seta count e retorna linhas.
- **Referência:** sprint-4-code-review.md CRITICAL-003
- **Sprint:** v1.7.0 (pré-release)
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-012: DI Inconsistente Entre Services

- **Descoberto:** 2026-03-08 (Sprint 4 Code Review)
- **Impacto:** Três padrões de DI coexistem: `RoutineService(s)` (constructor), `HabitInstanceService().method(session=s)` (parameter + instance), `TaskService.method(session=s)` (static + parameter). Confuso para contribuidores.
- **Arquivo:** `src/timeblock/tui/screens/dashboard/loader.py`
- **Ação:** Unificar na v2.0 com Application Layer e Repository Pattern.
- **Referência:** sprint-4-code-review.md WARNING-001
- **Sprint:** v2.0

### DT-013: \_parse_time Duplicado em Dois Módulos

- **Descoberto:** 2026-03-08 (Sprint 4 Code Review)
- **Impacto:** Mesma função `_parse_time(value: str) -> time` em `crud_habits.py` e `crud_tasks.py`. Bug fix em um não propaga para o outro.
- **Ação:** Mover para `src/timeblock/tui/utils.py` ou reutilizar `validators.py`.
- **Referência:** sprint-4-code-review.md WARNING-006
- **Sprint:** v1.7.0
- **Resolvido em:** 2026-03 (fix/quick-dts)

### DT-014: Keybindings Divergentes Entre BR-TUI-004 e Código

- **Descoberto:** 2026-03-08
- **Impacto:** BR-TUI-004 especifica `Ctrl+K`, `Ctrl+P`, `Ctrl+W`, `Ctrl+E`, `d/r/h/t/m`. Código usa `n/e/x` sem Ctrl, `Ctrl+K`, `q` sem Ctrl. ADR-035 define mapa definitivo que difere de ambos.
- **Ação:** Alinhar código com ADR-035 e atualizar BR-TUI-004. Remover `d/r/h/t/m` e `Ctrl+K` do app.py e screen.py. Implementar `Ctrl+1..5`, `Ctrl+Q`, `Shift+Enter`, `Ctrl+X`.
- **Referência:** ADR-035 (Keybindings Standardization)
- **Sprint:** feat/tui-dashboard-timer (primeiro commit)
- **Resolvido em:** 2026-03-15 (feat/tui-dashboard-timer)

### DT-015: AgendaPanel Sem Auto-Refresh

- **Descoberto:** 2026-03-10
- **Impacto:** O marcador de hora atual (▸) calcula `datetime.now()` apenas quando `_build_lines()` executa. Sem `set_interval`, o marcador congela até próxima operação CRUD. Usuário observando o dashboard por 30 minutos vê hora desatualizada.
- **Arquivo:** `src/timeblock/tui/widgets/agenda_panel.py`
- **Ação:** Adicionar `set_interval(60, self._refresh_content)` no `on_mount` do AgendaPanel ou no DashboardScreen.
- **Sprint:** feat/tui-dashboard-timer (First Complete Loop)
- **Resolvido em:** 2026-03-15 (feat/tui-dashboard-timer)

### DT-016: load_active_timer Retorna elapsed_seconds (int), TimerPanel Espera elapsed (str)

- **Descoberto:** 2026-03-10
- **Impacto:** `loader.load_active_timer()` retorna `elapsed_seconds: int` e omite `name` e `elapsed` formatado. `TimerPanel._build_active_lines()` lê `info.get("elapsed", "00:00")` e `info.get("name", "")`. Resultado: timer ativo mostra "00:00" com nome vazio.
- **Arquivo:** `src/timeblock/tui/screens/dashboard/loader.py` linhas 120-139
- **Ação:** Converter `elapsed_seconds` para string `MM:SS`, buscar nome do hábito via `HabitInstance.habit.title`.
- **Sprint:** feat/tui-dashboard-timer (First Complete Loop, commit 1)
- **Resolvido em:** 2026-03-15 (feat/tui-dashboard-timer)

### DT-017: MetricsPanel Stub — load_metrics Não Existe

- **Descoberto:** 2026-03-10
- **Impacto:** `screen.py` linha 201 passa `{}` para MetricsPanel. Não existe `load_metrics()` no loader. O panel renderiza streak 0, barras 0%, "Sem dados de atividade".
- **Ação:** Criar `load_metrics()` no loader com queries de streak, completude 7d/30d, e heatmap semanal.
- **Sprint:** Sprint 5
- **Resolvido em:** 2026-03-19 (feat/metrics-panel)

### DT-018: load_tasks Omite Tasks Completed/Cancelled

- **Descoberto:** 2026-03-10
- **Impacto:** `load_tasks()` chama `list_pending_tasks` que filtra por `completed_datetime is None`. O TasksPanel tem formatadores para completed/cancelled (strikethrough) mas nunca recebe esses status. O modelo Task não tem campo `status` — a derivação depende de `completed_datetime`.
- **Ação:** Enriquecer loader para incluir tasks recém-concluídas (últimas 24h) com status derivado.
- **Sprint:** Sprint 5
- **Resolvido em:** 2026-03-14 (feat/task-lifecycle)

### DT-019: Command Bar (RECLASSIFICADO → Feature)

- **Status:** Movido para roadmap v1.8.0
- **Ver:** `docs/reference/roadmap.md` seção v1.8.0

### DT-020: Régua Fixa 06:00-22:00, Sem Auto-Scroll (BR-TUI-003-R15)

- **Descoberto:** 2026-03-10
- **Impacto:** `AgendaPanel._build_lines()` itera `range(12, 45)` — régua gera slots de 06:00 a 22:00 mas a viewport do TCSS corta a visualização. Docstring menciona "auto-scroll na hora atual" (BR-TUI-003-R15) mas não está implementado. Hábitos antes das 06:00 ou após 22:00 são invisíveis.
- **Ação:** Implementar viewport adaptativa que centraliza na hora atual ao carregar.
- **Sprint:** Sprint 5
- **Resolvido em:** 2026-03 (feat/agenda-viewport)

### DT-021: Loaders/CRUDs Acessam ORM Objects Fora da Sessão (RESOLVIDO)

- **Descoberto:** 2026-03-11 (Auditoria pós-fix DetachedInstanceError)
- **Resolvido:** 2026-03-11
- **Impacto:** `load_active_routine` e `load_tasks` retornavam ORM objects do callback `service_action` e acessavam atributos fora da sessão. `crud_habits.open_create_habit` acessava `result.id` (escalar de Habit desanexado) fora da sessão. Com `expire_on_commit=False`, escalares sobrevivem — sem bug hoje. Porém, qualquer acesso futuro a relationships (ex: `result.habits`, `task.tag`) quebraria silenciosamente (DetachedInstanceError engolido por `except Exception`).
- **Arquivos:** `loader.py` (load_active_routine, load_tasks), `crud_habits.py` (on_submit)
- **Resolução:** Alinhamento ao padrão `_load(s: Session) -> dict/tuple` já usado em `load_instances` e `load_active_timer`. Toda extração de dados acontece dentro do callback; apenas tipos primitivos (dict, tuple, int) saem da sessão.
- **Commits:** `c546b42`, `195bf0e`

### DT-022: Logging Estruturado — Adoção Zero Fora de habit_instance_service (RESOLVIDO)

- **Descoberto:** 2026-03-11 (Auditoria de observabilidade)
- **Impacto:** Infraestrutura de logging existe (`utils/logger.py` com `setup_logger`, `get_logger`, `RotatingFileHandler`, níveis, toggle para testes), mas apenas `habit_instance_service.py` usa (20 chamadas). Os demais 8 services, toda a camada TUI e todos os commands têm zero instrumentação. Erros em `timer_service`, `routine_service`, `task_service` e no dashboard são invisíveis — `except Exception` engole silenciosamente sem rastro. Bugs como o DetachedInstanceError (DT-021) foram detectados apenas por inspeção manual de código.
- **Escopo da resolução:**
  - Formato dual: texto no console (legibilidade dev), JSON Lines no arquivo (análise programática)
  - Localização dos logs: `~/.local/share/atomvs/logs/atomvs.jsonl` (XDG Base Directory)
  - Dependência: `python-json-logger` (JsonFormatter para stdlib logging)
  - Instrumentar: 8 services (timer, routine, task, tag, habit, event_reordering, backup, habit_instance_service já feito), camada TUI (session.py, loader.py, screen.py), commands
  - Níveis: ERROR (exceções, I/O), WARNING (degradação), INFO (operações de negócio), DEBUG (queries, refresh cycles)
  - Correlation ID por ação do usuário (equivalente local de distributed tracing)
- **Ferramentas de análise:** `jq` (filtros CLI), `lnav` (TUI para logs), `tail -f | jq` (live stream). Possibilidade futura de ferramenta própria de análise integrada ao ecossistema ATOMVS.
- **Resolvido:** 2026-03-13
- **Resolução:** MR !31 (feat/structured-logging). `logger.py` refatorado com formato dual (texto console + JSON Lines arquivo), XDG paths, `python-json-logger>=3.0.0`, `configure_logging()` idempotente. Instrumentação completa: 8 services (info em operações de negócio), camada TUI (session, loader, screen), 8 commands (warning/exception em todos os except). Imagem CI reconstruída com dependência.
- **Commits:** `93b9843` a `b5da37b` (14 commits na branch)
- **Sprint:** feat/structured-logging

### DT-023: Instâncias Diárias — Geração Manual Obrigatória (RESOLVIDO)

- **Descoberto:** 2026-03-11
- **Resolvido:** 2026-03-11
- **Impacto:** Sem `ensure_today_instances()`, o usuário precisava executar `atomvs habit atom generate` manualmente todo dia antes de abrir a TUI. Caso contrário, o dashboard mostrava agenda vazia mesmo com hábitos configurados.
- **Arquivos:** `loader.py` (novo `ensure_today_instances`), `screen.py` (chamada em `on_mount` e `_refresh_agenda`)
- **Resolução:** Função idempotente no loader que gera instâncias para hábitos aplicáveis ao dia, filtrada por rotina ativa e recurrence. Chamada no startup e na detecção de virada de dia.
- **Commits:** `661f361`, `fcd670c`

### DT-024: Keybindings Ctrl+N Inoperantes em VTE/GNOME Terminal (RESOLVIDO)

- **Descoberto:** 2026-03-12
- **Resolvido:** 2026-03-12
- **Impacto:** `Ctrl+1..5` para navegação de telas não funcionava em terminais VTE (GNOME Terminal, Tilix, Terminator). O VTE não emite sequências de escape para `Ctrl+digit`, tornando a navegação inacessível nesses terminais.
- **Arquivos:** `app.py`, `help_overlay.py`, 4 arquivos de teste
- **Resolução:** Substituição de `Ctrl+1..5` por números puros `1..5` (padrão lazygit), que funciona universalmente em todos os emuladores de terminal.
- **Commits:** `92da23a`, `1fbe90b`, `b4d2fe1`

### DT-025: Pyright como Job CI Complementar

- **Descoberto:** 2026-03-13
- **Impacto:** O projeto usa mypy (`--check-untyped-defs`) como único type checker. Pyright oferece análise complementar — detecta categorias de erros que o mypy ignora (narrowing de unions, reachability, import resolution) e é significativamente mais rápido. A adição como job CI não-bloqueante (`allow_failure: true`) amplia a cobertura de type safety sem risco de quebrar pipelines.
- **Ação:** Adicionar job `pyright` no `.gitlab-ci.yml` com `allow_failure: true`. Configurar `pyrightconfig.json` com `typeCheckingMode: "basic"` inicialmente, evoluir para `"standard"` conforme erros forem resolvidos.
- **Sprint:** Sprint futuro

### DT-026: load_metrics sem filtro de rotina ativa (RESOLVIDO)

MetricsPanel recebia métricas globais sem filtrar pela rotina ativa. Dashboard exibia streak e completude de todas as rotinas misturadas.

- **Descoberto:** 2026-03-14 (v2.6.0 — teste manual do MetricsPanel)
- **Severidade:** MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-19 (feat/metrics-panel) — `load_metrics()` filtra por `routine_id` da rotina ativa.

### DT-027: FormModal sem suporte a campo select (RESOLVIDO)

FormModal renderizava apenas campos de texto (`Input`). Sem `Select`, a criação de hábitos não oferecia escolha de recorrência.

- **Descoberto:** 2026-03-14 (v2.6.0 — teste manual de criação de hábitos)
- **Severidade:** ALTA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-15 (feat/tui-dashboard-timer) — `FormField` com `field_type="select"` e `options` renderiza `Select` nativo do Textual.

### DT-028: Enter sem ação em habit selecionado (RESOLVIDO)

Pressionar Enter sobre um hábito no HabitsPanel não fazia nada. ADR-037 define Enter como atalho para abrir detalhes ou editar.

- **Descoberto:** 2026-03-14 (v2.6.0 — revisão de keybindings ADR-037)
- **Severidade:** MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-15 (feat/tui-dashboard-timer) — Enter delegado para `_action_edit` no HabitsPanel.

### DT-029: Conflitos de horário detectados no CRUD habits (RESOLVIDO)

CRUD de hábitos permitia criar dois hábitos com horários sobrepostos na mesma rotina sem aviso.

- **Descoberto:** 2026-03-14 (v2.6.0 — teste manual de sobreposição de blocos)
- **Severidade:** ALTA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-15 (fix/dashboard-quality) — Validação de overlap em `create_habit` e `update_habit` via `detect_conflicts()`.

### DT-030: Help overlay incompleto (RESOLVIDO)

Help overlay listava keybindings antigos (Ctrl+1..5) e omitia ações de hábitos (v, s, u, t).

- **Descoberto:** 2026-03-14 (v2.6.0 — revisão de keybindings ADR-037)
- **Severidade:** MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-15 (fix/dashboard-quality) — Help overlay reescrito conforme ADR-037.

### DT-031: Auto-scroll call_later travava TUI (RESOLVIDO)

`call_later` com `scroll_visible` no `on_mount` causava deadlock intermitente na inicialização da TUI. Agenda não scrollava para a hora atual.

- **Descoberto:** 2026-03-14 (v2.6.0 — teste manual, freeze no startup)
- **Severidade:** ALTA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-15 (feat/tui-dashboard-timer) — Auto-scroll delegado ao `VerticalScroll` pai com `set_timer(0.5)` para aguardar layout completo.

### DT-032: Migração de banco manual para Task lifecycle (RESOLVIDO)

Adição dos campos `completed_datetime`, `cancelled_datetime` e `postponement_count` ao modelo Task exigia migração manual do banco existente.

- **Descoberto:** 2026-03-14 (feat/task-lifecycle)
- **Severidade:** MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-14 (feat/task-lifecycle) — migration_002 criada para `ALTER TABLE task ADD COLUMN` com defaults.

### DT-033: 3 testes CRUD routines quebrados por VerticalScroll (RESOLVIDO)

Testes de CRUD de rotinas falhavam após introdução de `VerticalScroll` como container pai da agenda. Seletores CSS dos testes não encontravam os widgets.

- **Descoberto:** 2026-03-14 (pipeline CI quebrado)
- **Severidade:** MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03-14 (fix/dashboard-quality) — Seletores CSS atualizados para refletir nova hierarquia DOM.

### DT-034: mark_completed sem done_substatus (CRITICA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** `HabitInstanceService.mark_completed()` seta `status=DONE` sem setar `done_substatus`. Viola BR-HABITINSTANCE-002 regra 1.
- **Correção:** Abrir modal de substatus ao pressionar `v` (ADR-038 D3).
- **BRs afetadas:** BR-HABITINSTANCE-002, BR-TUI-004
- **Resolvido:** 2026-03 — Parâmetro `done_substatus` obrigatório em `mark_completed()`. Campos conflitantes limpos, `validate_status_consistency()` chamado antes de persistir.

### DT-035: Undo handler nao limpa skip_reason/skip_note (CRITICA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** Handler undo limpa `done_substatus` e `not_done_substatus` mas nao limpa `skip_reason`, `skip_note`, `completion_percentage`. Viola `validate_status_consistency()`.
- **Correção:** Limpar todos os campos no undo.
- **BRs afetadas:** BR-SKIP-002, BR-HABITINSTANCE-002
- **Resolvido:** 2026-03 — Metodo `reset_to_pending()` centraliza limpeza de todos os campos.

### DT-036: TimerStopAndDoneRequest sem handler (ALTA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** `v` em habito com timer ativo e silenciosamente ignorado.
- **Correção:** Implementar handler com modal de opcoes (ADR-038 D4).
- **BRs afetadas:** BR-TUI-021
- **Resolvido:** 2026-03 — Handler on_habits_panel_timer_stop_and_done_request com ConfirmDialog.

### DT-037: v (done) deveria abrir modal de substatus (ALTA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** `v` marca done sem substatus. Viola BR-HABITINSTANCE-002.
- **Correção:** Abrir modal com Select de DoneSubstatus (ADR-038 D3).
- **BRs afetadas:** BR-HABITINSTANCE-002, BR-HABITINSTANCE-003
- **Resolvido:** 2026-03 — Modal open_done_modal com detecção de TimeLog e restauração de substatus.

### DT-038: s (postpone) deveria abrir FormModal de edit (MEDIA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** Handler chama `update_task` sem parametros. Nenhuma acao visivel.
- **Correção:** `s` abre mesmo FormModal que `e` (ADR-038 D5).
- **BRs afetadas:** BR-TASK-008, BR-TUI-018
- **Resolvido:** 2026-03 — Postpone delega para crud_tasks.open_edit_task via FormModal.

### DT-039: s (skip) deveria abrir modal de SkipReason (MEDIA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** `s` aplica `SkipReason.OTHER` hardcoded. Viola BR-SKIP-001.
- **Correção:** Abrir modal com Select de SkipReason (ADR-038 D6).
- **BRs afetadas:** BR-SKIP-001, BR-SKIP-004
- **Resolvido:** 2026-03 — Modal open_skip_modal com Select de SkipReason e nota opcional.

### DT-040: n sem rotina: silent no-op no habits panel (MEDIA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** `n` com habits focado e sem rotina nao faz nada.
- **Correção:** Redirecionar para criacao de rotina (ADR-038 D9).
- **BRs afetadas:** BR-TUI-017
- **Resolvido:** 2026-03 — Fallback para crud_routines.open_create_routine quando sem rotina ativa.

### DT-041: BR-TUI-004/017/018/021 keybindings obsoletos (ALTA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** BRs documentam Ctrl+Enter, Ctrl+S, Shift+Enter. Codigo usa v, s, space, c (ADR-037).
- **Correção:** Reescrever secoes de keybindings nas 4 BRs.
- **BRs afetadas:** BR-TUI-004, BR-TUI-017, BR-TUI-018, BR-TUI-021
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-042: BR-HABITINSTANCE-001 nao documenta undo (ALTA)

- **Descoberto:** 2026-03-15 (revisão de testes e2e)
- **Impacto:** BR define DONE e NOT_DONE como [FINAL]. Codigo implementa undo.
- **Correção:** Adicionar transicao undo + BR-HABITINSTANCE-007 (ADR-038 D1).
- **BRs afetadas:** BR-HABITINSTANCE-001
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-043: DEFAULT_CSS inline no FormModal (BAIXA)

- **Descoberto:** 2026-03-17 (revisão de codigo)
- **Impacto:** FormModal define ~50 linhas de CSS via DEFAULT_CSS inline. O projeto usa pasta dedicada para TCSS modularizado.
- **Correção:** Mover CSS para arquivo TCSS dedicado e usar CSS_PATH. Alinhar com padrao do projeto.
- **BRs afetadas:** BR-TUI-020
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-044: basedpyright em modo standard gera ~190 warnings (MEDIA)

- **Descoberto:** 2026-03-17 (configuração basedpyright no Zed)
- **Impacto:** App[Unknown], dict[Unknown, Unknown], reportAny, reportUnusedCallResult em screen.py, crud_habits.py, form_modal.py e demais. Modo reduzido para basic temporariamente no pyproject.toml.
- **Correção:** Adicionar type arguments a App, tipar dicts com TypedDict, resolver reportAny com casts explicitos. Restaurar typeCheckingMode = standard apos limpeza.
- **BRs afetadas:** Nenhuma diretamente — qualidade de codigo.

### DT-045: Blocos sobrepostos sem distinção visual na Agenda (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da TUI)
- **Impacto:** Quando dois hábitos têm horários sobrepostos (ex: 08:30-10:30 e 09:00-10:00), os blocos se empilham verticalmente sem distinção visual. O bloco de 2h aparenta ter a duração do espaço até o próximo bloco (30min), enquanto o bloco de 1h herda visualmente o espaço restante (parecendo 2h). Confusão grave sobre duração real de cada hábito.
- **Correção:** Implementar renderização lado a lado para blocos com sobreposição temporal, similar a calendários como Google Calendar e Outlook. Alternativas para TUI: (1) colunas divididas com Rich layout, (2) indicador visual de conflito (cor, borda), (3) tooltip ou annotation com horário real. Pesquisar referências de TUI calendar rendering.
- **BRs afetadas:** BR-TUI-003 (Dashboard layout), BR-EVENT-001 (detecção de conflitos)
- **Resolvido em:** 2026-03 (feat/agenda-blocks)

### DT-046: Troca de rotina não atualiza Habits e Tasks (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao criar uma segunda rotina, os panels Habits e Tasks continuam exibindo dados da rotina anterior. O refresh_data usa \_active_routine_id que não é atualizado ao trocar de contexto.
- **Correção:** Implementar callback de troca de rotina que atualiza \_active_routine_id e chama refresh_data. Garantir que load_instances e load_tasks filtrem por routine_id.
- **BRs afetadas:** BR-TUI-003, BR-TUI-016
- **Testes necessarios:** e2e com duas rotinas — criar rotina A com hábitos, criar rotina B, verificar que panels atualizam.
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-047: Sem mecanismo de seleção entre rotinas no dashboard (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Não existe keybinding nem UI para alternar entre rotinas criadas. O usuário pode criar e editar a rotina ativa, mas não pode selecionar outra. Funcionalidade essencial para uso com múltiplas rotinas (manhã, tarde, noite).
- **Correção:** Implementar seletor de rotina — opções: (1) FormModal com Select listando rotinas, (2) keybinding dedicado (ex: r para cycle, ou Select no AgendaPanel), (3) integração com a tela Routines (screen 2).
- **BRs afetadas:** BR-TUI-003, BR-TUI-016
- **Testes necessarios:** e2e com troca de rotina e verificação de atualização dos panels.
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-048: Deleção de rotina não carrega outra e não limpa panels (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao deletar a rotina ativa, o título some do header mas \_active_routine_id não é atualizado para None ou para outra rotina existente. Habits e Tasks continuam exibindo dados da rotina deletada. Estado inconsistente.
- **Correção:** Após deleção, verificar se existe outra rotina e carregar. Se não existir, setar \_active_routine_id = None e limpar panels (mostrar placeholders). refresh_data já trata None via loader, basta garantir que o callback de deleção atualiza o estado.
- **BRs afetadas:** BR-TUI-003, BR-TUI-016
- **Testes necessarios:** e2e com deleção de rotina e verificação de estado limpo nos panels.
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-049: Habit criado sem vínculo com rotina ativa (CRITICA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao criar um hábito via FormModal, o hábito não é vinculado à rotina ativa. Aparece no panel mas sem associação — gera instâncias órfãs ou não gera instâncias. Funcionalidade core quebrada.
- **Correção:** Verificar se open_create_habit recebe e propaga \_active_routine_id corretamente. Investigar HabitService.create_habit e generate_instances.
- **BRs afetadas:** BR-TUI-017, BR-HABIT-001
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-050: FormModal de criação de habit sem Select de recorrência (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** O FormModal de criação de hábito deveria ter 4 campos (título, horário, duração, recorrência) mas o Select de recorrência não renderiza. Todos os hábitos ficam com recorrência default (EVERYDAY) sem opção de alterar.
- **Correção:** Verificar se o campo FormField de recorrência com field_type="select" está no compose de open_create_habit. O campo existe em open_edit_habit — pode ter sido omitido na criação.
- **BRs afetadas:** BR-TUI-017, BR-TUI-020
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-051: Edit habit não atualiza renderização no frontend (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao editar título do hábito via FormModal, a alteração persiste no banco de dados mas o panel não re-renderiza com o novo nome. Provável falha no callback \_on_crud_done ou no refresh_data não propagando para o HabitsPanel.
- **Correção:** Investigar se \_on_crud_done chama refresh_data, e se refresh_data reconstrói os dicts via loader.load_instances. Pode ser cache ou falta de \_refresh_content no panel.
- **BRs afetadas:** BR-TUI-017
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-052: Skip habit não atualiza renderização no frontend (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao marcar skip via modal, o status pode persistir no banco mas o HabitsPanel não atualiza visualmente. Mesmo problema de refresh que DT-051 — provável causa raiz compartilhada.
- **Correção:** Mesma investigação de DT-051. Se a causa raiz for refresh_data, um único fix resolve DT-051 e DT-052.
- **BRs afetadas:** BR-TUI-024, BR-SKIP-001
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-053: Timer start não muda visual do bloco na Agenda nem cor no HabitsPanel (ALTA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao iniciar timer com t, o TimerPanel atualiza (cronômetro rodando, nome do hábito) mas o bloco na Agenda e o item no HabitsPanel não mudam para estado "running" (sem mudança de cor ou indicador). Usuário não sabe visualmente qual hábito está sendo cronometrado nos outros panels.
- **Correção:** Verificar se refresh_data é chamado após timer start e se HabitsPanel.\_refresh_content renderiza status "running" com cor distinta. Agenda pode precisar de lógica adicional para status running.
- **BRs afetadas:** BR-TUI-003, BR-TUI-021
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-054: Timer pause não para a contagem (CRITICA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao pressionar space para pausar, o status e a cor mudam para "paused" no TimerPanel mas o cronômetro continua incrementando. O tempo registrado será incorreto — viola a contabilidade de tempo que é o core do produto.
- **Correção:** Investigar TimerService.pause_timer — se atualiza pause_start e status no banco. Verificar se o TimerPanel usa set_interval/set_timer para atualizar o display e se a lógica de elapsed respeita paused_duration. Pode ser bug no cálculo de elapsed no loader ou no display do panel.
- **BRs afetadas:** BR-TIMER-002, BR-TIMER-003
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-055: v em hábito running não abre ConfirmDialog (CRITICA)

- **Descoberto:** 2026-03-18 (teste manual da dashboard)
- **Impacto:** Ao pressionar v em hábito com timer ativo (status running), nada acontece. O DT-036 foi marcado como resolvido mas o handler pode não estar sendo acionado. O teste e2e test_timer_stop_marks_habit_done passa — investigar diferença entre teste e uso real.
- **Correção:** Verificar se HabitsPanel.\_action_done detecta status "running" no dict do item (item.get("status") == "running"). Pode ser que o loader retorne "running" diferente do que o panel espera. Verificar se o get_selected_item retorna o item atualizado após timer start.
- **BRs afetadas:** BR-TUI-021, BR-TUI-023
- **Resolvido em:** 2026-03 (fix/loader-critical)

### DT-056: TUI conecta a banco sem tabelas — falha silenciosa total (CRITICA)

- **Descoberto:** 2026-03-21 (análise de logs da TUI)
- **Impacto:** A TUI cria/conecta ao banco via `get_db_path()` (path relativo `src/data/timeblock.db`), mas quando executada de outro diretório de trabalho, o path relativo resolve para um banco inexistente. O SQLModel cria o arquivo vazio (0 bytes) sem tabelas. Todas as operações da TUI falham silenciosamente via `service_action` — `no such table: routines`, `no such table: tasks`, `no such table: time_log`, `no such table: habitinstance`. O dashboard renderiza placeholders vazios sem nenhuma indicação de erro ao usuário. A CLI funciona porque é executada a partir do diretório do projeto.
- **Correção:** (1) `get_db_path()` deve usar path absoluto ou XDG path canônico, nunca relativo ao CWD. (2) A TUI deve chamar `create_db_and_tables()` no startup se o banco não tiver tabelas. (3) `service_action` deve notificar o usuário quando ocorrem erros de banco (atualmente engole tudo).
- **BRs afetadas:** Todas — nenhuma funcionalidade da TUI opera sem banco.
- **Resolvido em:** 2026-03 (fix/dt056-xdg)

### DT-057: Delete de rotina falha silenciosamente na TUI (ALTA)

- **Descoberto:** 2026-03-21 (teste manual da dashboard)
- **Impacto:** O ConfirmDialog de deleção de rotina fecha com Enter, o callback `on_confirm` executa `service_action(delete_routine)`, mas o delete falha por FK RESTRICT (rotina tem hábitos vinculados). O `service_action` captura o `OperationalError` e retorna `(None, "Erro interno")`, mas o callback ignora o retorno — nenhuma notificação é exibida ao usuário. A rotina permanece ativa como se nada tivesse acontecido. A CLI trata esse caso corretamente: lista os hábitos vinculados e pede confirmação para cascade delete.
- **Correção:** (1) `on_confirm` em `crud_routines.py` deve verificar o retorno de `service_action` e exibir `app.notify(error)` se houver erro. (2) Avaliar se a TUI deve oferecer cascade delete (como a CLI) ou apenas informar que a rotina tem hábitos e não pode ser deletada.
- **BRs afetadas:** BR-ROUTINE-002 (soft delete), BR-TUI-016 (CRUD de rotinas)
- **Resolvido em:** 2026-03 (fix/quick-dts)

### DT-058: Logging ausente na CLI — apenas TUI loga via service_action (RESOLVIDO)

- **Descoberto:** 2026-03-21 (análise de logs)
- **Resolvido em:** 2026-04 (MR !73) — sys.excepthook global, TUI \_handle_exception override, logger em todos os CLI commands e 21 except blocks de widgets/screens
- **Impacto:** Apenas chamadas via `service_action` (exclusivo da TUI) geram log entries. Operações via CLI (commands Typer) não passam por esse wrapper e não geram nenhum log. Operações externas à TUI que modifiquem o banco (create, delete, update via CLI) são invisíveis nos logs, dificultando diagnóstico de inconsistências entre CLI e TUI.
- **Correção:** Adicionar logging estruturado nos commands da CLI, idealmente via decorator ou middleware que capture entrada, saída e erros de cada comando.
- **BRs afetadas:** Nenhuma diretamente — observabilidade.

### DT-059: Mensagens de migração visíveis no stdout da TUI (RESOLVIDO)

Na primeira execução após criação do banco, a mensagem `[INFO] Migração 002 aplicada` aparecia no terminal antes do dashboard abrir.

- **Descoberto:** 2026-03-21 (Sessão 8)
- **Severidade:** UX — MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-04 — `configure_logging(console=False)` no entry point da TUI (`main.py` linha 95). Migrations rodam com logging silenciado no console; erros críticos registrados apenas no arquivo de log.

### DT-060: Sidebar redesign (RECLASSIFICADO → Feature)

- **Status:** Movido para roadmap v1.8.0
- **Ver:** `docs/reference/roadmap.md` seção v1.8.0, ADR-042

### DT-061: AgendaPanel sem scroll horizontal

AgendaPanel não tem scroll horizontal. Com 3+ colunas de sobreposição, blocos ficam com ~12 chars cada, truncando títulos severamente. A falta de scroll H é o bloqueador principal para multi-coluna legível.

- **Descoberto:** 2026-03-22 (Sessão 9 — design review)
- **Severidade:** UX — ALTA (bloqueador de multi-coluna legível)
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03 (feat/agenda-blocks) — Margem de horas separada, `ScrollableContainer` com scroll horizontal.

**Solução proposta:**

1. Separar margem de horas (`Static`) do conteúdo de blocos (`ScrollableContainer` com `scroll_x`)
2. Layout: `Horizontal(horas_widget, blocos_scrollable)`
3. Input: Shift+scroll wheel; Shift+h/l (vi-like)
4. Largura mínima de coluna: 18 chars (não encolhe)
5. Indicador de overflow (`→`/`←`) no BorderTitle do painel
6. `←→` sem Shift SEMPRE muda dia (sem ambiguidade com scroll)

**Referências:** ADR-041, BR-TUI-031

### DT-062: Linhas horizontais cortam blocos de tempo coloridos

A renderização atual usa linhas horizontais (`───`) na régua de horário que atravessam os blocos de tempo coloridos, criando intersecções (`─┼─`) que quebram a continuidade visual. É o bug visual mais perceptível do dashboard.

- **Descoberto:** 2026-03-22 (Sessão 9 — design review, análise da print)
- **Severidade:** UX — ALTA (visual quebrado é o bug mais visível)
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03 (feat/agenda-blocks) — Accent bar + cor sólida, linhas horizontais removidas, intersecções eliminadas.

**Solução proposta:**

1. Primeira linha do bloco: `{título} {ícone}` (sem cor, texto limpo)
2. Linhas seguintes: `▌{cor_sólida}` (accent bar + preenchimento)
3. Pontilhado (`· · ·`) onde não há bloco
4. Remover linhas `───` e intersecções `─┼─`
5. Cada linha = 15min (não 30min)
6. Horário de término do bloco AINDA tem cor; linha seguinte é livre

**Referências:** ADR-041, BR-TUI-032

### DT-063: Paginação de dias (RECLASSIFICADO → Feature)

- **Status:** Movido para roadmap v1.8.0
- **Ver:** `docs/reference/roadmap.md` seção v1.8.0, BR-TUI-030

### DT-064: CVE-2026-4539 pygments sem fix disponível

pip-audit falhava no CI porque pygments 2.19.2 tinha CVE-2026-4539 — ReDoS local no AdlLexer (CVSS 3.3 LOW). Workaround `--ignore-vuln` foi adicionado ao CI temporariamente.

- **Descoberto:** 2026-03-24 (Sessão 12 — pipeline bloqueado)
- **Severidade:** BAIXA (CVE local-only, AdlLexer não usado no projeto)
- **Status:** RESOLVIDO (Pygments 2.20.0 corrige CVE-2026-4539)
- **Resolvido em:** 2026-04-02 — Pygments atualizado para 2.20.0, `--ignore-vuln` removido do CI

**Referências:** https://github.com/pygments/pygments/issues/3058

### DT-065: Layout adaptativo (RECLASSIFICADO → Feature)

- **Status:** Movido para roadmap v1.8.0
- **Ver:** `docs/reference/roadmap.md` seção v1.8.0

### DT-066: Placeholders truncados nos panels

Mensagens "Crie uma rotina: atomvs routine ac..." cortadas dentro do panel body. Essas instruções deveriam ir para o footer contextual (status_bar), não para o corpo do panel.

- **Descoberto:** 2026-03-25 (Sessão 12 — snapshot 80x24)
- **Severidade:** BAIXA
- **Status:** RESOLVIDO (2026-04, MR !64)
- **Resolvido em:** 2026-04 — Hints movidos para footer contextual via status_bar

### DT-067: README sem links para diagramas + diagramas desatualizados (RESOLVIDO)

16 diagramas em `docs/diagrams/` sem referência no README e com conteúdo divergente do código v1.7.0.

- **Descoberto:** 2026-03-25 (Sessão 12)
- **Severidade:** MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-04 (MR !72) — 14 diagramas auditados contra código v1.7.0 (2 removidos, 5 atualizados, 9 reescritos). README atualizado com ASCIIs corrigidos e links Mermaid para cada diagrama.

### DT-068: Habits não ordenados por scheduled_start (RESOLVIDO)

O HabitsPanel exibia hábitos na ordem de criação (ID sequencial), não por horário.

- **Descoberto:** 2026-03-27 (Sessão 13 — revisão de snapshots)
- **Severidade:** MÉDIA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-03 (fix/habit-sort-dt068) — `loader.py` ordena instâncias via `sorted(instances, key=lambda i: i["start_minutes"])` (linha 272).

### DT-069: Settings screen (RECLASSIFICADO → Feature)

- **Status:** Movido para roadmap v1.8.0
- **Ver:** `docs/reference/roadmap.md` seção v1.8.0

### DT-070: 47 ADRs padronizados (RESOLVIDO)

Headers de ADRs usavam formatos inconsistentes: datas em formatos mistos, títulos sem padrão, campos faltando.

- **Descoberto:** 2026-04-04 (Sessão 17 — auditoria de documentação)
- **Severidade:** BAIXA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-04-06 (chore/v1.7.1-snapshot) — 47 ADRs padronizados com headers em PT-BR, datas ISO, campos de status e revisão.

### DT-071: Sem padrão de header/footer em documentação (PENDENTE)

Documentos em `docs/` não seguem formato consistente de metadados: alguns têm versão no topo, outros não; datas em formatos variados; sem campo de status ou última revisão.

- **Descoberto:** 2026-04-04 (Sessão 17 — auditoria de documentação)
- **Severidade:** BAIXA
- **Status:** PENDENTE
- **Sprint planejado:** Sprint futuro

### DT-072: Job sync:github substituído por GitLab Push Mirroring (RESOLVIDO)

Job CI `sync:github` usava `git push --mirror` manual com token. Frágil, falhava com force push e branches protegidas no GitHub.

- **Descoberto:** 2026-04-06 (Sessão 17 — pipeline falho em main)
- **Severidade:** BAIXA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-04-06 (chore/replace-sync-job) — Substituído por GitLab Push Mirroring nativo (Settings → Repository → Mirroring). Job removido do `.gitlab-ci.yml`.

### DT-073: `__pycache__` com paths absolutos impede portabilidade

- **Descoberto:** 2026-04-08 (Sessão 18 — mudança de diretório do projeto)
- **Severidade:** BAIXA
- **Status:** PENDENTE
- **Impacto:** Editable installs (`pip install -e .`) compilam `.pyc` com paths absolutos. Mover o projeto para outro diretório causa `FileNotFoundError` nos testes BDD (`pytest-bdd` resolve feature paths via `__file__` do `.pyc` cached). Workaround: `find . -name __pycache__ -exec rm -rf {} +` seguido de recriar venv.
- **Correção permanente:** Documentar no CONTRIBUTING.md que mover o projeto requer recriar venv e limpar `__pycache__`. Considerar `PYTHONDONTWRITEBYTECODE=1` no CI.

### DT-074: BRs e Humble Objects com testes intencionados ausentes (RESOLVIDO)

Quinze BRs do catálogo não tinham cobertura direta em arquivos de teste no momento da auditoria estrutural conduzida em abril/2026. A concentração era no domínio TUI (nove de quinze), refletindo o padrão Humble Object aplicado pelo ADR-041 onde os widgets delegam para renderers puros — alguns desses renderers ficaram sem teste de unidade direta.

- **Descoberto:** 2026-04-10 (auditoria estrutural pré-v1.7.2)
- **Severidade:** ALTA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-04 — MR de caracterização (`test/v1.7.2-coverage-renderer-and-tasks`) cobriu lacunas críticas em renderers da agenda e em fluxos de tasks. Cobertura geral mantida em ~82% e a issue #42 do GitLab agora rastreia apenas as quinze BRs sem cobertura ainda pendentes (escopo movido para v1.7.5).
- **Issue de continuação:** #42 (priority::high, milestone v1.7.5)

### DT-075: BR fantasma BR-EVENT-002 vs nomenclatura BR-REORDER-XXX

`tests/unit/test_services/test_event_reordering_models.py` referencia `BR-EVENT-002` em cinco docstrings de métodos de teste. Inspeção do arquivo `docs/reference/business-rules/br-event.md` revela que o domínio inteiro é nomeado `BR-REORDER-XXX`, não `BR-EVENT-XXX`. A nomenclatura é portanto inconsistente em três níveis: filename (`br-event.md`), identificadores internos do arquivo (`BR-REORDER-001` a `BR-REORDER-006`) e referências em testes (`BR-EVENT-002`).

- **Descoberto:** 2026-05-01 (auditoria estrutural da Sessão 28)
- **Severidade:** BAIXA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-05-28 (Opção A) — commits `10ac4fd` (rename `br-event.md` → `br-reorder.md` + refs em index.md/mkdocs.yml), `3095b7b` (nomenclatura no teste: classe, 4 métodos, 5 docstrings → BR-REORDER-001) e `4ed781c` (rastreabilidade: 4 testes anexados à BR-REORDER-001). Instância event-reordering do Caso 3 da issue #42 fechada; br-task.md/br-skip.md seguem em aberto sob #42.
- **Impacto:** Quebra de rastreabilidade BR → Teste. Buscas como `grep -rn "BR-REORDER" tests/` não localizam os cinco testes que de fato cobrem a regra. Não há impacto funcional.
- **Correção sugerida:** opção A (mais barata) — renomear filename para `br-reorder.md`, manter os seis identificadores internos como estão e atualizar os cinco docstrings dos testes para `BR-REORDER-001` correspondente. Opção B — renomear todo o conjunto de identificadores para `BR-EVENT-XXX`, mais invasiva.

### DT-076: TimerScreen é placeholder com cinco TODOs ao TimerService

`src/timeblock/tui/screens/timer.py` carrega cinco TODOs apontando para integração com `TimerService` que nunca foi feita: linha 174 (`start_timer`), linha 182 (`pause_timer`), linha 185 (`resume_timer`), linha 192 (`stop_timer`), linha 211 (`reset_timer`). A tela existe no roteamento da TUI (BR-TUI-006) mas opera como placeholder visual — o display de contagem é local, sem persistência de TimeLog nem integração com o ciclo de vida do timer no banco.

- **Descoberto:** 2026-05-01 (auditoria estrutural da Sessão 28)
- **Severidade:** MÉDIA
- **Status:** PENDENTE
- **Impacto:** Usuários que naveguem para a TimerScreen via keybinding têm UX divergente do que o dashboard oferece via TimerPanel. O timer da TimerScreen não conta a favor de streak nem grava TimeLog. Atualmente a feature é mascarada porque o fluxo principal de uso (dashboard) não passa pela TimerScreen.
- **Correção sugerida:** integrar com `TimerService` seguindo o padrão já estabelecido no `TimerPanel` do dashboard. Trabalho cabível em v1.8.0 dado que a refatoração do `TimerService` (ADR-053) está prevista para v2.0-alpha — uma alternativa é remover a TimerScreen do roteamento até a refatoração e reintroduzir após.

### DT-077: Drift histórico **version** 0.1.0 vs pyproject.toml (RESOLVIDO)

Desde a fundação do projeto, `pyproject.toml` evoluiu sua declaração de `version` a cada release enquanto `src/timeblock/__init__.py` permaneceu congelado no placeholder de bootstrap `__version__ = "0.1.0"`. O drift acumulou ao longo de quase dezessete versões publicadas e gerava confusão em consumidores que importavam a constante para fins de logging ou diagnóstico.

- **Descoberto:** 2026-05-01 (auditoria do tar para release v1.7.3, Sessão 28)
- **Severidade:** BAIXA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-05-01 (v1.7.3, commit `8580c9a`) — `__init__.py` refatorado para ler via `importlib.metadata.version("atomvs-timeblock-terminal")`, eliminando a duplicação. `pyproject.toml` é agora a única fonte de verdade. Validação local após `pip install -e . --no-deps --force-reinstall` confirmou `__version__: 1.7.3` lido do metadata.
- **Referência:** CHANGELOG `[1.7.3] - 2026-05-01`

### DT-078: Testes de integração sem guarda global de banco isolado

Os testes de integração CLI (`tests/integration/commands/`) sofrem falhas intermitentes (`exit_code 2`, mensagens de listagem ausentes) quando rodados como parte da suíte completa, mas passam quando rodados isoladamente. A causa não é contaminação de estado entre arquivos de teste, e sim **concorrência com uma instância ATOMVS em execução** tocando o banco XDG real (`~/.local/share/atomvs/atomvs.db`).

A suíte tem isolamento parcial: `tests/unit/test_tui/conftest.py` força `TIMEBLOCK_DB_PATH=:memory:` (autouse, scope sessão) e `tests/integration/conftest.py` usa engine em memória próprio (`integration_engine`, ADR-033). Mas os testes CLI dependem exclusivamente da fixture `isolated_db` (scope função), e qualquer teste de integração que não a use cai no path XDG default via `get_db_path()`. Não existe guarda **global** que garanta que nenhum teste, em nenhuma circunstância, toque o banco real.

Quando há uma TUI/CLI ATOMVS aberta em paralelo durante a execução da suíte, ocorre contenção de lock SQLite no banco XDG: comandos CLI de teste que resolvem para esse path falham de forma não-determinística. Em CI (ambiente headless, sem instância concorrente) o problema nunca se manifesta — o pipeline da MR !99 passou os 8 jobs verdes, incluindo `test:e2e`, enquanto a mesma suíte falhava localmente.

- **Descoberto:** 2026-05-30 (Sessão 30, durante validação da suíte completa antes do push da issue #46)
- **Severidade:** BAIXA
- **Status:** RESOLVIDO
- **Resolvido em:** 2026-05-30 — fixture autouse de escopo sessão `_isolate_production_database` no `tests/conftest.py` raiz força `TIMEBLOCK_DB_PATH` para um arquivo temporário (`tempfile.mkdtemp()`) caso não esteja definido. Acompanha BR-TEST-003 e dois testes-guarda em `tests/unit/test_infra/test_db_isolation_guard.py` (RED→GREEN). Suíte unit: 1128 passed. Nota: `tmp_path_factory` causava deadlock na coleta quando resolvido dentro de uma autouse de sessão — `tempfile.mkdtemp()` foi a alternativa adotada.
- **Impacto:** Nenhum em produção (uso real tem instância única) nem em CI (sem concorrência). Afeta apenas rodadas locais da suíte completa quando há ATOMVS aberto, gerando falsos negativos que custam tempo de diagnóstico. O ADR-026 já previa "falhas intermitentes" como sintoma do isolamento incompleto.

**Investigação:**

Cinco hipóteses foram testadas; quatro refutadas com evidência, uma confirmada.

1. **Engine cacheado globalmente** — REFUTADO. `get_engine()` em `database/engine.py` cria o engine na chamada, sem `lru_cache` nem singleton de módulo.
2. **Paralelismo pytest-xdist** — REFUTADO. `addopts` não contém `-n`; a suíte roda sequencialmente por padrão.
3. **Path congelado no import (`config.py` vs `engine.py`)** — REFUTADO. O `config.py` não lê mais `TIMEBLOCK_DB_PATH` (a duplicação que o ADR-026 condenava foi resolvida); um probe importando `config` + `main` antes de `get_db_path()` retornou o path da env corretamente.
4. **Vazamento de path (teste escreve no banco real mesmo com env setada)** — REFUTADO. Com `TIMEBLOCK_DB_PATH` apontando para `/tmp`, um comando CLI deixou o banco XDG real intocado (mtime imutável) e criou dados apenas no tmp. A resolução de path está sã.
5. **Concorrência com instância ATOMVS no banco XDG real** — CONFIRMADO. A suíte `integration/` passou 115/115 sem TUI aberta; havia falhado 10/115 com uma TUI em tab paralela (mtime do banco real recente, tempo de execução 4x maior por contenção de lock). A suíte completa com TUI fechada passou 1399 testes (apenas os 9 snapshots da issue #54 falharam, pré-existentes).

**Workaround imediato:** fechar qualquer instância ATOMVS antes de rodar a suíte (`pgrep -af atomvs` para verificar), ou exportar `TIMEBLOCK_DB_PATH` para um arquivo temporário antes de invocar o pytest.

**Correção sugerida:** generalizar o padrão de `tests/unit/test_tui/conftest.py` para a suíte inteira — fixture `autouse` de escopo sessão no `tests/conftest.py` que força `TIMEBLOCK_DB_PATH` para um arquivo temporário caso não esteja definido, garantindo que nenhum teste jamais resolva para o banco XDG real. Acompanhar de teste-guarda que asserta que `get_db_path()` nunca retorna o path XDG durante a suíte (transforma a fragilidade silenciosa em falha determinística). Atualizar o ADR-026 notando o gap fechado.

- **Referências:** ADR-026 (Test Database Isolation Strategy), ADR-033 (Fixture scope sessão com rollback), ADR-040 (Unified Database Path), issue #54 (snapshots flaky — distinta, mas mesma família de fragilidade de teste).

---

## 3. Política de Gestão

Novos débitos técnicos devem ser registrados aqui com ID sequencial (DT-XXX), severidade e sprint planejado para resolução. O inventário é revisado a cada release.

**Severidades:**

- **CRÍTICA:** Bloqueia desenvolvimento ou deploy
- **ALTA:** Impacta qualidade ou manutenibilidade significativamente
- **MÉDIA:** Degradação gradual, deve ser resolvido no próximo release
- **BAIXA:** Cosmético ou preferencial, resolver quando conveniente
- **ACEITO:** Débito consciente com justificativa documentada

---

## 4. Catálogo de Refatorações

Refatorações catalogadas seguem nomenclatura RF-XXX com referência a Fowler (2018). Itens resolvidos são mantidos como registro histórico. Novos itens seguem ID sequencial.

| RF     | Descrição                           | Fowler (2018)                | Status            | DT relacionado |
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

### 4b. Quick Status

- [ ] RF-001 — Extract Delegate (quick actions)............. Pendente
- [x] RF-002 — C_HIGHLIGHT → colors.py...................... RESOLVIDO
- [ ] RF-003 — Split Phase (data loading)................... Pendente
- [x] RF-004 — Remove @staticmethod duplicado............... RESOLVIDO
- [ ] RF-005 — Dict → dataclass nos panels.................. Pendente
- [ ] RF-006 — Polimorfismo por status...................... Adiado (Sprint 6)
- [x] RF-007 — Empty state centralizado..................... RESOLVIDO
- [ ] RF-008 — Counter em \_refresh_content................. Pendente
- [x] RF-009 — Imports lazy eliminados...................... RESOLVIDO
- [ ] RF-010 — Split timer_service.py (549 linhas).......... Adiado (Sprint 5)

---

## 5. Changelog do Documento

| Data       | Versão | Mudanças                                                               |
| ---------- | ------ | ---------------------------------------------------------------------- |
| 2026-05-30 | 2.37.0 | DT-078 RESOLVIDO: fixture autouse de isolamento global de              |
|            |        | banco (BR-TEST-003) + teste-guarda em test_infra. Sessão 30.           |
| 2026-05-30 | 2.36.0 | DT-078 registrado (EM RESOLUÇÃO): testes de integração                 |
|            |        | sem guarda global de banco isolado. Causa-raiz: concorrência           |
|            |        | com instância ATOMVS no banco XDG real. Cinco hipóteses                |
|            |        | testadas (quatro refutadas).                                           |
| 2026-05-28 | 2.35.0 | DT-075 RESOLVIDO: rename para br-reorder.md,                           |
|            |        | nomenclatura no teste e rastreabilidade BR-REORDER-001;                |
|            |        | Caso 3 (event-reordering) da #42 fechado.                              |
| 2026-05-01 | 2.34.0 | DT-074 RESOLVIDO. Adicionados DT-075                                   |
|            |        | (BR fantasma BR-EVENT-002), DT-076 (TimerScreen                        |
|            |        | placeholder), DT-077 (drift **version** resolvido em                   |
|            |        | v1.7.3). Achados originados em auditoria estrutural da Sessão 28.      |
| 2026-04-10 | 2.33.0 | Adicionado DT-074: BRs e Humble Objects com testes                     |
|            |        | intencionados ausentes. Cobertura iniciada em MR de                    |
|            |        | testes de caracterização (test/v1.7.2-coverage-renderer-and-tasks).    |
| 2026-04-08 | 2.32.0 | DT-073 registrado, inventário DT025/058/067 corrigido,                 |
|            |        | DT026-033 adicionados, detalhamentos alinhados                         |
| 2026-04-08 | 2.31.0 | DT-058 RESOLVIDO (MR !73), DT-067 RESOLVIDO (MR !72),                  |
|            |        | 5 DTs reclassificados como features (→ roadmap v1.8.0)                 |
| 2026-04-06 | 2.29.0 | DT-072 RESOLVIDO: sync:github substituído por GitLab Push Mirroring    |
| 2026-04-05 | 2.28.0 | DT-066 RESOLVIDO (MR !64), DT-065/DT-067 re-tagged para v1.7.1,        |
|            |        | contagens atualizadas (58/71 resolvidos, 12 pendentes, 1 aceito)       |
| 2026-03-27 | 2.25.0 | Registra DT-068 (sort habits), DT-069 (tela configurações)             |
| 2026-03-25 | 2.24.0 | Registra DT-065/066/067 (responsividade, placeholders, diagramas)      |
| 2026-03-25 | 2.23.0 | DT-064 registrado (CVE pygments), DT-044 atualizado (basic->standard)  |
| 2026-03-22 | 2.21.0 | Registra DT-059 a DT-063 (redesign agenda, sidebar, scroll, paginação) |
| 2026-03-19 | 2.19.0 | DT-026 resolvido (load_metrics com filtro de rotina)                   |
| 2026-03-19 | 2.18.0 | DT-009/010/011/041/042/043 resolvidos                                  |
| 2026-03-19 | 2.17.0 | DT-046/047/048/050/051/052 resolvidos (fix/loader-critical)            |
| 2026-03-19 | 2.16.0 | DT-049/053/054/055 resolvidos (fix/loader-critical)                    |
| 2026-03-14 | 2.6.0  | DT-017/018/020 resolvidos. Registra DT-026 a 033                       |
|            |        | (bugs TUI encontrados em teste manual)                                 |
| 2026-03-13 | 2.5.0  | DT-022 resolvido (feat/structured-logging mergeado).                   |
|            |        | Adicionado DT-025 (Pyright CI complementar)                            |
| 2026-03-12 | 2.4.0  | Adicionados DT-023 e DT-024 (resolvidos): auto-geração                 |
|            |        | de instâncias diárias e keybindings VTE/GNOME                          |
| 2026-03-11 | 2.3.0  | Adicionado DT-022 (logging estruturado: escopo,                        |
|            |        | formato, ferramentas, plano de instrumentação)                         |
| 2026-03-11 | 2.2.0  | Adicionado DT-021 (loaders/CRUDs ORM fora da sessão),                  |
|            |        | resolvido na mesma sessão via auditoria preventiva                     |
| 2026-03-10 | 2.1.0  | DT-014 resolvido. Adicionados DT-015 a DT-020 (gaps de                 |
|            |        | integração: timer, agenda, métricas, command bar)                      |
| 2026-03-08 | 2.0.0  | DT-003 resolvido. Adicionados DT-008 a DT-014 (Sprint 4                |
|            |        | Code Review + GitHub CI + keybindings divergentes)                     |
| 2026-02-03 | 1.1.0  | Atualiza status: DT-004, DT-005, DT-006 resolvidos                     |
| 2026-02-01 | 1.0.0  | Extração do roadmap.md para documento dedicado                         |

---

**Próxima revisão:** Release v1.7.5

**Última atualização:** 2026-05-01
