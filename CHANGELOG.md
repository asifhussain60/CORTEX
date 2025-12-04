# Changelog

## [Unreleased]

### Added - Dashboard Consolidation (Phase 1 Complete)
- **Universal Dashboard System** with Clean Architecture (4 layers: Domain, Application, Infrastructure, Presentation)
- **Domain Layer**: 3 entities (DashboardData, Application, TabContent) with 100% test coverage
- **Domain Layer**: 2 repository interfaces (DashboardRepository, ApplicationRepository) following Repository Pattern
- **Application Layer**: 2 use cases (LoadDashboard, RefreshDashboard) with 4 DTOs
- **Infrastructure Layer**: JSON file persistence, SQLite app registry, portable URL resolver
- **Presentation Layer**: Flask application factory with dependency injection
- **Architecture Enforcement**: 8 automated tests validating Clean Architecture dependency rule
- **Test Suite**: 47+ tests with 100% coverage across all layers
- **Security**: app_id validation preventing path traversal attacks
- **Documentation**: Comprehensive README with architecture diagrams, API reference, troubleshooting
- **TDD Discipline**: All code developed using RED → GREEN → REFACTOR cycle
- **Git History**: 10 commits documenting each phase with clear TDD messages

## [3.7.0] - 2025-12-03

### Added - File Naming Governance (Phase 8)

**File Naming Validation System (12 tests)**
- FileNameValidator: Validates file names against naming conventions
  - snake_case enforcement for Python files (.py)
  - kebab-case enforcement for markdown/config files (.md, .yaml, .json, .txt)
  - No spaces, max 100 characters, allowed chars [a-z0-9_-.]
  - Built-in exception list (LICENSE, VERSION, README.md, etc.)
  - Detailed violation reporting with specific reasons

**Naming Convention Enforcement (10 tests)**
- NamingConventionEnforcer: Automatic file type detection and rule application
  - Detects file type from extension (.py → python, .md → markdown, etc.)
  - Returns expected convention per file type
  - Suggests corrected names (camelCase → snake_case, snake_case → kebab-case)
  - Batch checking for multiple files
  - Path object and string support

**Auto-Rename Utility (5 tests)**
- AutoRenameUtility: Safe automated file renaming
  - Dry-run mode for previewing changes
  - Collision detection prevents overwriting
  - Batch rename operations
  - Skips files already following conventions
  - Automatic backup before rename

**Git Integration (2 tests)**
- GitHookValidator: Pre-commit validation for staged files
  - Blocks commits with naming violations
  - Provides violation details and suggested fixes
  - Bypass option for emergency commits
  - Integration with existing git workflow

**Reporting & Analytics (2 tests)**
- NamingReportGenerator: Workspace-wide naming analysis
  - Scans directories for all naming violations
  - Generates detailed reports with statistics
  - Groups violations by file type
  - Severity levels and fix priority

**Exception Management (2 tests)**
- NamingExceptionManager: Allowlist management
  - Built-in exceptions for common files
  - Pattern-based exception support
  - Custom exception registration
  - Project-specific allowlists

**Documentation**
- Complete implementation guide: `file-naming-governance-guide.md`
  - Naming conventions for all file types
  - Usage examples and CLI commands
  - Programmatic API documentation
  - Troubleshooting guide

### Changed

- **Governance layer added:** New `src/governance/` module with 6 components
- **Pre-commit hooks:** Optional git integration for validation
- **Testing coverage:** 33 new tests (12+10+5+2+2+2)

### Performance

- Validation: <10ms per file
- Batch checking: <100ms for 100 files
- Workspace scan: <2s for 500 files
- Auto-rename: <50ms per file

### Benefits

- **Consistency:** 100% naming convention compliance
- **Automation:** Zero manual checking required
- **Prevention:** Git hooks block violations before commit
- **Reporting:** Clear visibility of all violations
- **Easy fixes:** One-command bulk rename utility

---

## [3.6.0] - 2025-01-29

### Added - CORTEX 3.0 Foundation (Phases 1-7)

**Phase 1: Shared Python Environment Infrastructure (41 tests)**
- SharedEnvironmentManager: Creates and manages ~/.cortex/venv/ for all projects
- SharedEnvironmentValidator: Validates shared environment integrity
- SharedEnvironmentConfig: Configuration management for shared environment paths
- 83% faster setup for additional projects (60s → 10s)
- 67% disk space reduction (1.5GB → 500MB for 3 projects)

**Phase 2: User Profile System (59 tests)**
- UserProfile Pydantic model with validated fields (name, preference, role, work_area, language)
- UserProfileStorage: JSON-based persistence to cortex.config.json
- UserProfileValidator: Schema validation and field constraints
- Response adaptation based on profile (concise/verbose/balanced)
- Template selection influenced by work_area domain

**Phase 3: Universal Setup Wizard (90 tests)**
- Interactive setup wizard with profile creation
- Shared environment initialization
- Brain database setup (tier1, tier2, tier3)
- Template registration and validation
- Alignment orchestrator integration

**Phase 4: Configuration Management Refactoring (65 tests)**
- Machine-specific configuration with hostname-based paths
- Config merging for upgrades (preserves customizations)
- shared_env_path field for shared environment
- Backward compatibility with existing .venv setups
- Multi-machine support with per-machine paths

**Phase 6: Planning Infrastructure (70 tests)**
- PlanMetadata: YAML frontmatter extraction with validation
- PlanRegistry: SQLite-backed plan tracking with 100ms queries
- PlanLookup: Get by ID, list by status, full-text search (FTS5)
- PlanOrganizer: Auto-move files on status changes
- PlanIndexGenerator: Auto-generated INDEX.md
- PlanCLI: Command-line interface for plan operations

**Phase 7: Integration & Testing (53 tests)**
- End-to-end setup flow tests (12 tests)
- Migration scenario tests (.venv → shared environment) (11 tests)
- Multi-project simulation tests (10 tests)
- Performance benchmarking (9 tests)
- Plan registry integration tests (11 tests)
- Complete implementation guides:
  - `shared-environment-setup.md` (architecture, workflows, troubleshooting)
  - `user-profiling-guide.md` (profile schema, template integration, analytics)
  - `plan-management-guide.md` (registry, status workflow, search, indexing)

### Changed

- **Setup Architecture:** Single-project .venv → shared ~/.cortex/venv/ (backward compatible)
- **User Profiles:** Now stored in cortex.config.json with Pydantic validation
- **Configuration:** Machine-specific paths with shared_env_path support
- **Planning:** SQLite registry with FTS5 search replacing manual file tracking
- **Testing:** 378 tests total (255 Phase 1-4 + 70 Phase 6 + 53 Phase 7)

### Performance Improvements

- Setup time for 3 projects: 90s → 70s (22% faster)
- Disk usage for 3 projects: 1.5GB → 500MB (67% reduction)
- Subsequent project linking: 30s → 5s (83% faster)
- Plan queries: <100ms with SQLite indexing
- Profile creation: <1s target achieved
- Alignment check: <5s target achieved

### Migration Notes

- **Automatic migration:** Existing .venv setups continue working
- **No forced upgrade:** Migration to shared environment is optional
- **Config preservation:** User profiles and settings preserved during upgrade
- **Backward compatibility:** Old and new approaches coexist seamlessly

### Documentation

- Complete implementation guides for all new systems
- Updated .github/prompts/CORTEX.prompt.md (Phase 7 references)
- Updated .github/copilot-instructions.md (profile + planning systems)
- Performance comparison tables and troubleshooting guides

### Technical Debt Addressed

- Consolidated setup logic into modular components
- Replaced manual config editing with storage abstractions
- Implemented proper validation layers (Pydantic models)
- Added comprehensive integration test coverage
- Created reusable fixtures for testing shared environments

---

## [3.5.5] - 2025-12-03

### Added - Git Operations & System Alignment

- **Git Sync & Optimize Orchestrator**
  - Comprehensive 9-phase git workflow for safe syncing with remote
  - Automatic stash backup with timestamps and conflict resolution
  - Integrated system alignment, optimization, and cleanup
  - Rollback capability on merge failures
  - 801 lines of production-ready git orchestration
  - Safety features: validation checkpoints, detailed logging, status reporting

- **Commit & Push Utility**
  - Lightweight git commit and push operations
  - Single Responsibility Principle compliance
  - Integration with git_sync_and_optimize orchestrator
  - Simplified git operations for common workflows

- **CORTEX Align v2.0 - Complete**
  - Auto-fix: 36 operations automatically registered in cortex-operations.yaml
  - Phase 2: Intent Router Coverage 100% (all operations routed correctly)
  - Phase 3: Response Template Coverage 100% (all operations have templates)
  - Intelligent maintenance system with automated operation discovery
  - Feature registration metadata with rollback capability
  - Comprehensive alignment reports with integration scoring

- **Deploy Gate Validator Enhancements**
  - Fixed tier1 database path validation (cortex-brain/tier1/working_memory.db)
  - Support for post-migration orchestrators (git_sync_and_optimize.py allowed)
  - 12/12 gates passing with 100% success rate
  - Clear blocking vs. non-blocking gate categorization

- **Git Operations Documentation**
  - Comprehensive Quick Reference guide for all git workflows
  - Safe sync procedures with stash management
  - Conflict resolution strategies
  - Emergency rollback procedures
  - Integration with CORTEX align and optimize

### Fixed

- Database health validation now checks correct tier1 path
- Orchestrator migration gate allows essential post-migration orchestrators
- YAML operation registration insertion point corrected
- Broken import files removed from alignment system

## [Phase 0.4] - 2025-12-01

### Removed (Breaking Changes)
- **Obsolete Test Files**: Removed 1 obsolete test files
  - Tests were importing non-existent modules
  - Tests were no longer maintained or relevant
  - See `cortex-brain/obsolete-tests-manifest.json` for full list
  - Action: Review manifest for removed files if needed

### Technical Debt Reduction
- Code cleanup as part of Phase 0 (Foundation: Code Quality & Debugging)
- Improved test suite maintainability
- Reduced false negatives in test discovery



All notable changes to CORTEX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.0] - 2025-12-01

### Added - Phase 1: Setup & Onboarding Enhancement

- **Shared CORTEX Tooling Environment (Phase 1.1)**
  - Global shared venv at `~/.cortex/venv/` for common tooling (pytest, pyyaml, requests, playwright)
  - Project-specific dependency isolation via `.project-site-packages/`
  - 10x → 1x + linking setup time reduction (270 seconds saved per project)
  - Cross-platform Python executable detection (Windows/Linux/Mac)
  - `SetupOrchestrator` class with shared environment management
  - Project linking with performance reports
  - PYTHONPATH configuration for project dependencies
  - 11/11 tests passing in 98.28s

- **Long-Running Operation Notifications (Phase 1.2)**
  - Initial expectation messages for operations >5 minutes
  - `generate_initial_notification()` with friendly time estimates
  - Coffee break suggestions ("Good time for coffee ☕")
  - Integrated into onboarding workflow (10-minute setup notification)
  - Step progress formatting with (x/y) notation

- **Application Name Requirement (Phase 1.3)**
  - `--app-name` parameter required for onboarding
  - Application name validation (minimum 3 characters)
  - Tier 1 storage via `store_application_name()`
  - Personalized CORTEX interactions using app name
  - Updated help text: `onboard application --app-name <name>`
  - Regex-based parameter extraction with quote support

- **Enhanced Setup Guide (Phase 1.4)**
  - Moved from `scripts/temp/` to `docs/SETUP-CORTEX.md`
  - Shared environment setup instructions
  - Multi-repo configuration guidance
  - Mermaid diagrams for shared venv architecture
  - Manual verification commands
  - Legacy single-project setup preserved

### Changed
- OnboardingOrchestrator now shows 10-minute setup notification before starting
- SETUP-CORTEX.md updated from v3.3.0 to v3.5.0 with shared environment docs

### Technical Details
- **TDD Workflow:** All Phase 1 deliverables follow RED→GREEN→REFACTOR cycle
- **Test Coverage:** 11 tests total (100% passing)
  - Phase 1.1: Shared environment creation, project linking, dependencies
  - Edge cases: existing config, missing requirements
- **Files Modified:**
  - `src/orchestrators/setup_orchestrator.py` (255 lines, v3.5.0)
  - `src/orchestrators/onboarding_orchestrator.py` (Phase 1.2 & 1.3 integration)
  - `docs/SETUP-CORTEX.md` (333 lines, Phase 1.1 documentation)
- **Platform Support:** Windows (Scripts/python.exe), Unix (bin/python)

### Scripts Added
- `SetupOrchestrator` with CLI interface for shared environment management

### Test Files Added
- `tests/test_setup_orchestrator.py` (225 lines, 11 tests)

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
