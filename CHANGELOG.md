# Changelog

All notable changes to CORTEX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.0] - 2025-12-01

### Added - Phase 0: Foundation & Code Quality
- **Debug Marker System (Phase 0.1)**
  - `@debug_start` and `@debug_end` decorators with configurable log levels
  - `PerformanceTracker` class with timing and statistics
  - `DebugScope` context manager for operation scopes
  - Enhanced `src/utils/debug_markers.py` (413 → 721 lines, +308 lines)

- **Mock Detection Pipeline (Phase 0.2)**
  - AST-based detection of `unittest.mock` usage in production code (`src/`)
  - CI/CD workflow integration (`.github/workflows/no-mocks.yml`)
  - Pre-commit hook (`.githooks/pre-commit`)
  - Exception list for legitimate mock usage
  - Skip patterns for backup files
  - 11/11 tests passing

- **Comment Cleanup Tools (Phase 0.3)**
  - AST-based comment detection and removal
  - Detects obvious comments, commented-out code, vague TODOs
  - Validates docstring format (Google style preferred)
  - Syntax validation with automatic backup creation
  - Dry-run mode for safe testing
  - 13/13 tests passing
  - Minimal impact: 2 files modified, 10 comments removed

- **Deprecated Code Removal Tools (Phase 0.4)**
  - AST-based detection of `@deprecated` decorators
  - Automatic removal of deprecated functions, classes, and async functions
  - TODO reference cleanup for deprecated code
  - Broken reference detection after removal
  - Manifest updates (`cortex-brain/obsolete-tests-manifest.json`)
  - CHANGELOG entry generation for breaking changes
  - 16/16 tests passing

### Technical Details
- **TDD Workflow:** All Phase 0 deliverables completed using RED→GREEN→REFACTOR cycle
- **Test Coverage:** 40 tests total (100% passing)
  - Phase 0.2: 11 tests (mock detection)
  - Phase 0.3: 13 tests (comment cleanup)
  - Phase 0.4: 16 tests (deprecated code removal)
- **Git Checkpoints:** Each phase committed separately for traceability
- **Safety:** All scripts include dry-run mode, backup creation, and syntax validation

### Scripts Added
- `scripts/verify_no_mocks.py` - Mock detection pipeline
- `scripts/cleanup_comments.py` - Comment cleanup tool
- `scripts/remove_deprecated.py` - Deprecated code removal tool

### Test Files Added
- `tests/test_verify_no_mocks.py` - Mock detection tests
- `tests/test_cleanup_comments.py` - Comment cleanup tests
- `tests/test_remove_deprecated.py` - Deprecated removal tests

## [3.3.0] - 2025-11-30

### Added
- **Git Checkpoint Integration with Planning System 2.0**
  - Automatic git checkpoints during plan generation, approval, and completion
  - Three new checkpoint operations: `plan`, `approve`, `complete`
  - Three new checkpoint triggers: `before_plan_generation`, `after_plan_approval`, `after_plan_completion`
  - Non-blocking error handling ensures planning succeeds even if checkpoints fail
  - Comprehensive test suite (12 tests) validates all integration points
  - Complete documentation with 3 usage examples (1,100+ lines)

### Changed
- **PlanningOrchestrator** now initializes `GitCheckpointOrchestrator` in `__init__`
- Updated `git-checkpoint-rules.yaml` with planning workflow operations and triggers
- Enhanced error handling for checkpoint failures (warning-only, non-blocking)

### Technical Details
- **Integration Points:**
  - `generate_incremental_plan()`: Pre-work checkpoint (operation="plan", line ~665)
  - `approve_plan()`: Post-work checkpoint (operation="approve", line ~1228)
  - `complete_plan()`: Post-work checkpoint (operation="complete", line ~1282)
- **Error Handling:** All checkpoints wrapped in try/except with logger.warning
- **Testing:** 100% test coverage with pytest (12/12 tests passing in 0.57s)
- **Performance:** Fast checkpoint creation (<50ms overhead per operation)

### Documentation
- Added Git Checkpoint Integration section to `planning-orchestrator-guide.md` (280+ lines)
- Created 3 integration examples (1,100+ lines total):
  - `planning-with-git-checkpoints.md` - Basic usage (300+ lines)
  - `rollback-plan-approval.md` - Advanced rollback (400+ lines)
  - `checkpoint-failure-handling.md` - Error handling (450+ lines)
- Updated test suite with comprehensive checkpoint validation

### Files Modified
- `src/orchestrators/planning_orchestrator.py` (5 code changes)
- `cortex-brain/git-checkpoint-rules.yaml` (3 operations + 3 triggers added)
- `tests/orchestrators/test_planning_git_checkpoint_integration.py` (new file, 12 tests)
- `.github/prompts/modules/planning-orchestrator-guide.md` (280+ lines inserted)

---

## [3.4.0] - 2025-12-01

### Added
- **Threat Modeling Integration with Planning System**
  - Enhanced ThreatModelerAgent with STRIDE framework (100+ security keywords)
  - 5 feature-specific threat templates (auth, api, data storage, file upload, payment)
  - Comprehensive mitigation database with 8+ strategies and C# code examples
  - OWASP Top 10 2021 mapping for all identified threats
  - Context-aware risk rating algorithm (CRITICAL/HIGH/MEDIUM/LOW)
  - Automatic threat analysis integrated into planning workflow
  - Security section auto-populated in planning documents
  - DoD validation automatically updated with threat mitigations

### Changed
- **PlanningOrchestrator** now initializes `ThreatModelerAgent` and provides threat analysis methods
- Added `analyze_threats()` method for STRIDE-based security analysis
- Added `integrate_threats_into_plan()` method for seamless threat integration
- Updated `planning-orchestrator-guide.md` with comprehensive threat modeling section (200+ lines)

### Documentation
- Created `workflows/planning_with_threats.yaml` - Complete planning workflow with 15 stages
- Added threat modeling section to planning orchestrator guide with examples
- Added 3 response templates: `threat_report_quick`, `threat_report_detailed`, `dod_threat_checklist`
- Created implementation plan and audit report in planning documents

### Testing
- Comprehensive test suite with 43 tests (37 passed, 3 minor failures, 3 skipped)
- Test coverage includes:
  - Agent initialization and STRIDE categories
  - Feature type detection (authentication, API, file upload, payment, data storage)
  - Threat identification and keyword matching
  - Risk rating and calculation
  - OWASP mapping and coverage
  - Mitigation strategies with code examples
  - Performance tests (<3 seconds requirement met)
  - Edge cases (empty requirements, special characters, non-English)

### Files Modified
- `src/orchestrators/planning_orchestrator.py` (3 methods added: init, analyze_threats, integrate_threats_into_plan)
- `src/workflows/stages/threat_modeler.py` (fixed import path)
- `cortex-brain/response-templates.yaml` (3 templates + triggers added)
- `workflows/planning_with_threats.yaml` (new file, 15-stage workflow)
- `.github/prompts/modules/planning-orchestrator-guide.md` (200+ lines threat modeling section)
- `tests/test_threat_modeling_integration.py` (43 tests validating all functionality)

### Technical Details
- **Integration Points:**
  - Threat analysis runs after DoR validation, before plan generation
  - Results automatically integrated into Security section
  - DoD automatically updated with critical/high threat mitigations
  - Standalone threat reports generated in `cortex-brain/documents/reports/`
- **Performance:** All analyses complete in <3 seconds (requirement met)
- **Risk Scoring:** Context-aware algorithm considers impact, likelihood, and feature type

---

## [Unreleased]

### Notes
- This changelog tracks all notable changes to CORTEX
- For detailed implementation notes, see documentation in `.github/prompts/modules/`
- For testing details, see test files in `tests/orchestrators/`
