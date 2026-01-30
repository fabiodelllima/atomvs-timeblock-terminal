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

## [1.3.3] - 2026-01-22

### Added

- BR-CLI-002: Multi-format date parser (ISO 8601, DD-MM-YYYY, DD/MM/YYYY)
- 25 new tests for date parser (8 BDD + 17 unit)
- pyright configuration in pyproject.toml

### Fixed

- Enabled BDD steps for date_validation (BR-VAL-002)
- validate_date import in step definitions

### Metrics

- Tests: 466 → 558 (+92)
- Coverage: 65% → 67% (+2pp)
- Mypy: 0 errors maintained

### Changed (Documentation)

- **(2026-01-15)** Import Paths Standardization
  - Fixed imports from `src.timeblock.*` to `timeblock.*` across codebase
  - Updated mock/monkeypatch paths in 45+ test files
  - Resolved session isolation in tests (session injection)
  - Fixed truncated conftest.py from previous session
  - Updated metrics: 454 tests passing, 61% coverage

- **(2025-01-11)** Housekeeping and metrics correction
  - Deleted 15 obsolete branches (feat/_, fix/ci-_, refactor/\*)
  - README updated with actual metrics:
    - Version: v2.0.0 => v1.3.0
    - Tests: 492 => 441 (377 unit + 64 integration)
    - Coverage: 99% => 39%
  - Maintained README visual structure and diagrams

- **(2025-12-22)** Development Process and ADR-025
  - New section 11 in architecture.md: Development Process
  - ADR-025: Development Methodology (Vertical Slicing + Strict TDD)
  - Documented: Docs-First, BDD, Strict TDD, Sprints, WIP Limits
  - Updated ADR index: 24 => 25 (23 accepted, 2 proposed)

- **(2025-12-21)** Deployment Options and ADR-024
  - New section 10 in architecture.md: Deployment Options
  - Documented Raspberry Pi homelab as recommended server
  - Comparison: Pi vs VPS vs Desktop
  - ADR-024: Homelab Infrastructure Strategy
  - Updated ADR index: 23 => 24 (2 proposed)

- **(2025-12-21)** Roadmap v1.5-v4.0 and ADR-023
  - Added ADR-023: Microservices Ecosystem (Kafka, CloudEvents)
  - Documented complete roadmap in architecture.md:
    - v1.5.0: Infra Foundation (Docker, CI/CD)
    - v2.0.0: FastAPI REST API + Observability (Prometheus, Grafana, Loki)
    - v3.0.0: Microservices Ecosystem (Apache Kafka)
    - v4.0.0: Android App (Kotlin)
  - Updated ADR index: 22 => 23

- **(2025-12-01)** Complete docs/ reorganization
  - Consolidated 4 main documents in `docs/core/`:
    - architecture.md (v2.0.0)
    - business-rules.md (v3.0.0, 50 BRs)
    - cli-reference.md (v1.4.0)
    - workflows.md (v2.1.0)
  - Standardized 22 ADRs in `docs/decisions/` (ADR-XXX format)
  - Fixed duplicate ADR-021 to ADR-022
  - Moved 130+ obsolete docs to `docs/archived/`
  - Renamed: 02-diagrams to diagrams, 07-testing to testing
  - Updated broken links in ADRs and README

### BREAKING CHANGES

- **(2025-11-19)** Status+Substatus refactoring in HabitInstance (BR-HABIT-INSTANCE-STATUS-001)
  - `status` field changed from `HabitInstanceStatus` (5 values) to `Status` (3 values)
  - Old values: PLANNED, IN_PROGRESS, PAUSED, COMPLETED, SKIPPED
  - New values: PENDING, DONE, NOT_DONE
  - Automatic mapping in migration:
    - PLANNED/IN_PROGRESS/PAUSED => PENDING
    - COMPLETED => DONE + done_substatus=FULL
    - SKIPPED => NOT_DONE + not_done_substatus=SKIPPED_UNJUSTIFIED
  - **Action required:** Run migration_001_status_substatus.py
  - **Rollback available:** downgrade() function (new data loss)
  - **Compatibility:** HabitInstanceStatus kept as temporary alias (DEPRECATED)

### Added

- **(2025-11-19)** Enums for detailed tracking (BR-HABIT-INSTANCE-STATUS-001)
  - `Status`: PENDING, DONE, NOT_DONE
  - `DoneSubstatus`: FULL (90-110%), PARTIAL (<90%), OVERDONE (110-150%), EXCESSIVE (>150%)
  - `NotDoneSubstatus`: SKIPPED_JUSTIFIED, SKIPPED_UNJUSTIFIED, IGNORED
  - `SkipReason`: HEALTH, WORK, FAMILY, TRAVEL, WEATHER, LACK_RESOURCES, EMERGENCY, OTHER

- **(2025-11-19)** New fields in HabitInstance
  - `done_substatus`: DoneSubstatus (calculated based on completion %)
  - `not_done_substatus`: NotDoneSubstatus (skip/ignore categorization)
  - `skip_reason`: SkipReason (justified skip category)
  - `skip_note`: str (additional user note)
  - `completion_percentage`: int (persisted completion %)

- **(2025-11-19)** Status+Substatus consistency validations
  - DONE requires mandatory done_substatus
  - NOT_DONE requires mandatory not_done_substatus
  - PENDING cannot have substatus
  - Substatus are mutually exclusive
  - SKIPPED_JUSTIFIED requires mandatory skip_reason
  - skip_reason only allowed with SKIPPED_JUSTIFIED
  - `validate_status_consistency()` method implemented

- **(2025-11-19)** SQL migration (migration_001_status_substatus.py)
  - Adds 5 columns: done_substatus, not_done_substatus, skip_reason, skip_note, completion_percentage
  - Automatically migrates data preserving information
  - upgrade() and downgrade() functions for rollback
  - Metadata: version=001, name=status_substatus_refactoring

- **(2025-11-19)** Complete documentation (BR-HABIT-INSTANCE-STATUS-001)
  - BR-HABIT-INSTANCE-STATUS-001: Detailed specification
  - 18 BDD scenarios (Gherkin GIVEN/WHEN/THEN)
  - ADR-021: Architectural decision documented
  - 14 unit tests (100% passing)
  - Coverage: 84% (habit_instance.py)

- **(2025-11-17)** Integration fixtures for tests
  - `test_db` - Session with FK enabled
  - `sample_routine` - Pre-created Routine
  - `sample_habits` - 3 Habits with different recurrences
  - `sample_task` - Default Task
  - PRAGMA foreign_keys=ON in integration_engine

- **(2025-11-17)** BR-HABIT-004 validation: Recurrence Pattern
  - `habit.py` model validates recurrence via **init** override
  - 10 supported patterns (MONDAY-SUNDAY, WEEKDAYS, WEEKENDS, EVERYDAY)
  - Clear error messages listing valid values

- **(2025-11-17)** HABIT Business Rules implemented
  - BR-HABIT-001: Title Validation (not empty, max 200 chars, trim)
  - BR-HABIT-002: Time Range Validation (start < end)
  - BR-HABIT-003: Routine Association (FK constraint, delete RESTRICT)
  - BR-HABIT-004: Recurrence Pattern (validated enum)
  - BR-HABIT-005: Color Validation (optional hex format)

### Changed

- **(2025-11-19)** HabitInstance model refactored
  - Simplified status: 3 values instead of 5
  - Status+Substatus system for granularity
  - `is_overdue` property preserved (compatible)
  - Exports updated in `models/__init__.py`

- **(2025-11-17)** Services refactored with Dependency Injection
  - `task_service.py` - All methods accept optional session
  - `timer_service.py` - start_timer, stop_timer, etc. with session
  - `event_reordering_service.py` - detect_conflicts with session
  - `habit_service.py` - Complete CRUD with optional session
  - `habit_instance_service.py` - Generation and marking with session
  - Pattern: if session => use injected, else => create own

- **(2025-11-17)** Database engine with FK enabled
  - `engine.py` - PRAGMA foreign_keys=ON in SQLite

- **(2025-11-17)** Refactored imports
  - `routine_service.py` - Imports from src.timeblock.models
  - `conftest.py` - sqlalchemy.orm.Session => sqlmodel.Session

### Fixed

- **(2025-11-17)** Integration tests with Dependency Injection
  - 6 timer integration tests fixed (FK constraints resolved)
  - 4 fixtures validation tests fixed
  - Services now accept optional session: `session: Session | None = None`
  - Isolated tests with shared transactions
  - Production code maintains compatibility (backward compatible)

---

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

---

## [1.3.0] - 2025-11-08

### Added

#### **Testing and Quality Consolidation**

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

**Commits:**

- docs: Consolidate testing in 05-testing/
- docs(glossary): Expand glossary with all terms
- docs(specs): Formalize Business Rules event-reordering

---

## [1.2.2] - 2025-11-10

### Added

#### **Structured Logging System - Sprint 1.3**

**Logging Module:**

- `cli/src/timeblock/utils/logger.py` (118 lines)
  - `setup_logger()` with rotating file handler
  - `get_logger()` helper to obtain configured logger
  - `disable_logging()` / `enable_logging()` for tests
  - Structured format: `[timestamp] [level] [module] message`
  - Console and file support with automatic rotation (10MB, 5 backups)

**Logging Tests:**

- `cli/tests/unit/test_utils/test_logger.py` (277 lines)
- TestSetupLogger: 6+ configuration tests
- TestGetLogger: logger obtaining tests
- TestDisableEnableLogging: control tests
- 100% coverage of logger module

**Integration:**

- Structured logs in main services
- Configurable levels: DEBUG, INFO, WARNING, ERROR
- Automatic log rotation to prevent uncontrolled growth

**Metrics:**

- 6+ new tests (all passing)
- Complete and documented module
- Production ready

**Commits:**

- feat(logging): Implement structured logging system
- test(logging): Add 6 tests for logger.py
- docs(logging): Document usage and configuration

---

## [1.2.1] - 2025-11-11

### Added

#### **Documentation Reorganization and Consolidation**

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
- Better documentation site navigability
- Project philosophy and principles documented

**Commits:**

- docs(mkdocs): Add 9 missing ADRs to navigation (8b88b7b)
- docs: Consolidate architecture in 01-architecture/ (f3fcb5f)
- docs: Remove duplications and organize structure

---

## [1.1.0] - 2025-11-01

### Added

#### **Event Reordering System - Complete Implementation**

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

### Fixed

- None (no bug fixes, this is a feature-only release)

### Breaking Changes

- None

### Performance

- Conflict detection optimized for O(n log n) complexity
- Efficient event queries in date ranges

### Migration Guide

No migration required. All changes are backward compatible.

---

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
[1.4.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.3.3...v1.4.0
[1.3.3]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.3.1...v1.3.3
[1.3.1]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.1.0...v1.2.1
[1.1.0]: https://github.com/fabiodelllima/timeblock-organizer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/fabiodelllima/timeblock-organizer/releases/tag/v1.0.0
