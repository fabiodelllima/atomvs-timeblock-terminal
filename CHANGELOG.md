# Changelog

All notable changes to ATOMVS Time Planner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.7.1] - 2026-04-08

### Added

- Logging: sys.excepthook global for uncaught exceptions (CRITICAL level)
- Logging: TUI \_handle_exception override logs before Textual crash handler
- Logging: All CLI commands now log errors to JSON Lines file
- Logging: 21 bare-pass except blocks in TUI widgets/screens replaced with logger.debug
- Architecture diagram: docs/diagrams/architecture/system-overview.md (Mermaid)

### Changed

- README: Updated to ATOMVS Time Planner branding, badges (1345 tests, 82% coverage), stack, docs structure (Diataxis), roadmap
- README: ASCII diagrams corrected (TAG added, OVERDUE removed, CANCELLED in timer, keybindings)
- README: Mermaid diagram links below each ASCII diagram
- Diagrams: 14 diagrams audited — 2 removed, 5 updated, 9 rewritten to match v1.7.0 codebase
- technical-debt.md: 5 DTs reclassified as features (DT-019, DT-060, DT-063, DT-065, DT-069) moved to roadmap v1.8.0
- roadmap.md: New v1.8.0 section with 7 planned features

### Fixed

- main.py: launch_tui() no longer silences migration exceptions (was except:pass)
- main.py: Migration success now logged with count

## [1.7.0] - 2026-04-05

### Added

- TUI: Complete interactive dashboard with 5 functional panels (Habits, Tasks, Timer, Metrics, Agenda)
  - Textual framework with Tab/Shift+Tab navigation and internal cursor (j/k)
  - FocusablePanel as base for interactive panels with keyboard navigation
  - Color system with semantic tokens and WCAG-compliant palette (Catppuccin Mocha)
  - TCSS modularized into 7 files (base, layout, cards, dashboard, statusbar, timer, forms)
- TUI: Dashboard-first CRUD with contextual modals (ADR-034)
  - Create, edit and delete routines, habits and tasks via keybindings (n/e/x)
  - Reusable FormModal and ConfirmDialog widgets
  - PlaceholderActivated message for creation from empty state (BR-TUI-013)
- TUI: Quick actions on HabitsPanel — done (v), skip (s), timer (t), undo (u)
- TUI: Live timer with per-second updates, pause/resume/stop/cancel
- TUI: MetricsPanel with streak, completeness and weekly heatmap (BR-TUI-033, ADR-047)
  - Persistent best_streak via migration_003 (best_streak column on routines)
  - Retroactive PENDING instance generation for days without records (R8)
  - Keybinding f cycles display period between 7d/14d/30d (R7/R13)
  - Completeness calculated for 7d, 14d and 30d windows
  - Heatmap shows done/total per day with check marks
- TUI: Contextual footer with dynamic keybindings per focused panel (BR-TUI-007)
- TUI: Agenda with auto-refresh every 60s and auto-scroll to current time (BR-TUI-003-R15)
- TUI: StatusBar with active routine, contextual keybindings and timer elapsed
- TUI: Empty state with placeholder guidance in all panels
- TUI: Screen navigation — Dashboard, Routines, Habits, Tasks, Timer
- TUI: Widget system — NavBar, CommandBar, HelpOverlay, StatusBar, TimeblockGrid
- CLI: `atomvs demo create` with 3 mock routines and 8 tasks (BR-TUI-003-R28)
- CLI: `atomvs demo clear` to remove demo data (respects FK constraints)
- BDD: 8 TUI feature files in Gherkin format (61 scenarios)
- migration_003: best_streak column on routines table
- ADR-031 through ADR-047: 17 new architectural decisions documented
- docs: BR-TUI-001 through BR-TUI-033 (33 TUI business rules)
- docs: Refactoring plan RF-001 through RF-010 based on Fowler (2018) and Humble & Farley (2010)

### Changed

- CLI: Entry point changed from `timeblock.main:app` to `timeblock.main:main` (TUI opens with `atomvs` without args)
- CI/CD: Pipeline optimized from 10 to 8 jobs
- CI/CD: GitHub Actions aligned with GitLab CI consolidation
- CI/CD: Test timeout increased to 45min for test:all, 60min for integration
- Navigation keybinding changed from j/i to j/k (vim industry standard)
- Contextual footer displays placeholder hints when empty panel is focused (DT-066)
- Snapshot testing guide rewritten with real data (17 tests / 19 baselines)
- BR-TUI-033-R5: Streak semantics corrected — no grace period, streak breaks on first non-100% day

### Fixed

- DT-059: Migration messages on stdout replaced with logger
- DT-064: CVEs resolved (aiohttp 3.13.5, Pygments 2.20.0)
- DT-066: Placeholder hints moved from panel body to contextual footer
- DT-068: Habits not sorted by scheduled_start

### Metrics

- Total tests: ~1,340 (1,336 passed, +558 since v1.6.0)
- Distribution: Unit ~1,050 (78%), Integration ~130 (10%), BDD ~61 (5%), E2E ~95 (7%)
- Global coverage: ~82% (threshold 80%)
- BRs formalized: 115+ (+34 TUI since v1.6.0)
- ADRs: 47 documented (+15 since v1.6.0)
- DTs: 51 resolved / 66 total (77%)
- Pipeline: 8 jobs (~10min CI)

## [1.7.0] - 2026-04-05

### Added

- TUI: Dashboard interativo com 5 painéis funcionais (Habits, Tasks, Timer, Metrics, Agenda)
  - Textual framework com navegação Tab/Shift+Tab e cursor interno (j/k)
  - FocusablePanel como base para painéis interativos
  - Color system com semantic tokens e paleta WCAG-compliant
  - TCSS modularizado em 7 arquivos (base, layout, cards, dashboard, statusbar, timer, forms)
- TUI: Dashboard-first CRUD com modais contextuais (ADR-034)
  - Criação, edição e deleção de rotinas, hábitos e tasks via keybindings (n/e/x)
  - FormModal e ConfirmDialog reutilizáveis
  - PlaceholderActivated para criação a partir de empty state (BR-TUI-013)
- TUI: Quick actions no HabitsPanel — done (v), skip (s), timer (t), undo (u)
- TUI: Timer live com atualização a cada segundo, pause/resume/stop/cancel
- TUI: MetricsPanel com streak, completude e heatmap semanal (BR-TUI-033, ADR-047)
  - Streak persistido no banco via migration_003 (best_streak em routines)
  - Geração retroativa de instâncias PENDING para dias sem registro (R8)
  - Keybinding f alterna período entre 7d/14d/30d (R7/R13)
  - Completude calculada para 7d, 14d e 30d
  - Heatmap mostra done/total por dia com check marks
- TUI: Footer contextual com keybindings dinâmicos por painel focado (BR-TUI-007)
- TUI: Agenda com auto-refresh a cada 60s e auto-scroll na hora atual (BR-TUI-003-R15)
- TUI: StatusBar com rotina ativa, keybindings e timer elapsed
- TUI: Empty state com placeholders orientativos em todos os painéis
- CLI: `atomvs demo create` com 3 rotinas mock e 8 tasks (BR-TUI-003-R28)
- CLI: `atomvs demo clear` para remover dados de demonstração
- BDD: 8 features TUI em formato Gherkin (61 scenarios)
- migration_003: campo best_streak na tabela routines
- ADR-031 a ADR-047: 17 novas decisões arquiteturais documentadas
- docs: BR-TUI-001 a BR-TUI-033 (33 regras de negócio TUI)

### Changed

- CLI: Entry point alterado para abrir TUI com `atomvs` sem argumentos
- CI/CD: Pipeline otimizado de 10 para 8 jobs
- CI/CD: GitHub Actions sincronizado com GitLab CI
- Footer contextual exibe hints de placeholder quando painel vazio está focado (DT-066)
- Documentação: snapshot-testing.md reescrito com dados reais
- BR-TUI-033-R5: Semântica do streak corrigida — sem grace period

### Fixed

- DT-059: Mensagens de migração no stdout substituídas por logger
- DT-064: CVEs resolvidos (aiohttp 3.13.5, Pygments 2.20.0)
- DT-066: Hints de placeholder movidos do corpo dos painéis para footer contextual
- DT-068: Hábitos não ordenados por scheduled_start

### Metrics

- Testes: ~1.340 (1336 passed, +558 desde v1.6.0)
- Distribuição: Unit ~1050 (78%), Integration ~130 (10%), BDD ~61 (5%), E2E ~95 (7%)
- Cobertura global: ~82% (threshold 80%)
- BRs formalizadas: 115+ (+34 TUI desde v1.6.0)
- ADRs: 47 documentados (+15 desde v1.6.0)
- DTs: 51 resolvidos / 66 total (77%)
- Pipeline: 8 jobs (~10min CI)

## [1.6.0] - 2026-02-12

### Added

- CI/CD: Docker image with pre-installed dependencies (Dockerfile.ci)
- CI/CD: DevSecOps with Bandit (SAST) and pip-audit (SCA)
- CI/CD: Combined coverage from 4 suites via coverage run
- CI/CD: Updated pre-commit hooks (ruff on commit, full suite on push)

### Changed

- refactor: Flattened structure from cli/ to project root
- CI/CD: Pipeline migrated to Docker (eliminates pip install overhead)
- CI/CD: Removed build:docs from pipeline (manual validation)
- CI/CD: GitHub Actions aligned with GitLab CI

### Fixed

- fix: CVE-2026-1703 in pip 25.3 (updated to pip>=26.0)
- fix: pytest-cov auto-combined partials (migrated to coverage run)
- fix: Partial threshold blocked individual jobs (--cov-fail-under=0)

### Metrics

- Total tests: 778 (576 unit, 116 integration, 56 bdd, 30 e2e)
- Global coverage: 87% (threshold 85%)
- Pipeline: 9 jobs (quality + test + coverage + security + sync)
- ADRs: 32 documented

## [1.5.0] - 2026-02-03

### Added

- CI/CD: Automatic sync GitLab => GitHub via sync:github job
- CI/CD: GitHub Merge Queue support (merge_group event)
- CI/CD: Sync stage in GitLab pipeline
- docs: cicd-flow.md v2.0 with complete dual-repo architecture

### Changed

- CI/CD: GitLab defined as source of truth
- CI/CD: GitHub configured as public showcase
- CI/CD: Branch protection adjusted for automatic sync

### Fixed

- CI/CD: Divergent histories between GitLab and GitHub
- CI/CD: Token scope workflow for GitHub Actions updates

### Metrics

- Total tests: 873 (+188 since v1.4.1)
- Global coverage: 76% (+5pp since v1.4.1)
- Distribution: Unit 696 (79.7%), Integration 83 (9.5%), BDD 52 (6.0%), E2E 42 (4.8%)
- GitLab CI: 8 jobs (6 test + 1 build + 1 sync)
- Pipeline time: ~3min (local => GitHub sync)

## [1.4.1] - 2026-01-30

### Added

- test(e2e): 16 E2E tests for task lifecycle (BR-TASK-001 to 005)
- test(e2e): 12 E2E tests for list command filters
- docs: ATOMVS logo and expanded table of contents in README
- docs: Updated quality-metrics.md with v2.0.0 metrics
- docs: Updated references (SWEBOK v4.0, ISO/IEC/IEEE 29148:2018)

### Metrics

- Total tests: 685 (+172 since v1.4.0)
- Global coverage: 71% (+27pp since v1.4.0)
- E2E tests: 42 (+28)
- Distribution: Unit 513 (75%), Integration 83 (12%), E2E 42 (6%), BDD 7 (1%)

## [1.4.0] - 2026-01-28

### Added

- ADR-027: Documentation Tooling (MkDocs + mkdocstrings)
- BR-CLI-002: Multi-format datetime parser (ISO 8601, DD-MM-YYYY, DD/MM/YYYY)
- Section 5 in architecture.md with actual models (Event, PauseLog, ChangeLog)
- Enum documentation: TimerStatus, EventStatus, ChangeType
- Section 7 in architecture.md with 27 categorized ADRs
- glab CLI for GitLab pipeline monitoring

### Fixed

- GitLab/GitHub CI: added `pip install -e .` to resolve ModuleNotFoundError
- mkdocs.yml aligned with consolidated docs/ structure
- Broken links in ADRs and diagrams (DT-009)

### Updated

- Dependencies: sqlmodel 0.0.31, typer 0.21.1, SQLAlchemy 2.0.46, ruff 0.14.14
- pytest 9.0.2, mypy 1.19.1, rich 14.3.1, coverage 7.13.2

### Metrics

- Tests: 513 passing
- Coverage: 44% (unit)
- ADRs: 27 documented
- BRs: 67 formalized
- Mypy: 0 errors

## [1.3.2] - 2026-01-22

### Added

- BR-VAL-001: Time Validation (20 unit tests)
- BR-VAL-002: Date Validation (35 unit tests)
- BDD structure for date validation feature
- pyright configuration in pyproject.toml

### Fixed

- Enabled BDD steps for date_validation (BR-VAL-002)
- validate_date import in step definitions

### Metrics

- Tests: 466 → 558 (+92)
- Coverage: 42% (+26pp from v1.3.1)
- Mypy: 0 errors

## [1.3.1] - 2026-01-19

### Added

- **ADR-026: Test Database Isolation Strategy**
  - Hybrid strategy: DI for unit, env var for integration
  - Standardized fixtures in conftest.py
  - Documentation in architecture.md section 4.4

- **BR → Tests Coverage Analysis**
  - Complete matrix in quality-metrics.md section 6.1
  - 52 BRs documented, 35 with tests (67%)
  - 17 BRs identified without coverage
  - Updated roadmap with implementation plan

### Changed

- **SSOT for database path**
  - Centralized in `engine.get_db_path()`
  - Removed `DATABASE_PATH` from config.py
  - Eliminated `sys.modules` hacks in tests

- **Simplified integration fixtures**
  - `isolated_db` uses only env var (ADR-026)
  - Removed duplicate local fixtures
  - `test_init.py` uses specific `empty_db_path`

### Fixed

- **BR-SKIP-003:** IGNORED can receive retroactive justification (recovery)

### Metrics

- 466 tests passing
- 65% global coverage
- 0 mypy errors
- 26 skipped tests (documented analysis)

## [1.3.0] - 2025-11-08

### Added

#### Testing and Quality Consolidation

**Testing Structure:**

- Consolidated structure in `05-testing/` (removed duplicate `07-testing/`)
- Added navigable documents:
  - `testing-philosophy.md` - Project testing philosophy
  - `requirements-traceability-matrix.md` - Complete RTM with BR => Test => Code traceability
  - `test-strategy.md` - Consolidated test strategy
- 5 test scenarios now accessible:
  - event-creation
  - conflict-detection
  - event-reordering
  - habit-generation
  - timer-lifecycle

**Complete Glossary:**

- Glossary expanded to 298 lines in `01-architecture/12-glossary.md`
- All main terms defined (TimeBlock, Habit, HabitInstance, Event, etc)
- HabitAtom marked as DEPRECATED (marketing only)
- Relationships between concepts documented

**Formalized Business Rules:**

- `event-reordering.md` - Complete formal specification (222 lines)
- Fundamental principles: Explicit User Control, Information Without Imposition
- BR-EVENT-001 to BR-EVENT-007 documented
- Purpose change: System only DETECTS conflicts, doesn't propose automatic reordering

**Impact:**

- Consolidated testing structure without duplications
- Complete and precise glossary
- Formally specified Business Rules
- Philosophy alignment: user always in control

## [1.2.2-logging] - 2025-11-10

### Added

#### Structured Logging System - Sprint 1.3

**Logging Module:**

- `cli/src/timeblock/utils/logger.py` (118 lines)
  - `setup_logger()` with rotating file handler
  - `get_logger()` helper to obtain configured logger
  - `disable_logging()` / `enable_logging()` for tests
  - Structured format: `[timestamp] [level] [module] message`
  - Console and file support with automatic rotation (10MB, 5 backups)

**Tests:**

- test_habit_lifecycle.py: E2E test
- test_logging_integration.py: Integration
- test_logger.py: Unit tests
- test_habit_instance_service_extended.py
- Test coverage: 43% -> 83%

**Documentation:**

- PHILOSOPHY.md, ARCHITECTURE.md
- ADRs 015-018 (HabitAtom refactor)
- logging-strategy.md
- HabitAtom Sprints docs

## [1.2.1-docs] - 2025-11-11

### Added

#### Documentation Reorganization and Consolidation

**Documentation Structure:**

- 9 ADRs now navigable in mkdocs (ADR-012 to ADR-020)
  - ADR-012: Sync Strategy
  - ADR-013: Offline-First Schema
  - ADR-014: Sync UX Flow
  - ADR-015: HabitInstance Naming
  - ADR-016: Alembic Timing
  - ADR-017: Environment Strategy
  - ADR-018: Language Standards
  - ADR-019: Test Naming Convention
  - ADR-020: Business Rules Nomenclature

**Architecture Consolidation:**

- Unified structure in `01-architecture/` (removed `02-architecture/` and `01-guides/`)
- Added navigable documents:
  - `00-architecture-overview.md` - Consolidated overview (20KB)
  - `16-sync-architecture-v2.md` - Sync architecture v2.0
  - `17-user-control-philosophy.md` - User control philosophy (15KB)
  - `18-project-philosophy.md` - Atomic habits philosophy (12KB)

**Impact:**

- 20 navigable ADRs (vs 11 previously) = +82%
- Organized docs/ structure without duplications
- Project philosophy and principles documented

## [1.1.0] - 2025-11-01

### Added

#### Event Reordering System - Complete Implementation

- Automatic conflict detection between scheduled events
- Priority calculation based on status and deadlines (CRITICAL, HIGH, NORMAL, LOW)
- Sequential reordering algorithm respecting priorities
- Interactive confirmation before applying changes
- New CLI command: `timeblock reschedule [preview] [--auto-approve]`

**Enhanced Services:**

- `TaskService.update_task()` now returns tuple with optional ReorderingProposal
- `HabitInstanceService.adjust_instance_time()` integrated with conflict detection
- `TimerService.start_timer()` detects conflicts when starting timers

**New Components:**

- `EventReorderingService` - Central reordering logic (90% test coverage)
- `event_reordering_models.py` - Data structures (EventPriority, Conflict, ProposedChange, ReorderingProposal)
- `proposal_display.py` - Rich formatted CLI output for proposals
- `reschedule.py` - CLI command implementation

**Tests:**

- 78 new tests (219 total, +55% increase)
- 100% coverage in event_reordering_models
- 90% coverage in event_reordering_service
- Integration tests for all affected services

**Documentation:**

- Complete technical documentation in `docs/10-meta/event-reordering-completed.md`
- Sprint retrospective in `docs/10-meta/sprints-v2.md`
- Architecture and API documentation updated

### Changed

- Services now return tuples where appropriate to include reordering proposals
- Enhanced error messages with conflict information

### Breaking Changes

- None

### Performance

- Conflict detection optimized for O(n log n) complexity
- Efficient event queries in date ranges

## [1.0.0] - 2025-10-16

### Added

- Initial baseline release
- SQLite database initialization
- Basic CRUD operations for events
- Event listing with filters (day, week)
- Brazilian time format support (7h, 14h30)
- Basic conflict detection (warning only, non-blocking)
- Support for events crossing midnight
- 141 tests with 99% coverage

**CLI Commands:**

- `timeblock init` - Initialize database
- `timeblock add` - Create events
- `timeblock list` - List events with filters

### Known Limitations

- No recurring habits
- No automatic reordering
- No reports or analytics
- Basic CLI (no TUI)

---

[Unreleased]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.7.1...HEAD
[1.7.1]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.2.2-logging...v1.3.0
[1.2.2-logging]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.2.1-docs...v1.2.2-logging
[1.2.1-docs]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.1.0...v1.2.1-docs
[1.1.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/fabiodelllima/atomvs-timeblock-terminal/releases/tag/v1.0.0
