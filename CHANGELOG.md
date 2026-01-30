# Changelog

All notable changes to TimeBlock Organizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.4.1...HEAD
[1.4.1]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.2.2-logging...v1.3.0
[1.2.2-logging]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.2.1-docs...v1.2.2-logging
[1.2.1-docs]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.1.0...v1.2.1-docs
[1.1.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/fabiodelllima/timeblock-organizer/releases/tag/v1.0.0
