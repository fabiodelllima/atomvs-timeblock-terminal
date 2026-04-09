# Contributing to ATOMVS Time Planner

Thank you for your interest in contributing. This document covers environment setup, coding standards, testing practices, and the contribution workflow.

## Table of Contents

- [Development Environment](#development-environment)
- [Architecture Overview](#architecture-overview)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contribution Workflow](#contribution-workflow)
- [CI/CD Pipeline](#cicd-pipeline)
- [Reporting Issues](#reporting-issues)

## Development Environment

### Prerequisites

- Python 3.13+ (developed on 3.14)
- Git with gitflow workflow knowledge
- A terminal emulator with 256-color support (for TUI development)

### Setup

```bash
git clone https://gitlab.com/delimafabio/atomvs-timeblock-terminal.git
cd atomvs-timeblock-terminal
python3 -m venv venv
source venv/bin/activate
pip install -e ".[tui,dev]"
```

### Additional Test Dependencies

The snapshot testing tools are not included in the `[dev]` extras and must be installed separately. The `pytest` version is pinned for compatibility with `pytest-textual-snapshot` 1.1.0 on Python 3.14:

```bash
pip install "pytest-textual-snapshot>=1.1.0" "syrupy>=4.8.0" "pytest==8.4.2"
```

### Known Portability Issue

Editable installs (`pip install -e .`) compile `.pyc` files with absolute paths. If you move the project directory, tests will fail with `FileNotFoundError`. The fix is:

```bash
find . -name "__pycache__" -exec rm -rf {} +
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e ".[tui,dev]"
```

See DT-073 in `docs/reference/technical-debt.md` for details.

### Editor Configuration

The project includes `.editorconfig` for consistent formatting across editors. Key rules: 4-space indentation for Python, 2-space for YAML/JSON/HTML/CSS/JS/TS/SVG. The recommended editor setup is basedpyright in `standard` mode + ruff for linting and formatting.

## Architecture Overview

The project follows a layered architecture: CLI (Typer) and TUI (Textual) consume a shared Service Layer backed by SQLModel/SQLite. No business logic exists in the presentation layer — both interfaces call the same services. Data is stored locally following XDG Base Directory conventions (`~/.local/share/atomvs/`).

```
src/timeblock/
├── commands/       # CLI commands (Typer)
├── models/         # SQLModel ORM models
├── services/       # Business logic (shared by CLI and TUI)
├── tui/            # TUI application (Textual)
│   ├── screens/    # Screen definitions
│   ├── widgets/    # Reusable widget components
│   └── styles/     # TCSS stylesheets
├── database/       # DB engine, migrations
└── utils/          # Logger, validators, helpers
```

## Coding Standards

### Language Policy (ADR-018)

| Context                      | Language             |
| ---------------------------- | -------------------- |
| Code, filenames, comments    | EN                   |
| Commit messages              | pt-BR                |
| User-facing messages         | pt-BR                |
| Documentation (docs/)        | pt-BR                |
| BDD scenarios                | EN (Given/When/Then) |
| CONTRIBUTING.md, SECURITY.md | EN                   |
| CHANGELOG.md                 | EN                   |

### Commit Format

Conventional Commits in Brazilian Portuguese:

```
type(scope): Descrição com inicial maiúscula
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`.

Examples:

- `feat(timer): Implementa pausa e retomada do cronômetro`
- `fix(loader): Corrige DetachedInstanceError no load_tasks`
- `docs(debt): Registra DT-073 — __pycache__ portabilidade`

### Code Style

- Type hints on all public interfaces
- Docstrings explaining "why", not "what"
- CSS in `.tcss` files, never in `DEFAULT_CSS` (SRP — see ADR on TCSS modularization)
- Functions: 30–50 lines target, 100 hard limit
- Classes: 300 soft limit, 500+ triggers refactoring discussion
- Linting and formatting enforced by ruff (pre-commit + CI)

### Git Workflow

Gitflow model with protected branches:

- `develop` — integration branch, all feature branches merge here
- `main` — release branch, only receives merges from `develop`
- Feature branches: `feat/...`, `fix/...`, `docs/...`, `chore/...`
- All changes enter via MR with green pipeline
- Merges use `--no-ff` to preserve branch history
- Releases are tagged with annotated tags on `main`
- Use `git switch` and `git restore` — never `git checkout`

## Testing

### Philosophy

Tests validate Business Rules (BRs) — code adapts to tests, never the opposite. If a test fails, the code is wrong, not the test. Negative and defensive tests are formal policy (BR-TEST-002).

### Test Pyramid

```
Unit:         ~990 (74%)  — Fast, BR isolated
Integration:  ~150 (11%)  — Service + DB
BDD:             83 (6%)  — Gherkin scenarios
E2E:           ~117 (9%)  — Full CLI/TUI
─────────────────────────
TOTAL:       ~1345 tests
```

### Naming Convention

Every test references a Business Rule:

- Class: `TestBRDomainXXX`
- Method: `test_br_domain_xxx_scenario`
- Example: `TestBREvent001::test_br_event_001_detects_total_overlap`

### Running Tests

```bash
# Full suite
python -m pytest tests/ -v

# By layer
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/bdd/ -v
python -m pytest tests/e2e/ -v

# Linting and formatting
ruff check .
ruff format .

# Type checking (CI uses mypy, local dev uses basedpyright)
mypy src/timeblock --check-untyped-defs
basedpyright src/
```

### Snapshot Testing

E2E snapshot tests live in `tests/e2e/` with snapshots stored in `tests/e2e/__snapshots__/`. To update snapshots after intentional visual changes:

```bash
python -m pytest tests/e2e/test_snapshots.py --snapshot-update && \
python -m pytest tests/e2e/test_snapshots.py
```

Always run update and verify in sequence (`&&`) to catch date-sensitive drift. Test files use `App` instances (not file paths) to enable isolated test databases.

Note: `pytest-textual-snapshot` 1.1.0 has a Python 3.14 compatibility issue. A monkey-patch in `tests/e2e/conftest.py` wraps `node.reportinfo()` with `Path()` to work around it.

## Documentation

### Framework

Documentation follows the Diataxis framework with additional arc42-inspired cross-cutting directories:

```
docs/
├── tutorials/     # Step-by-step learning guides
├── guides/        # How-to guides for specific tasks
├── reference/     # Specifications, metrics, debt register
├── explanation/   # Context, rationale, analysis
├── decisions/     # ADRs (Architecture Decision Records)
└── diagrams/      # 15 Mermaid diagrams (audited against code)
```

`ROADMAP.md` lives at the project root (does not fit Diataxis categories).

### Business Rules

- Format: `BR-DOMAIN-XXX` (e.g., BR-EVENT-001, BR-HABIT-004)
- Location: `docs/reference/business-rules/`
- Every BR must exist **before** implementation begins
- Every BR must have at least one test

### Architecture Decision Records

- Format: Michael Nygard template adapted with PT-BR headers
- Location: `docs/decisions/`
- ADRs are immutable once accepted — new decisions reference superseded ADRs
- Currently 46 documented ADRs

### Technical Debt

- `docs/reference/technical-debt.md` is the Single Source of Truth (SSOT)
- Format: `DT-XXX` with severity, status, discovery date, and resolution notes
- Versioned with semver (currently v2.32.0)
- Every new debt item gets a sequential ID and must include severity and planned sprint

## Contribution Workflow

1. Create a branch from `develop` following naming conventions
2. If adding functionality: document the BR first, then write the BDD scenario if applicable
3. Write tests following TDD (RED → GREEN → REFACTOR)
4. Implement until tests pass
5. Verify locally: `python -m pytest tests/ -v && ruff check .`
6. Push — the pre-push hook runs the full test suite automatically
7. Open MR targeting `develop` — CI pipeline must pass (7 jobs)
8. After review and green pipeline, merge with `--no-ff`

### Code Review Criteria

Reviews use explicit severity levels:

- **CRITICAL:** Must fix before merge (security, data loss, broken tests)
- **WARNING:** Should fix, may be deferred with justification
- **INFO:** Suggestion for improvement, non-blocking

Each finding includes: severity, criterion violated, line reference, description, production impact, and suggested fix. Verdict: APPROVE | APPROVE WITH RESERVATIONS | REQUEST CHANGES.

## CI/CD Pipeline

The GitLab CI pipeline runs 7 jobs across 4 stages:

| Stage    | Job              | Purpose                                      |
| -------- | ---------------- | -------------------------------------------- |
| quality  | lint             | ruff check + ruff format --check             |
| test     | test:unit        | Unit tests with coverage                     |
| test     | test:integration | Integration + BDD tests (parallel via xdist) |
| test     | test:e2e         | E2E tests with coverage                      |
| test     | test:typecheck   | mypy --check-untyped-defs                    |
| coverage | coverage:report  | Combines coverage, enforces 80% threshold    |
| security | security:bandit  | SAST via Bandit                              |
| security | security:deps    | SCA via pip-audit against known CVEs         |

The pipeline runs on a custom Docker image (`Dockerfile.ci`) with all dependencies pre-installed. Both `develop` and `main` are protected — merges require a green pipeline.

GitHub serves as a mirror (via GitLab Push Mirroring) with Dependabot enabled for supply chain monitoring.

## Reporting Issues

Open an issue on GitLab with:

- Problem description
- Steps to reproduce
- Expected vs observed behavior
- ATOMVS version (`atomvs version`)
- Terminal emulator and size (for TUI issues)

For security vulnerabilities, see `SECURITY.md` — do not open public issues.
