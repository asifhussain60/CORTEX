# PowerShell Automation Scripts - Feature Inventory

**Source System:** KDS v8  
**Target System:** CORTEX v1.0  
**Component:** PowerShell Automation Scripts  
**Date Extracted:** 2025-11-05  
**Status:** Complete Feature List  

---

## 📊 Overview

**Purpose:** Automation scripts that enable KDS functionality, TDD workflows, BRAIN management, and system monitoring.

**KDS v8 Implementation:**
- Total Scripts: 45+ PowerShell scripts
- Organization: Hemisphere-separated (`left-brain/`, `right-brain/`, `corpus-callosum/`)
- Architecture: Modular, reusable, event-driven
- Location: `KDS/scripts/`

**CORTEX v1.0 Design:**
- Language: Python (replacing PowerShell)
- Organization: Same hemisphere structure preserved
- Architecture: Object-oriented with interfaces
- Location: `cortex/scripts/`

---

## 📁 Script Categories

### Category 1: LEFT BRAIN Scripts (Tactical Execution)
**Location:** `scripts/left-brain/`  
**Purpose:** TDD automation, test execution, code implementation  
**Count:** 12 scripts

### Category 2: RIGHT BRAIN Scripts (Strategic Planning)
**Location:** `scripts/right-brain/`  
**Purpose:** Pattern matching, workflow generation, similarity analysis  
**Count:** 7 scripts

### Category 3: CORPUS CALLOSUM Scripts (Coordination)
**Location:** `scripts/corpus-callosum/`  
**Purpose:** Message passing, feedback loops, optimization  
**Count:** 8+ scripts

### Category 4: CRAWLERS (BRAIN Feeding)
**Location:** `scripts/crawlers/`  
**Purpose:** Codebase analysis, multi-threaded crawling  
**Count:** 7 scripts

### Category 5: BRAIN Management
**Location:** `scripts/` (root)  
**Purpose:** BRAIN updates, health monitoring, data collection  
**Count:** 10+ scripts

### Category 6: System Utilities
**Location:** `scripts/` (root)  
**Purpose:** Setup, validation, maintenance, reporting  
**Count:** 8+ scripts

---

## 🔴 Category 1: LEFT BRAIN Scripts (Tactical - 12 scripts)

### Script 1.1: TDD Cycle Orchestrator
**File:** `left-brain/run-tdd-cycle.ps1` (~217 lines)

**Purpose:** Master script that coordinates complete RED→GREEN→REFACTOR TDD cycle

**Features:**
```powershell
Features:
  - Load feature configuration (YAML)
  - Execute RED phase (create-tests.ps1)
  - Execute GREEN phase (implement-code.ps1)
  - Execute REFACTOR phase (refactor-code.ps1)
  - Automatic rollback on failure
  - Coordination messages to RIGHT brain
  - Duration tracking
  - Phase logging to execution-state.jsonl
```

**Input:**
```yaml
# Feature config YAML
feature_name: "PDF Export Button"
files_to_create:
  - "PdfService.cs"
  - "PdfServiceTests.cs"
tests_to_create:
  - "PdfServiceTests.cs"
```

**Output:**
```json
{
  "success": true,
  "duration_seconds": 84,
  "phases_completed": ["RED", "GREEN", "REFACTOR"],
  "all_tests_passing": true
}
```

**CORTEX Migration:**
- Python `TDDOrchestrator` class
- Async phase execution
- SQLite state tracking

---

### Script 1.2: Test Creation (RED Phase)
**File:** `left-brain/create-tests.ps1`

**Purpose:** Automate test creation before implementation (RED phase)

**Features:**
```powershell
Features:
  - Parse feature config YAML
  - Generate test file structure
  - Create failing tests (RED state expected)
  - Log RED phase events
  - Return test file paths
```

**CORTEX Migration:**
- Python `TestCreator` class
- Jinja2 templates for test generation
- Pytest/Playwright test frameworks

---

### Script 1.3: Code Implementation (GREEN Phase)
**File:** `left-brain/implement-code.ps1`

**Purpose:** Implement minimal code to make tests pass (GREEN phase)

**Features:**
```powershell
Features:
  - Parse feature config
  - Create implementation files
  - Run tests to verify GREEN
  - Log GREEN phase events
  - Rollback if tests don't pass
```

**CORTEX Migration:**
- Python `CodeImplementer` class
- AST-based code generation
- Automatic syntax validation

---

### Script 1.4: Code Refactoring (REFACTOR Phase)
**File:** `left-brain/refactor-code.ps1`

**Purpose:** Optimize code while keeping tests green (REFACTOR phase)

**Features:**
```powershell
Features:
  - Apply refactoring patterns
  - Verify tests still pass
  - Log REFACTOR phase events
  - Rollback if tests break
```

**CORTEX Migration:**
- Python `CodeRefactorer` class
- Automated refactoring patterns (extract method, rename, etc.)
- Safety checks (tests must stay green)

---

### Script 1.5: Test Execution
**File:** `left-brain/execute-tests.ps1`

**Purpose:** Execute tests and capture results (framework-agnostic)

**Features:**
```powershell
Supported:
  - PowerShell tests (.ps1)
  - Playwright tests (.spec.ts)
  - xUnit tests (.cs)
  - Pytest tests (.py)

Returns:
  - Pass/fail status
  - Output logs
  - Duration
  - Error details (if failed)
```

**CORTEX Migration:**
- Python `TestRunner` interface
- Plugin architecture for frameworks
- Unified result format

---

### Script 1.6-1.12: Phase Verification Scripts
**Files:**
- `verify-red-phase.ps1` - Verify tests fail initially
- `verify-green-phase.ps1` - Verify tests pass after implementation
- `verify-refactor-safety.ps1` - Verify tests still pass after refactor
- `rollback-changes.ps1` - Rollback to last known good state
- `validate-implementation.ps1` - Full validation suite
- `quality-checks.ps1` - Code quality validation (linting, formatting)
- `auto-test-runner.ps1` - Automatic test runner (watch mode)

**CORTEX Migration:** All become methods in Python `TDDOrchestrator` class

---

## 🟢 Category 2: RIGHT BRAIN Scripts (Strategic - 7 scripts)

### Script 2.1: Pattern Matcher
**File:** `right-brain/match-pattern.ps1`

**Purpose:** Match user request to learned workflow patterns

**Features:**
```powershell
Features:
  - Query knowledge-graph.yaml for patterns
  - Fuzzy text matching
  - Confidence scoring
  - Return best match pattern
```

**Input:**
```powershell
.\match-pattern.ps1 -Request "Add PDF export feature"
```

**Output:**
```yaml
pattern_id: "export_feature_workflow"
confidence: 0.92
phases: 4
estimated_hours: 6.5
```

**CORTEX Migration:**
- Python `PatternMatcher` class
- SQLite FTS5 semantic search
- Enhanced confidence algorithms

---

### Script 2.2: Pattern Extractor
**File:** `right-brain/extract-pattern.ps1`

**Purpose:** Extract reusable pattern from completed work

**Features:**
```powershell
Features:
  - Load completed session history
  - Identify reusable components
  - Extract phase structure
  - Calculate success metrics
  - Store as workflow pattern
```

**CORTEX Migration:**
- Python `PatternExtractor` class
- Automatic pattern abstraction
- Pattern consolidation (merge similar)

---

### Script 2.3: Pattern Creator
**File:** `right-brain/create-pattern.ps1`

**Purpose:** Create new workflow pattern from template

**Features:**
```powershell
Features:
  - Define pattern structure
  - Specify phases and tasks
  - Set success criteria
  - Generate YAML pattern file
```

**CORTEX Migration:**
- Python `PatternCreator` class
- Template system
- Validation rules

---

### Script 2.4: Workflow Template Generator
**File:** `right-brain/generate-workflow-template.ps1`

**Purpose:** Generate workflow from pattern library

**Features:**
```powershell
Features:
  - Query pattern library
  - Adapt pattern to current context
  - Generate session plan
  - Include task estimates
```

**CORTEX Migration:**
- Python `WorkflowGenerator` class
- Context-aware adaptation
- Tier 3 estimates integration

---

### Script 2.5-2.7: Pattern Management
**Files:**
- `update-pattern-library.ps1` - Add/update patterns in library
- `validate-workflow-template.ps1` - Validate pattern structure
- `analyze-similarity.ps1` - Find similar patterns for consolidation

**CORTEX Migration:** All become methods in Python `PatternManager` class

---

## 🌉 Category 3: CORPUS CALLOSUM Scripts (Coordination - 8 scripts)

### Script 3.1: Execution Metrics Collector
**File:** `corpus-callosum/collect-execution-metrics.ps1`

**Purpose:** Gather metrics from LEFT brain execution for RIGHT brain optimization

**Features:**
```powershell
Collects:
  - Phase durations
  - Test results (pass/fail)
  - TDD effectiveness (cycles needed)
  - Files modified count
  - Success indicators
```

**Output:**
```json
{
  "session_id": "20251105-export-pdf",
  "phase_durations": {"phase_1": 300, "phase_2": 450},
  "test_results": {"total": 15, "passed": 15},
  "tdd_effectiveness": {"followed": true, "cycles_needed": 1}
}
```

**CORTEX Migration:**
- Python `MetricsCollector` class
- Real-time metrics streaming
- SQLite storage

---

### Script 3.2: Execution Feedback Processor
**File:** `corpus-callosum/process-execution-feedback.ps1`

**Purpose:** Analyze execution metrics and generate optimization suggestions

**Features:**
```powershell
Analysis:
  - Slow phase detection (>10 min = warning)
  - TDD compliance validation
  - Test coverage analysis
  - Performance anomalies
  
Generates:
  - Optimization suggestions
  - Process improvements
  - Warnings for RIGHT brain
```

**CORTEX Migration:**
- Python `FeedbackProcessor` class
- Machine learning for anomaly detection
- Pattern-based suggestions

---

### Script 3.3: Plan Optimizer
**File:** `corpus-callosum/optimize-plan-from-metrics.ps1`

**Purpose:** Optimize future plans based on execution feedback

**Features:**
```powershell
Optimizations:
  - Adjust task time estimates
  - Reorder phases for efficiency
  - Suggest parallel execution
  - Identify TDD workflow improvements
```

**CORTEX Migration:**
- Python `PlanOptimizer` class
- Historical data analysis
- Predictive adjustments

---

### Script 3.4-3.8: Coordination Scripts
**Files:**
- `send-feedback-to-right.ps1` - Send LEFT→RIGHT messages
- `collect-brain-metrics.ps1` - Overall BRAIN performance metrics
- `predict-issues.ps1` - Proactive issue prediction
- `suggest-preventive-actions.ps1` - Preventive recommendations
- `send-message.ps1` - Generic message passing

**CORTEX Migration:** All become methods in Python `AgentOrchestrator` class

---

## 🕷️ Category 4: CRAWLERS (BRAIN Feeding - 7 scripts)

### Script 4.1: Multi-Threaded Orchestrator
**File:** `crawlers/orchestrator.ps1` (~300 lines)

**Purpose:** Coordinate 5 parallel area-specific crawlers for fast BRAIN feeding

**Features:**
```powershell
Parallel Crawlers:
  - UI Crawler (Blazor components, pages)
  - API Crawler (Controllers, endpoints)
  - Service Crawler (Services, business logic)
  - Test Crawler (Test frameworks, patterns)
  - Database Crawler (DbContext, entities)

Performance:
  - Target: <5 min for 1000+ files
  - 60% faster than single-threaded
  - Real-time progress display
```

**Architecture:**
```powershell
Start-Job: ui-crawler.ps1
Start-Job: api-crawler.ps1
Start-Job: service-crawler.ps1
Start-Job: test-crawler.ps1
Start-Job: database-crawler.ps1

Wait-Job (all 5 jobs)

Collect results → feed-brain.ps1
```

**CORTEX Migration:**
- Python `CrawlerOrchestrator` class
- Async/await for parallelization
- Progress bars (tqdm)

---

### Script 4.2: UI Crawler
**File:** `crawlers/ui-crawler.ps1`

**Purpose:** Discover UI components, pages, styles

**Features:**
```powershell
Discovers:
  - Blazor components (.razor)
  - Pages and layouts
  - CSS/SCSS files
  - JavaScript/TypeScript
  - Element selectors (data-testid, id)
```

**CORTEX Migration:**
- Python `UICrawler` class
- BeautifulSoup for HTML parsing
- Regex for selector extraction

---

### Script 4.3: API Crawler
**File:** `crawlers/api-crawler.ps1`

**Purpose:** Discover API controllers, endpoints, routes

**Features:**
```powershell
Discovers:
  - Controllers (.cs)
  - HTTP methods (GET, POST, etc.)
  - Route patterns
  - Request/Response DTOs
```

**CORTEX Migration:**
- Python `APICrawler` class
- AST parsing for C#
- OpenAPI schema generation

---

### Script 4.4: Service Crawler
**File:** `crawlers/service-crawler.ps1`

**Purpose:** Discover services, business logic, DI patterns

**Features:**
```powershell
Discovers:
  - Service interfaces (I*Service.cs)
  - Service implementations
  - Dependency injection patterns
  - Constructor parameters
```

**CORTEX Migration:**
- Python `ServiceCrawler` class
- Dependency graph generation

---

### Script 4.5: Test Crawler
**File:** `crawlers/test-crawler.ps1`

**Purpose:** Discover test patterns, frameworks, coverage

**Features:**
```powershell
Discovers:
  - Test frameworks (Playwright, xUnit, Jest)
  - Test patterns (unit, integration, E2E)
  - Selector strategies (ID, text, data-testid)
  - Test data (fixtures, tokens)
```

**CORTEX Migration:**
- Python `TestCrawler` class
- Coverage report parsing

---

### Script 4.6: Database Crawler
**File:** `crawlers/database-crawler.ps1`

**Purpose:** Discover database schema, entities, migrations

**Features:**
```powershell
Discovers:
  - DbContext classes
  - Entity models
  - Migration files
  - Database relationships
```

**CORTEX Migration:**
- Python `DatabaseCrawler` class
- SQL schema analysis

---

### Script 4.7: BRAIN Feeder
**File:** `crawlers/feed-brain.ps1`

**Purpose:** Aggregate crawler results and update BRAIN storage

**Features:**
```powershell
Updates:
  - file-relationships.yaml
  - test-patterns.yaml
  - architectural-patterns.yaml
  - knowledge-graph.yaml
  
Process:
  - Merge crawler results
  - Deduplicate patterns
  - Calculate confidence scores
  - Update YAML files
```

**CORTEX Migration:**
- Python `BrainFeeder` class
- SQLite batch inserts
- Transaction safety

---

## 🧠 Category 5: BRAIN Management (10 scripts)

### Script 5.1: Auto BRAIN Updater
**File:** `auto-brain-updater.ps1`

**Purpose:** Automatic BRAIN updates triggered by event thresholds

**Features:**
```powershell
Triggers:
  - 50+ events accumulated
  - 24 hours since last update
  - Manual force flag

Process:
  - Call brain-updater.md agent
  - Process events → knowledge-graph.yaml
  - Trigger Tier 3 collection (if >1 hour)
  - Log update event
```

**CORTEX Migration:**
- Python `AutoBrainUpdater` class
- Scheduled task (cron/systemd)
- Event-driven triggers

---

### Script 5.2: Development Context Collector
**File:** `collect-development-context.ps1` (~500 lines)

**Purpose:** Collect Tier 3 metrics (git, test, build, work patterns)

**Features:**
```powershell
Collects:
  - Git activity (commits, churn, velocity)
  - Code changes (lines added/deleted)
  - Test metrics (pass rates, flaky tests)
  - KDS usage (intent distribution)
  - Work patterns (productive times)
  - Correlations (commit size vs success)

Performance:
  - Target: <10 seconds
  - Delta collection (incremental)
  - Error handling (graceful degradation)
```

**CORTEX Migration:**
- Python `ContextCollector` class
- Multiple collector plugins
- SQLite time-series storage

---

### Script 5.3: BRAIN Amnesia
**File:** `brain-amnesia.ps1`

**Purpose:** Remove application-specific data (reset BRAIN to transferable state)

**Features:**
```powershell
Preserves:
  - Tier 0 (governance rules)
  - Tier 2 patterns (transferable)

Removes:
  - Tier 1 (conversations - app-specific)
  - Tier 3 (metrics - app-specific)
  - Sessions (app-specific)
```

**CORTEX Migration:**
- Python `BrainAmnesia` class
- Selective reset
- Backup before amnesia

---

### Script 5.4: BRAIN Reset
**File:** `brain-reset.ps1`

**Purpose:** Complete BRAIN reset to initial state

**CORTEX Migration:**
- Python `BrainReset` class
- Factory reset functionality

---

### Script 5.5: BRAIN Crawler
**File:** `brain-crawler.ps1` (standalone, not orchestrator)

**Purpose:** Comprehensive codebase analysis (Google-style crawler)

**Modes:**
```powershell
Modes:
  - quick: Fast scan (UI + Test only)
  - deep: Full analysis (all areas)
  - incremental: Only changed files
  - targeted: Specific path/workspace
```

**CORTEX Migration:**
- Python `BrainCrawler` class
- Multi-mode support
- Progress reporting

---

### Script 5.6-5.10: BRAIN Utilities
**Files:**
- `populate-kds-brain.ps1` - Initial BRAIN population
- `monitor-tier1-health.ps1` - STM health monitoring
- `tier1-health-report.ps1` - Detailed STM reports
- `conversation-stm.ps1` - Conversation storage (Tier 1)
- `record-session-conversation.ps1` - Manual conversation recording

**CORTEX Migration:** All integrated into Python `BrainManager` class

---

## 🛠️ Category 6: System Utilities (8 scripts)

### Script 6.1: Setup KDS Tooling
**File:** `setup-kds-tooling.ps1` (~400 lines)

**Purpose:** Automatic setup of all development dependencies

**Features:**
```powershell
Installs:
  - Node.js packages (18): Playwright, Percy, ESLint, TypeScript
  - .NET packages (3): Analyzers, StyleCop
  - Playwright browsers (Chromium, Firefox, WebKit)

Detects:
  - Project type (.NET, Node.js, Python, Java)
  - Existing packages (skip if already installed)
  - Core dependencies (Git, PowerShell, Node, .NET)

Validates:
  - Config files present
  - Versions correct
  - Test frameworks functional
```

**CORTEX Migration:**
- Python `SetupCORTEX` script
- Package manager abstractions (pip, npm, dotnet)
- Cross-platform support

---

### Script 6.2: Commit Validation
**File:** `validate-commit.ps1`

**Purpose:** Pre-commit validation (git hook)

**Features:**
```powershell
Validates:
  - Semantic commit message (feat/fix/test/docs)
  - Zero errors/warnings (DoD)
  - All tests passing
  - BRAIN state files not committed
```

**CORTEX Migration:**
- Python `CommitValidator` class
- Git hook integration
- Fast validation (<5 seconds)

---

### Script 6.3: System Health Verifier
**File:** `verify-system-health.ps1`

**Purpose:** Comprehensive system health check

**Features:**
```powershell
Checks:
  - BRAIN files integrity
  - Event log health
  - Session state validity
  - Script availability
  - Git repository health
```

**CORTEX Migration:**
- Python `HealthVerifier` class
- Health dashboard integration

---

### Script 6.4-6.8: Additional Utilities
**Files:**
- `generate-metrics-report.ps1` - Metrics dashboard generation
- `launch-dashboard.ps1` - WPF dashboard launcher
- `run-health-checks.ps1` - Automated health monitoring
- `run-maintenance.ps1` - Periodic maintenance tasks
- `backup-kds.ps1` - BRAIN backup utility

**CORTEX Migration:** All integrated into Python utility classes

---

## 📊 Complete Script Summary

| Category | Scripts | KDS LOC | CORTEX LOC | Migration Approach |
|----------|---------|---------|------------|-------------------|
| LEFT BRAIN | 12 | ~1,500 | ~800 | `TDDOrchestrator` + helpers |
| RIGHT BRAIN | 7 | ~800 | ~500 | `PatternManager` class |
| CORPUS CALLOSUM | 8 | ~1,000 | ~600 | `AgentOrchestrator` class |
| CRAWLERS | 7 | ~2,000 | ~1,200 | Async Python crawlers |
| BRAIN Management | 10 | ~2,500 | ~1,500 | `BrainManager` class |
| System Utilities | 8 | ~1,500 | ~800 | Utility classes |
| **TOTAL** | **52** | **~9,300** | **~5,400** | **42% reduction** |

---

## 🎯 CORTEX Migration Strategy

### 1. Language Migration: PowerShell → Python

**Why Python?**
- ✅ Cross-platform (Windows/Linux/Mac)
- ✅ Better testing frameworks (pytest)
- ✅ Async/await for parallelization
- ✅ Rich libraries (AST parsing, async, ML)
- ✅ More maintainable (OOP, type hints)

**PowerShell Advantages Lost:**
- ❌ Native Windows integration
- ❌ Simple .ps1 execution

**Mitigation:**
- ✓ Use `subprocess` for Git/dotnet commands
- ✓ Entry point scripts (cortex.py)
- ✓ Virtual environment management

---

### 2. Architecture Preservation

**Keep:**
- ✅ Hemisphere separation (left/right/corpus-callosum)
- ✅ Script organization by purpose
- ✅ Event-driven triggers
- ✅ Modular, reusable components

**Enhance:**
- ⚡ Object-oriented design
- ⚡ Interface abstractions (ITestRunner, ICrawler)
- ⚡ Plugin architecture
- ⚡ Async parallelization

---

### 3. Feature Parity Requirements

**Must Preserve:**
- ✅ Full TDD automation (RED→GREEN→REFACTOR)
- ✅ Multi-threaded crawlers (5 areas)
- ✅ BRAIN management (updates, amnesia, reset)
- ✅ Metrics collection (Tier 3)
- ✅ Pattern matching/extraction
- ✅ Coordination messaging
- ✅ System setup automation

**Must Enhance:**
- ⚡ Faster execution (async)
- ⚡ Better error handling
- ⚡ Progress reporting (tqdm)
- ⚡ Cross-platform support

---

### 4. Testing Strategy

**Unit Tests:**
- 50+ tests for script logic
- Mock file system operations
- Mock subprocess calls

**Integration Tests:**
- Test full TDD cycle
- Test crawler orchestration
- Test BRAIN updates

**Performance Tests:**
- Crawler speed (<5 min target)
- BRAIN update speed (<10 sec)
- Metrics collection speed (<10 sec)

---

## ✅ Migration Checklist

### Data Migration
- [ ] Convert PowerShell → Python scripts
- [ ] Preserve all 52 script features
- [ ] Create base classes (TDDOrchestrator, PatternManager, etc.)
- [ ] Implement interfaces (ITestRunner, ICrawler)

### Architecture Migration
- [ ] Organize scripts/left-brain/, scripts/right-brain/, scripts/corpus-callosum/
- [ ] Create Python package structure
- [ ] Implement async crawlers
- [ ] Message-passing via orchestrator

### Feature Validation
- [ ] TDD automation working (RED→GREEN→REFACTOR)
- [ ] Crawlers functional (5 areas, <5 min)
- [ ] BRAIN updates automated
- [ ] Metrics collection accurate
- [ ] Pattern matching working
- [ ] System setup automated

### Performance Validation
- [ ] TDD cycle <2 min (KDS parity)
- [ ] Crawlers <5 min (60% faster than sequential)
- [ ] BRAIN update <10 sec (KDS parity)
- [ ] Metrics collection <10 sec (KDS parity)

---

## ✅ Completion Status

**Script Inventory:** ✅ COMPLETE  
**Total Scripts:** 52 automation scripts  
**Total Features:** 100+ features across all scripts  
**CORTEX Enhancement:** 42% LOC reduction + cross-platform  

**Next Steps:**
1. Update PROGRESS.md to mark Scripts inventory complete
2. Continue with Workflows inventory
3. Finish with Dashboard inventory
4. Begin Phase 0 implementation

---

**Extracted By:** GitHub Copilot  
**Date:** 2025-11-05  
**Source:** KDS v8 `scripts/` (52 scripts, 9,300+ lines)  
**Status:** ✅ Complete and comprehensive
