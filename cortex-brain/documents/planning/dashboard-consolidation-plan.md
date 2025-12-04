# Unified Health Dashboard - Multi-Application Architecture

**Plan ID:** unified-dashboard-2025-12-04  
**Created:** December 4, 2025  
**Status:** 📋 ACTIVE PLANNING  
**Plan File:** `cortex-brain/documents/planning/dashboard-consolidation-plan.md`  
**Architecture:** Single dashboard UI + URL-driven routing + Universal schema + Per-app data subdirectories

---

## 📋 Plan Overview

**Objective:** Build unified health dashboard supporting multiple applications (CORTEX, NOOR CANVAS, ALIST, KSESSIONS) with mock-first development approach, universal data schema, and URL-based routing.

**Total Features:** 3 (FEAT 0: Flask Cleanup, FEAT 1: Mock Dashboard, FEAT 2: CORTEX Health, FEAT 3: External Repos)  
**Total Phases:** 12  
**Estimated Time:** 8 hours 30 minutes  
**Execution Mode:** Supervised (phase checkpoints with progress reports)

---

## 🎯 Core Requirements

1. ✅ **Universal Data Schema:** All applications conform to standardized health-data format
2. ✅ **URL-Driven Routing:** Single dashboard loads data based on URL parameter (`/mock`, `/cortex`, `/noor-canvas`)
3. ✅ **Per-App Subdirectories:** Clean data separation (`dashboards/mock/`, `dashboards/cortex/`, etc.)
4. ✅ **Mock-First Development:** Build with mock data, iterate until satisfied, then implement live scanning
5. ✅ **Schema Validation:** Automated validation ensures all apps match universal schema
6. ✅ **External Repo Scanning:** CORTEX can scan external repos (NOOR CANVAS, ALIST, KSESSIONS)
7. ✅ **Multi-Tab Interface:** Overview, Metrics, Code Quality, Dependencies tabs
8. ✅ **Reusable Patterns:** Mock data structure becomes template for live data generation

---

## 📊 Execution Progress

**Overall Progress:** [░░░░░░░░░░] 0% - Planning Phase

**Completed Phases:** 0/12  
**Current Feature:** FEAT 0 (Flask Cleanup)  
**Current Phase:** Phase 0 (Flask Cleanup & Archive)  
**Remaining Phases:** 12

---

## 🏗️ Architecture Overview

**Directory Structure:**
```
cortex-brain/dashboards/
├── schema/
│   ├── health-data-schema.json       # Universal schema (ALL apps must conform)
│   ├── schema-validator.py           # Automated validation
│   └── README.md                     # Schema documentation
├── mock/                             # FEAT 1: Mock data for development
│   ├── health-data.json
│   ├── metrics.json
│   ├── code-quality.json
│   ├── dependencies.json
│   └── metadata.json
├── cortex/                           # FEAT 2: CORTEX internal health
│   └── (same structure as mock)
├── noor-canvas/                      # FEAT 3: External repo data
│   └── (same structure as mock)
├── alist/                            # FEAT 3: Future
│   └── (same structure as mock)
├── ksessions/                        # FEAT 3: Future
│   └── (same structure as mock)
└── ui/                               # Single dashboard codebase
    ├── index.html                    # Main dashboard page
    ├── app.js                        # URL routing + data loading
    ├── data-loader.js                # Dynamic data fetcher
    ├── components/
    │   ├── overview-tab.js
    │   ├── metrics-tab.js
    │   ├── quality-tab.js
    │   └── dependencies-tab.js
    └── styles/
        ├── main.css
        └── themes.css
```

**URL Routing:**
- `https://url/mock` → Loads `dashboards/mock/` data
- `https://url/cortex` → Loads `dashboards/cortex/` data
- `https://url/noor-canvas` → Loads `dashboards/noor-canvas/` data
- `https://url/alist` → Loads `dashboards/alist/` data (future)
- `https://url/ksessions` → Loads `dashboards/ksessions/` data (future)

**Key Deliverables:**
- Universal health data schema (standardized across all apps)
- Mock data files with realistic patterns from NOOR CANVAS/ALIST/KSESSIONS
- Single dashboard UI with multi-tab interface
- Schema validator for automated compliance checking
- External repo scanning capability (CORTEX → other repos)

---

## ⭐ FEAT 0: Flask Cleanup & Archive

**Duration:** 60 minutes  
**Objective:** Remove all Flask code, dependencies, and configurations; archive for historical reference

---

## Phase 0: Flask Cleanup & Archive

**Status:** ☐ NOT STARTED  
**Duration:** 60 minutes  
**Dependencies:** None (starting phase)

### Objective
Identify and remove ALL Flask-related code, configurations, and dependencies from CORTEX repository, archive removed files for historical reference, ensure no Flask remnants remain.

### Tasks

- [ ] **Task 0.1:** Create pre-cleanup git checkpoint
  - Command: `git tag -a flask-cleanup-checkpoint-$(date +%Y%m%d-%H%M%S) -m "Before Flask cleanup"`
  - Purpose: Easy rollback if issues discovered
  - Verify: Tag created successfully
  
- [ ] **Task 0.2:** Search for all Flask imports in Python files
  - Command: `grep -r "from flask import" --include="*.py" .`
  - Command: `grep -r "import flask" --include="*.py" .`
  - Document: List of files with Flask imports (save to cleanup report)
  
- [ ] **Task 0.3:** Search for Flask route decorators
  - Command: `grep -r "@app.route" --include="*.py" .`
  - Command: `grep -r "@blueprint.route" --include="*.py" .`
  - Document: All route definitions found
  
- [ ] **Task 0.4:** Search for Flask template rendering
  - Command: `grep -r "render_template" --include="*.py" .`
  - Command: `grep -r "render_template_string" --include="*.py" .`
  - Document: Files using Flask templating
  
- [ ] **Task 0.5:** Identify Flask configuration files
  - Search: Files containing `FLASK_APP`, `FLASK_ENV`, `app.config`
  - Check: `config.py`, `.env`, environment variables
  - Document: Configuration files to remove/update
  
- [ ] **Task 0.6:** Check requirements.txt for Flask dependencies
  - Search: `Flask`, `flask-*` packages
  - Examples: `Flask==X.X.X`, `flask-cors`, `flask-sqlalchemy`, `Werkzeug`
  - Document: All Flask-related packages to remove
  
- [ ] **Task 0.7:** Search for Flask test code
  - Search: `app.test_client()`, `client.get()`, `client.post()`
  - Location: `tests/` directory
  - Document: Tests that depend on Flask
  
- [ ] **Task 0.8:** Create archive directory for Flask files
  - Create: `cortex-brain/archives/flask-removal-2025-12-04/`
  - Subdirectories: `code/`, `templates/`, `configs/`, `tests/`
  - Purpose: Preserve removed files for historical reference
  
- [ ] **Task 0.9:** Archive Flask Python files (don't delete yet)
  - Copy: All files with Flask imports to archive
  - Preserve: Original directory structure in archive
  - Document: Archive manifest (file paths and sizes)
  
- [ ] **Task 0.10:** Archive Flask template files
  - Identify: HTML templates in `templates/` with Jinja2 syntax
  - Copy: Templates to `archives/.../templates/`
  - Document: Which templates were Flask-specific
  
- [ ] **Task 0.11:** Archive Flask configuration files
  - Copy: Flask configs to `archives/.../configs/`
  - Include: `.env` entries related to Flask (if any)
  
- [ ] **Task 0.12:** Remove Flask imports from Python files
  - Edit: Each file identified in Task 0.2
  - Remove: `import flask` and `from flask import ...` lines
  - Remove: Flask-specific code (routes, render_template calls, etc.)
  - Test: Verify files still parse (no syntax errors)
  
- [ ] **Task 0.13:** Remove Flask route decorators and functions
  - Edit: Files with @app.route or @blueprint.route
  - Remove: Route decorator and function body (or comment out if needed for reference)
  - Alternative: Replace with placeholder comment explaining removal
  
- [ ] **Task 0.14:** Remove Flask template rendering calls
  - Edit: Files with render_template calls
  - Remove: Template rendering logic
  - Alternative: Replace with TODO comments if functionality needs reimplementation
  
- [ ] **Task 0.15:** Update requirements.txt
  - Remove: `Flask==X.X.X` line
  - Remove: All `flask-*` extensions (cors, sqlalchemy, login, etc.)
  - Remove: `Werkzeug` if not used elsewhere
  - Save: Updated requirements.txt
  
- [ ] **Task 0.16:** Remove Flask configuration from config files
  - Edit: Remove `FLASK_APP`, `FLASK_ENV` from environment
  - Edit: Remove Flask-specific settings from config files
  - Clean: Any `.flaskenv` files
  
- [ ] **Task 0.17:** Update or remove Flask-dependent tests
  - Option 1: Remove tests entirely if no longer applicable
  - Option 2: Archive tests to `archives/.../tests/`
  - Option 3: Rewrite tests without Flask test client (use requests/pytest-mock)
  - Decision: Based on whether test intent is still valid
  
- [ ] **Task 0.18:** Verify no Flask references remain
  - Command: `grep -ri "flask" --include="*.py" .` (case-insensitive)
  - Command: `grep -ri "flask" --include="*.txt" .` (check docs/configs)
  - Expected: Zero matches (or only in archives and documentation)
  
- [ ] **Task 0.19:** Create Flask cleanup report
  - File: `cortex-brain/documents/reports/flask-cleanup-report-2025-12-04.md`
  - Sections:
    - Files removed/modified (count and list)
    - Dependencies removed from requirements.txt
    - Archive location and contents
    - Verification results (grep search showing zero Flask)
    - Rollback instructions (git tag reference)
  
- [ ] **Task 0.20:** Test CORTEX basic functionality without Flask
  - Run: `python -m src.main --help` (verify CLI works)
  - Run: `pytest tests/` (verify tests pass without Flask)
  - Check: Import errors or missing dependencies
  - Fix: Any issues found
  
- [ ] **Task 0.21:** Commit Flask cleanup
  - Stage: All modified files (removed Flask code)
  - Commit message: "Remove Flask dependencies and code - Phase 0 cleanup"
  - Include: Reference to cleanup report in commit message
  - Push: To current branch

### Checkpoint
✓ All Flask code removed from repository  
✓ Flask dependencies removed from requirements.txt  
✓ Removed files archived (not lost)  
✓ Flask cleanup report generated  
✓ Git checkpoint created for rollback safety  
✓ CORTEX basic functionality verified working  
✓ Clean slate ready for new dashboard development

---

## ⭐ FEAT 1: Mock Dashboard Development

**Duration:** 4 hours 15 minutes  
**Objective:** Build complete dashboard with mock data, iterate until satisfied with UI/UX

---

## Phase 1: Repository Data Discovery & Schema Design

**Status:** ☐ NOT STARTED  
**Duration:** 90 minutes  
**Dependencies:** None

### Objective
Scan NOOR CANVAS, ALIST, KSESSIONS repos to understand real-world data patterns, then design universal health data schema that works for all applications.

### Tasks

- [ ] **Task 1.1:** Scan NOOR CANVAS dev branch (primary reference)
  - Target: https://github.com/[owner]/noor-canvas/tree/dev
  - Focus: Repository structure, code organization, file types
  - Extract: Common patterns (src/, tests/, docs/, config files)
  - Document: Directory tree, key metrics to track
  
- [ ] **Task 1.2:** Quick validation scan of ALIST develop branch
  - Target: https://github.com/[owner]/alist/tree/develop
  - Purpose: Validate patterns found in NOOR CANVAS
  - Compare: Similarities and differences in structure
  - Document: Unique patterns not in NOOR CANVAS
  
- [ ] **Task 1.3:** Quick validation scan of KSESSIONS development branch
  - Target: https://github.com/[owner]/ksessions/tree/development
  - Purpose: Further validation of patterns
  - Compare: Consistency with NOOR CANVAS and ALIST
  - Document: Any additional unique patterns
  
- [ ] **Task 1.4:** Analyze common data patterns across all 3 repos
  - Identify: Metrics present in all repos (LOC, file count, complexity, etc.)
  - Identify: Metrics unique to specific repos (may need optional fields)
  - Categorize: Must-have vs nice-to-have metrics
  
- [ ] **Task 1.5:** Design universal health data schema
  - Create: `cortex-brain/dashboards/schema/health-data-schema.json`
  - Include: Core fields (repo_name, timestamp, overall_health_score)
  - Include: Metrics fields (lines_of_code, file_count, test_coverage, etc.)
  - Include: Code quality fields (complexity_score, violations, tech_debt)
  - Include: Dependencies fields (total_dependencies, outdated_count, vulnerabilities)
  - Make: Extensible (allow optional fields for app-specific metrics)
  
- [ ] **Task 1.6:** Create schema documentation
  - File: `cortex-brain/dashboards/schema/README.md`
  - Document: Each field's purpose, data type, valid ranges
  - Include: Example data for each field
  - Explain: How to extend schema for new apps
  
- [ ] **Task 1.7:** Define tab structure based on discovered data
  - Tab 1: Overview (health score, key metrics at-a-glance)
  - Tab 2: Metrics (detailed statistics, trends, comparisons)
  - Tab 3: Code Quality (complexity, violations, tech debt)
  - Tab 4: Dependencies (dependency graph, vulnerabilities, updates)
  - Map: Which schema fields appear in which tabs

### Checkpoint
✓ 3 repos scanned and documented  
✓ Universal schema designed and documented  
✓ Tab structure defined based on real data patterns  
✓ Schema ready for mock data generation

---

## Phase 2: Mock Data File Generation

**Status:** ☐ NOT STARTED  
**Duration:** 45 minutes  
**Dependencies:** Phase 1 (schema must exist)

### Objective
Generate comprehensive mock data files conforming to universal schema, simulating realistic scenarios (small/medium/large repos, various health states).

### Tasks

- [ ] **Task 2.1:** Create mock data directory structure
  - Create: `cortex-brain/dashboards/mock/`
  - Verify: Directory writable and accessible
  
- [ ] **Task 2.2:** Generate health-data.json (overall health metrics)
  - Fields: repo_name, timestamp, overall_health_score (0-100)
  - Fields: status (healthy/warning/critical), last_scan_date
  - Include: Summary metrics (total_issues, critical_issues, warnings)
  - Scenario: Generate 3 variants (healthy=90, warning=60, critical=30)
  
- [ ] **Task 2.3:** Generate metrics.json (detailed statistics)
  - Fields: lines_of_code, file_count, directory_count
  - Fields: average_file_size, largest_file, test_file_count
  - Fields: test_coverage_percentage, documentation_coverage
  - Scenario: Small repo (1K LOC), Medium (10K LOC), Large (100K LOC)
  
- [ ] **Task 2.4:** Generate code-quality.json (quality metrics)
  - Fields: complexity_score, cyclomatic_complexity_avg, cognitive_complexity_avg
  - Fields: code_smells_count, code_smell_details (array)
  - Fields: duplication_percentage, maintainability_index
  - Fields: tech_debt_hours, tech_debt_ratio
  - Scenario: High quality (few issues), Medium, Low (many issues)
  
- [ ] **Task 2.5:** Generate dependencies.json (dependency data)
  - Fields: total_dependencies, direct_dependencies, transitive_dependencies
  - Fields: outdated_count, outdated_list (array with name, current, latest)
  - Fields: vulnerabilities_count, vulnerability_details (severity, CVE)
  - Fields: license_issues, dependency_graph (simplified tree)
  - Scenario: Clean deps, Some outdated, Many vulnerabilities
  
- [ ] **Task 2.6:** Generate metadata.json (repository metadata)
  - Fields: repo_url, branch, commit_hash, commit_date
  - Fields: contributors_count, primary_language, languages_breakdown
  - Fields: repo_age_days, last_commit_days_ago, commit_frequency
  - Fields: tags, custom_labels (array)
  
- [ ] **Task 2.7:** Create README.md in mock directory
  - Document: Purpose of each mock file
  - Explain: How to modify mock data for testing
  - Include: Examples of using mock data with dashboard
  - Note: These files are templates for live data generation
  
- [ ] **Task 2.8:** Validate all mock files against schema
  - Run: `python cortex-brain/dashboards/schema/schema-validator.py mock`
  - Verify: All files pass validation
  - Fix: Any schema violations found

### Checkpoint
✓ Mock data directory created with 5 JSON files  
✓ Mock data covers realistic scenarios (small/medium/large, healthy/warning/critical)  
✓ All mock files validated against universal schema  
✓ Mock data ready for UI development

---

## Phase 3: Schema Validator Implementation

**Status:** ☐ NOT STARTED  
**Duration:** 30 minutes  
**Dependencies:** Phase 1 (schema exists)

### Objective
Create automated schema validator to ensure all application data directories conform to universal schema.

### Tasks

- [ ] **Task 3.1:** Create schema validator script
  - File: `cortex-brain/dashboards/schema/schema-validator.py`
  - Imports: json, jsonschema, pathlib, sys
  
- [ ] **Task 3.2:** Implement schema loading function
  - Function: `load_schema()` → returns parsed health-data-schema.json
  - Error handling: Graceful failure if schema file missing/invalid
  
- [ ] **Task 3.3:** Implement data directory validation function
  - Function: `validate_directory(app_name)` → validates dashboards/{app_name}/
  - Check: All required files exist (health-data, metrics, code-quality, dependencies, metadata)
  - Check: Each file conforms to schema
  - Return: (success: bool, errors: list)
  
- [ ] **Task 3.4:** Implement detailed error reporting
  - Report: Which file failed validation
  - Report: Which field violated schema (missing, wrong type, out of range)
  - Report: Suggested fix for common errors
  
- [ ] **Task 3.5:** Add CLI interface
  - Usage: `python schema-validator.py <app_name>`
  - Example: `python schema-validator.py mock`
  - Exit code: 0 for success, 1 for validation failure
  
- [ ] **Task 3.6:** Add batch validation mode
  - Usage: `python schema-validator.py --all`
  - Validates: All subdirectories in dashboards/
  - Report: Summary table (app name, status, error count)
  
- [ ] **Task 3.7:** Test validator with mock data
  - Run: `python schema-validator.py mock`
  - Verify: Passes with no errors
  - Test: Intentionally break mock file, verify error caught
  - Test: Restore mock file to valid state

### Checkpoint
✓ Schema validator implemented and tested  
✓ Validates all required files and schema compliance  
✓ Clear error reporting for debugging  
✓ Ready for use with all application data directories

---

## Phase 4: Dashboard UI Framework

**Status:** ☐ NOT STARTED  
**Duration:** 90 minutes  
**Dependencies:** Phase 2 (mock data exists)

### Objective
Build single-page dashboard with URL-driven routing, dynamic data loading, and multi-tab interface.

### Tasks

- [ ] **Task 4.1:** Create UI directory structure
  - Create: `cortex-brain/dashboards/ui/`
  - Create: `cortex-brain/dashboards/ui/components/`
  - Create: `cortex-brain/dashboards/ui/styles/`
  
- [ ] **Task 4.2:** Create index.html (main dashboard page)
  - HTML5 boilerplate with semantic structure
  - Header: Dashboard title, app selector dropdown
  - Navigation: Tab buttons (Overview, Metrics, Quality, Dependencies)
  - Main content area: Dynamic tab content loads here
  - Footer: Last updated timestamp, data source indicator
  
- [ ] **Task 4.3:** Create app.js (main application logic)
  - Function: `parseURLParam()` → extracts app name from URL
  - Function: `loadAppData(appName)` → fetches all JSON files for app
  - Function: `switchTab(tabName)` → shows selected tab, hides others
  - Function: `init()` → initializes dashboard on page load
  - Event listeners: Tab clicks, app selector changes
  
- [ ] **Task 4.4:** Create data-loader.js (data fetching module)
  - Function: `fetchJSON(url)` → async fetch with error handling
  - Function: `loadAllData(appName)` → loads all 5 JSON files
  - Function: `validateData(data)` → client-side schema check (basic)
  - Cache: Store loaded data to avoid redundant fetches
  - Error handling: Display friendly message if data missing/invalid
  
- [ ] **Task 4.5:** Create overview-tab.js (Overview tab component)
  - Display: Overall health score with color coding (green/yellow/red)
  - Display: Key metrics summary (LOC, files, coverage, issues)
  - Display: Health status indicator (healthy/warning/critical)
  - Display: Last scan timestamp
  - Visual: Progress bars for scores, icon for status
  
- [ ] **Task 4.6:** Create metrics-tab.js (Metrics tab component)
  - Display: Detailed statistics table (all metrics from metrics.json)
  - Display: Code distribution (languages breakdown)
  - Display: Test coverage visualization
  - Display: Repository age and activity metrics
  
- [ ] **Task 4.7:** Create quality-tab.js (Code Quality tab component)
  - Display: Complexity scores with trend indicators
  - Display: Code smells list with severity
  - Display: Duplication percentage visualization
  - Display: Tech debt estimation (hours, ratio)
  - Display: Maintainability index gauge
  
- [ ] **Task 4.8:** Create dependencies-tab.js (Dependencies tab component)
  - Display: Total dependencies count
  - Display: Outdated dependencies table (name, current, latest, action)
  - Display: Vulnerabilities list with severity and CVE
  - Display: License compliance status
  - Display: Simplified dependency graph (if possible with plain JS)
  
- [ ] **Task 4.9:** Create main.css (core styles)
  - Layout: Responsive grid for tabs and content
  - Typography: Readable fonts, proper hierarchy
  - Colors: Semantic colors (green=good, yellow=warning, red=critical)
  - Components: Buttons, cards, tables, progress bars
  
- [ ] **Task 4.10:** Create themes.css (visual themes)
  - Light theme: Default, high contrast
  - Dark theme: Optional, eye-friendly
  - Theme toggle: Button in header (future enhancement)
  
- [ ] **Task 4.11:** Wire URL routing to data loading
  - Example: `https://url/mock` → calls `loadAppData('mock')`
  - Example: `https://url/cortex` → calls `loadAppData('cortex')`
  - Fallback: If no param, default to 'mock'
  - Error: If app not found, show friendly 404-style message
  
- [ ] **Task 4.12:** Test dashboard with mock data
  - Navigate to: `https://url/mock` (or local equivalent)
  - Verify: All tabs load and display mock data correctly
  - Verify: Tab switching works smoothly
  - Verify: Data displays match mock JSON files
  - Test: Responsive design on mobile/tablet/desktop

### Checkpoint
✓ Dashboard UI fully functional  
✓ All 4 tabs rendering mock data correctly  
✓ URL-driven routing working  
✓ Responsive design validated

---

## Phase 5: Mock Dashboard Iteration & Refinement

**Status:** ☐ NOT STARTED  
**Duration:** 60 minutes  
**Dependencies:** Phase 4 (dashboard UI exists)

### Objective
Review dashboard with you, iterate on layout/information density/tabs until fully satisfied with UI/UX.

### Tasks

- [ ] **Task 5.1:** Initial dashboard review session
  - Load: Dashboard with mock data (`https://url/mock`)
  - Review: Overall layout and visual hierarchy
  - Capture: Your feedback on what works/doesn't work
  
- [ ] **Task 5.2:** Tab structure review
  - Review: 4 tabs (Overview, Metrics, Quality, Dependencies)
  - Question: Are these the right tabs? Need more/fewer?
  - Question: Is information organized logically within each tab?
  - Adjust: Add/remove/rename tabs based on feedback
  
- [ ] **Task 5.3:** Information density review
  - Review: Amount of information shown per tab
  - Question: Too much clutter? Too sparse?
  - Adjust: Show more/less detail, add collapsible sections
  
- [ ] **Task 5.4:** Visual design review
  - Review: Colors, fonts, spacing, alignment
  - Question: Professional enough? Easy to read?
  - Adjust: Styling tweaks based on feedback
  
- [ ] **Task 5.5:** Data visualization review
  - Review: How metrics are displayed (tables, charts, gauges)
  - Question: Are visualizations clear and useful?
  - Consider: Adding charts (can use simple CSS-based charts or lightweight library)
  
- [ ] **Task 5.6:** Interaction review
  - Review: Tab switching, data loading, error states
  - Test: Edge cases (missing data, network errors)
  - Question: Is interaction smooth and intuitive?
  
- [ ] **Task 5.7:** Mobile responsiveness review
  - Test: Dashboard on mobile viewport
  - Question: Does layout adapt well to small screens?
  - Adjust: Media queries, mobile-first considerations
  
- [ ] **Task 5.8:** Implement approved changes from review
  - Make: All agreed-upon adjustments
  - Test: Changes don't break existing functionality
  
- [ ] **Task 5.9:** Second review session (if needed)
  - Review: Updated dashboard with changes
  - Verify: All feedback addressed
  - Iterate: Further adjustments if needed
  
- [ ] **Task 5.10:** Final approval checkpoint
  - Confirm: Dashboard UI/UX meets expectations
  - Confirm: Ready to move to FEAT 2 (CORTEX health data)
  - Document: Final design decisions for future reference

### Checkpoint
✓ Dashboard UI/UX approved and finalized  
✓ All tabs displaying information effectively  
✓ Mock data serving as successful template  
✓ Ready for FEAT 2 (CORTEX health data integration)

---

## ⭐ FEAT 2: CORTEX Health Dashboard

**Duration:** 2 hours  
**Objective:** Implement CORTEX internal health metrics, generate data conforming to universal schema

---

## Phase 6: CORTEX Metrics Collection

**Status:** ☐ NOT STARTED  
**Duration:** 60 minutes  
**Dependencies:** Phase 5 (mock dashboard approved)

### Objective
Implement CORTEX internal metrics collection to generate health data matching universal schema.

### Tasks

- [ ] **Task 6.1:** Create CORTEX data directory
  - Create: `cortex-brain/dashboards/cortex/`
  - Structure: Same as mock (health-data.json, metrics.json, etc.)
  
- [ ] **Task 6.2:** Implement CORTEX metrics collector script
  - File: `cortex-brain/dashboards/cortex/collect-metrics.py`
  - Purpose: Scan CORTEX repo and generate dashboard data files
  
- [ ] **Task 6.3:** Implement health-data.json generation
  - Calculate: Overall health score based on multiple factors
  - Factors: Test pass rate, code quality, tech debt, outdated deps
  - Status: Derive from health score (>80=healthy, 50-80=warning, <50=critical)
  
- [ ] **Task 6.4:** Implement metrics.json generation
  - Count: Lines of code (using cloc or pygount)
  - Count: Files, directories, test files
  - Calculate: Test coverage (from pytest coverage report)
  - Calculate: Average file size, largest file
  
- [ ] **Task 6.5:** Implement code-quality.json generation
  - Run: pylint or flake8 for code quality analysis
  - Calculate: Complexity metrics (radon or similar)
  - Identify: Code smells, duplication (via similarity analysis)
  - Estimate: Tech debt using established formulas
  
- [ ] **Task 6.6:** Implement dependencies.json generation
  - Parse: requirements.txt for dependencies
  - Check: pip list --outdated for outdated packages
  - Check: safety or pip-audit for vulnerabilities
  - Note: License compliance (if applicable)
  
- [ ] **Task 6.7:** Implement metadata.json generation
  - Extract: Git metadata (commit hash, date, branch)
  - Count: Contributors (git log analysis)
  - Analyze: Primary language, language breakdown
  - Calculate: Repo age, last commit time, commit frequency
  
- [ ] **Task 6.8:** Run metrics collector for CORTEX
  - Execute: `python cortex-brain/dashboards/cortex/collect-metrics.py`
  - Verify: All 5 JSON files generated
  - Validate: `python schema-validator.py cortex` passes
  
- [ ] **Task 6.9:** Test CORTEX dashboard
  - Navigate: `https://url/cortex`
  - Verify: Dashboard loads CORTEX data correctly
  - Compare: Mock vs real data display, confirm no issues
  - Review: Accuracy of metrics displayed

### Checkpoint
✓ CORTEX metrics collector implemented  
✓ All dashboard data files generated and validated  
✓ Dashboard successfully displays CORTEX health data  
✓ Universal schema proven to work with real data

---

## Phase 7: CORTEX Dashboard Automation

**Status:** ☐ NOT STARTED  
**Duration:** 60 minutes  
**Dependencies:** Phase 6 (metrics collector works)

### Objective
Automate CORTEX metrics collection to keep dashboard data fresh without manual intervention.

### Tasks

- [ ] **Task 7.1:** Create automated collection script
  - Script: `scripts/update-cortex-dashboard.sh`
  - Actions: Run metrics collector, validate with schema, update timestamp
  
- [ ] **Task 7.2:** Add scheduling options
  - Option 1: Cron job (for Unix systems)
  - Option 2: GitHub Actions workflow (runs on push/schedule)
  - Option 3: Manual trigger (for on-demand updates)
  - Document: How to set up each option
  
- [ ] **Task 7.3:** Implement error handling and notifications
  - Check: Metrics collection success/failure
  - Log: Errors to `logs/dashboard-updates.log`
  - Notify: (Optional) Email/Slack on collection failure
  
- [ ] **Task 7.4:** Add incremental update support
  - Optimization: Only regenerate files if source changed
  - Track: Last update timestamp, source file hashes
  - Skip: Expensive calculations if data unchanged
  
- [ ] **Task 7.5:** Test automation
  - Run: Automated update script manually
  - Verify: Dashboard data refreshes correctly
  - Verify: Error handling works (simulate failure)
  
- [ ] **Task 7.6:** Document automation setup
  - File: `cortex-brain/dashboards/cortex/README.md`
  - Explain: How automation works
  - Include: Setup instructions for all scheduling options
  - Include: Troubleshooting guide

### Checkpoint
✓ CORTEX dashboard updates automatically  
✓ Scheduling options documented  
✓ Error handling robust  
✓ Dashboard data stays fresh without manual work

---

## ⭐ FEAT 3: External Repository Scanning

**Duration:** 3 hours 15 minutes (deferred after FEAT 1 & 2 complete)  
**Objective:** Scan external repos (NOOR CANVAS, ALIST, KSESSIONS), generate data matching universal schema

---

## Phase 8: External Repo Scanner Implementation

**Status:** ☐ NOT STARTED (DEFERRED)  
**Duration:** 90 minutes  
**Dependencies:** Phase 7 (CORTEX automation working)

### Objective
Implement external repository scanner that can clone, analyze, and generate dashboard data for any Git repository.

### Tasks

- [ ] **Task 8.1:** Create external scanner framework
  - File: `src/scanners/external_repo_scanner.py`
  - Purpose: Generic scanner for any external Git repo
  
- [ ] **Task 8.2:** Implement repository cloning
  - Function: `clone_repo(repo_url, target_dir)` using GitPython or subprocess
  - Handle: Authentication (SSH keys, tokens if needed)
  - Handle: Shallow clones for large repos (efficiency)
  
- [ ] **Task 8.3:** Implement metrics collection (reuse CORTEX logic)
  - Adapt: CORTEX metrics collector to work with any repo
  - Input: Path to cloned repo
  - Output: 5 JSON files matching universal schema
  
- [ ] **Task 8.4:** Implement cleanup after scanning
  - Delete: Temporary clone directory
  - Preserve: Generated dashboard data files
  - Handle: Cleanup on error/interruption
  
- [ ] **Task 8.5:** Add configuration for external repos
  - File: `cortex-brain/dashboards/external-repos-config.yaml`
  - Config: List of repos to scan (name, URL, branch)
  - Example:
    ```yaml
    repos:
      - name: noor-canvas
        url: https://github.com/[owner]/noor-canvas
        branch: dev
      - name: alist
        url: https://github.com/[owner]/alist
        branch: develop
    ```
  
- [ ] **Task 8.6:** Create scan orchestrator
  - Script: `scripts/scan-external-repos.py`
  - Reads: external-repos-config.yaml
  - For each repo: Clone → Collect metrics → Validate → Save to dashboards/{name}/
  
- [ ] **Task 8.7:** Test with NOOR CANVAS
  - Run: `python scripts/scan-external-repos.py --repo noor-canvas`
  - Verify: dashboards/noor-canvas/ populated with valid data
  - Test: Dashboard loads NOOR CANVAS data (`https://url/noor-canvas`)

### Checkpoint
✓ External repo scanner working  
✓ NOOR CANVAS scanned and dashboard operational  
✓ Framework ready for ALIST and KSESSIONS  
✓ Generic scanner can handle any Git repo

---

## Phase 9: NOOR CANVAS Dashboard Integration

**Status:** ☐ NOT STARTED (DEFERRED)  
**Duration:** 30 minutes  
**Dependencies:** Phase 8 (external scanner works)

### Objective
Finalize NOOR CANVAS dashboard integration, validate metrics accuracy, ensure smooth operation.

### Tasks

- [ ] **Task 9.1:** Run full NOOR CANVAS scan
  - Execute: `python scripts/scan-external-repos.py --repo noor-canvas`
  - Verify: All 5 JSON files generated in dashboards/noor-canvas/
  - Validate: `python schema-validator.py noor-canvas` passes
  
- [ ] **Task 9.2:** Review NOOR CANVAS dashboard data
  - Navigate: `https://url/noor-canvas`
  - Review: All tabs display data correctly
  - Check: Metrics accuracy (compare with actual repo if possible)
  
- [ ] **Task 9.3:** Compare NOOR CANVAS vs Mock data
  - Identify: Differences between mock and real data
  - Question: Does real data reveal missing metrics/fields?
  - Adjust: Schema if needed (add optional fields for real-world patterns)
  
- [ ] **Task 9.4:** Optimize scanning performance
  - Profile: Identify slow operations in scanner
  - Optimize: Use caching, parallel processing if applicable
  - Document: Expected scan time for various repo sizes
  
- [ ] **Task 9.5:** Document NOOR CANVAS integration
  - File: `cortex-brain/dashboards/noor-canvas/README.md`
  - Explain: How scanning works, how often to update
  - Include: Specific notes about NOOR CANVAS patterns

### Checkpoint
✓ NOOR CANVAS dashboard fully operational  
✓ Metrics accurate and validated  
✓ Performance optimized for real repo scanning  
✓ Documentation complete

---

## Phase 10: ALIST & KSESSIONS Dashboard Integration

**Status:** ☐ NOT STARTED (DEFERRED)  
**Duration:** 45 minutes  
**Dependencies:** Phase 9 (NOOR CANVAS working)

### Objective
Extend dashboard to support ALIST and KSESSIONS repos using proven patterns from NOOR CANVAS.

### Tasks

- [ ] **Task 10.1:** Add ALIST to external-repos-config.yaml
  - Name: alist
  - URL: https://github.com/[owner]/alist
  - Branch: develop
  
- [ ] **Task 10.2:** Scan ALIST repository
  - Run: `python scripts/scan-external-repos.py --repo alist`
  - Verify: dashboards/alist/ populated
  - Validate: Schema compliance
  
- [ ] **Task 10.3:** Test ALIST dashboard
  - Navigate: `https://url/alist`
  - Verify: All tabs functional
  - Review: Data accuracy
  
- [ ] **Task 10.4:** Add KSESSIONS to external-repos-config.yaml
  - Name: ksessions
  - URL: https://github.com/[owner]/ksessions
  - Branch: development
  
- [ ] **Task 10.5:** Scan KSESSIONS repository
  - Run: `python scripts/scan-external-repos.py --repo ksessions`
  - Verify: dashboards/ksessions/ populated
  - Validate: Schema compliance
  
- [ ] **Task 10.6:** Test KSESSIONS dashboard
  - Navigate: `https://url/ksessions`
  - Verify: All tabs functional
  - Review: Data accuracy
  
- [ ] **Task 10.7:** Create comparison view (optional enhancement)
  - Feature: Side-by-side comparison of multiple apps
  - Example: Compare CORTEX vs NOOR CANVAS vs ALIST metrics
  - UI: Dropdown to select 2-3 apps for comparison

### Checkpoint
✓ ALIST dashboard operational  
✓ KSESSIONS dashboard operational  
✓ All 5 applications (mock, cortex, noor-canvas, alist, ksessions) working  
✓ Universal schema proven across diverse repos

---

## Phase 11: Dashboard Deployment & Automation

**Status:** ☐ NOT STARTED (DEFERRED)  
**Duration:** 30 minutes  
**Dependencies:** Phase 10 (all apps integrated)

### Objective
Deploy dashboard for production use, set up automated scanning for all external repos.

### Tasks

- [ ] **Task 11.1:** Configure dashboard hosting
  - Option 1: Static hosting (GitHub Pages, Netlify)
  - Option 2: Python web server (Flask, FastAPI)
  - Option 3: Local-only (file:// URLs for development)
  - Choose: Based on access requirements and security
  
- [ ] **Task 11.2:** Set up automated scanning schedule
  - GitHub Actions workflow: `scan-all-repos.yml`
  - Schedule: Daily at 2 AM UTC (configurable)
  - Actions: Clone → Scan → Validate → Commit updated data
  
- [ ] **Task 11.3:** Implement scan failure notifications
  - Detect: Any repo scan failures
  - Notify: Email/Slack/GitHub issue
  - Log: Detailed error information
  
- [ ] **Task 11.4:** Add dashboard health monitoring
  - Monitor: Last successful scan time per app
  - Alert: If data >48 hours old
  - Display: Data freshness indicator on dashboard
  
- [ ] **Task 11.5:** Create deployment documentation
  - File: `cortex-brain/dashboards/DEPLOYMENT.md`
  - Sections: Hosting setup, automation setup, troubleshooting
  - Include: Security considerations for external repo access
  
- [ ] **Task 11.6:** Test end-to-end automation
  - Trigger: GitHub Actions workflow manually
  - Verify: All repos scanned successfully
  - Verify: Dashboard data updated
  - Verify: Notifications work on failure

### Checkpoint
✓ Dashboard deployed and accessible  
✓ Automated scanning operational for all repos  
✓ Failure notifications working  
✓ System fully autonomous and production-ready

---

## 🎯 Success Criteria

**FEAT 0: Flask Cleanup & Archive**
- [ ] All Flask imports removed from Python files (zero grep matches)
- [ ] Flask dependencies removed from requirements.txt
- [ ] Removed code archived in `cortex-brain/archives/flask-removal-2025-12-04/`
- [ ] Flask cleanup report generated with rollback instructions
- [ ] Git checkpoint created before cleanup
- [ ] CORTEX CLI and tests working without Flask
- [ ] Commit pushed with Flask removal changes

**FEAT 1: Mock Dashboard Development**
- [ ] Universal health data schema designed and documented
- [ ] Mock data files generated covering 3 scenarios (small/medium/large repos)
- [ ] Schema validator implemented and passing for mock data
- [ ] Dashboard UI with 4 tabs rendering mock data correctly
- [ ] URL routing working (`https://url/mock` loads mock data)
- [ ] Dashboard UI/UX approved after iteration with you
- [ ] Responsive design working on mobile/tablet/desktop

**FEAT 2: CORTEX Health Dashboard**
- [ ] CORTEX metrics collector implemented
- [ ] All 5 JSON files generated for CORTEX and validated
- [ ] Dashboard displays CORTEX health data (`https://url/cortex`)
- [ ] Automated update mechanism working (manual/cron/GitHub Actions)
- [ ] CORTEX data stays fresh without manual intervention

**FEAT 3: External Repository Scanning**
- [ ] External repo scanner framework implemented
- [ ] NOOR CANVAS scanned and dashboard operational (`https://url/noor-canvas`)
- [ ] ALIST scanned and dashboard operational (`https://url/alist`)
- [ ] KSESSIONS scanned and dashboard operational (`https://url/ksessions`)
- [ ] Automated scanning schedule configured for all external repos
- [ ] Dashboard deployed and production-ready

**Cross-Cutting Requirements**
- [ ] All application data directories pass schema validation
- [ ] Single dashboard UI handles all applications without custom code per app
- [ ] Documentation complete (schema, setup, deployment, automation)
- [ ] Error handling robust (missing data, network failures, validation errors)

---

## 📝 Execution Notes

**Session Restoration:**
This plan can be resumed from any chat window. To resume:
1. Open new Copilot Chat
2. Reference this plan file
3. Say "continue" or "resume plan"
4. CORTEX will resume from last checkpoint

**Progress Tracking:**
- Real-time progress bars show completion percentage and ETA
- Plan file updates with checkmarks as tasks complete
- Phase checkpoints include timestamp and summary

**Interactive Planning:**
Once this plan is active, all your input is assumed for the plan until you say "approve plan". No need to prefix with "add to plan".

**Execution Strategy:**
- **FEAT 0 (First):** Phase 0 Flask cleanup - Clean slate before building new
- **FEAT 1 (Priority):** Complete Phases 1-5 first, iterate until mock dashboard approved
- **FEAT 2 (Next):** Phases 6-7 after FEAT 1 complete, validates schema with real data
- **FEAT 3 (Deferred):** Phases 8-11 after FEAT 1 & 2 working, extends to external repos

**Parallel Opportunities:**
- Phase 3 (Schema Validator) can start as soon as Phase 1 (Schema Design) completes
- Phase 4 (UI Framework) can start in parallel with Phase 2 (Mock Data Generation)
- Phase 6 (CORTEX Metrics) development can begin during Phase 5 (Mock Iteration)

**External Repo Access:**
You'll need to provide:
- GitHub URLs for NOOR CANVAS, ALIST, KSESSIONS repos
- Branch names (dev, develop, development, main)
- Access credentials if repos are private (SSH keys, tokens)

**Technology Decisions:**
- **Frontend:** Plain HTML/CSS/JavaScript (framework-agnostic, easy iteration)
- **Backend:** Python for metrics collection and scanning
- **Data Format:** JSON (human-readable, easy to validate)
- **Schema Validation:** jsonschema library in Python
- **Hosting:** TBD in Phase 11 based on requirements

---

## 📚 References

**Related Documentation:**
- `.github/prompts/modules/planning-orchestrator-guide.md` - Planning System 2.0
- `.github/prompts/modules/response-format.md` - Response templates
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules

**Schema Documentation:**
- `cortex-brain/dashboards/schema/README.md` - Schema field definitions (to be created)
- `cortex-brain/dashboards/schema/health-data-schema.json` - Universal schema (to be created)

**Application Documentation:**
- `cortex-brain/dashboards/mock/README.md` - Mock data usage (to be created)
- `cortex-brain/dashboards/cortex/README.md` - CORTEX metrics collection (to be created)
- `cortex-brain/dashboards/DEPLOYMENT.md` - Deployment guide (to be created)

**Reports (To Be Generated):**
- `cortex-brain/documents/reports/dashboard-schema-design.md` - Schema design decisions
- `cortex-brain/documents/reports/dashboard-implementation.md` - Implementation summary
- `cortex-brain/documents/reports/external-repo-scanning.md` - Scanning results

---

## 🔄 Migration from Old Plan

**What Changed:**
- ❌ **Removed:** Flask consolidation and removal (not applicable to new dashboard)
- ❌ **Removed:** Deploy validator updates (not needed for standalone dashboard)
- ✅ **Added:** Universal schema design and validation
- ✅ **Added:** URL-driven routing architecture
- ✅ **Added:** Mock-first development approach
- ✅ **Added:** External repo scanning capability
- ✅ **Changed:** From "consolidate 2 dashboards" to "build unified multi-app dashboard"

**Why:**
- Clarified this is onboarding application dashboard, not CORTEX internal dashboard
- Recognized need for external repo scanning to understand data patterns
- Adopted mock-first approach to iterate quickly without backend dependencies
- Universal schema ensures consistency across all applications

---

**Plan Ready for Execution**  
Say "approve plan" to begin Phase 1 (Repository Data Discovery)

**Status:** ☐ NOT STARTED  
**Duration:** 60 minutes  
**Dependencies:** Phase 1 (need dashboard inventory)

### Objective
Locate ALL Flask code in the repository and analyze impact of removal on dashboards, validators, and other components.

### Tasks
- [ ] **Task 2.1:** Search for Flask imports across codebase
  - Command: `grep -r "from flask import" --include="*.py"`
  - Command: `grep -r "import flask" --include="*.py"`
  - Document: Every file that imports Flask
  
- [ ] **Task 2.2:** Identify Flask app instances
  - Search: `Flask(__name__)`, `app = Flask`, `create_app()`
  - Document: Entry points, configuration files
  
- [ ] **Task 2.3:** Catalog Flask routes and endpoints
  - Search: `@app.route`, `@blueprint.route`
  - Document: All route definitions with HTTP methods
  - Map: Which routes are used by dashboards
  
- [ ] **Task 2.4:** Find Flask template rendering
  - Search: `render_template(`, `render_template_string(`
  - Document: HTML templates requiring Flask context
  
- [ ] **Task 2.5:** Identify Flask-dependent deploy validators
  - Location: `src/operations/modules/admin/deploy_validators/`
  - Review: Which validators import or use Flask
  - Document: Validators requiring replacement/removal
  
- [ ] **Task 2.6:** Analyze Flask session/cookie usage
  - Search: `session[`, `request.cookies`, `response.set_cookie`
  - Document: State management that needs alternative
  
- [ ] **Task 2.7:** Check for Flask extensions
  - Search: `flask_`, `Flask-` in requirements.txt
  - Examples: flask_cors, flask_sqlalchemy, flask_login
  - Document: Extensions to uninstall
  
- [ ] **Task 2.8:** Create Flask removal impact matrix
  - Columns: File, Flask Usage, Impact Level, Replacement Strategy
  - Impact Levels: Critical (breaks dashboard), High (breaks deploy), Medium (breaks tests), Low (cosmetic)

### Checkpoint
✓ Complete Flask inventory with 100% coverage  
✓ Impact matrix shows replacement strategy  
✓ Flask-dependent validators identified for Phase 5

---

## Phase 3: Dashboard Consolidation

**Status:** ☐ NOT STARTED  
**Duration:** 90 minutes  
**Dependencies:** Phase 1 (consolidation strategy), Phase 2 (Flask inventory)

### Objective
Merge two dashboards into one, preserving ALL original requirements, removing Flask dependencies.

### Tasks
- [ ] **Task 3.1:** Choose consolidated dashboard architecture
  - Decision: Keep Dashboard 1 structure, Dashboard 2 structure, or hybrid?
  - Rationale: Which architecture works without Flask?
  - Document: Selected architecture with justification
  
- [ ] **Task 3.2:** Migrate unique features from source dashboard
  - Identify: Features only in Dashboard 1 or Dashboard 2
  - Implement: Add missing features to consolidated dashboard
  - Test: Each migrated feature works standalone
  
- [ ] **Task 3.3:** Remove Flask template rendering
  - Replace: `render_template()` with static HTML or JavaScript fetch
  - Strategy: Serve HTML statically, use AJAX for dynamic data
  - Update: All dashboard endpoints to return JSON (not rendered HTML)
  
- [ ] **Task 3.4:** Convert Flask routes to alternative backend
  - Options: FastAPI, vanilla Python HTTP server, static JSON files
  - Implement: New backend endpoints (if needed)
  - Document: API contract (request/response formats)
  
- [ ] **Task 3.5:** Update JavaScript to fetch from new backend
  - Modify: AJAX calls to use new endpoint URLs
  - Remove: Flask-specific URL generation (url_for)
  - Add: Error handling for fetch failures
  
- [ ] **Task 3.6:** Validate all original requirements still met
  - Review: Feature matrix from Phase 1
  - Test: Each requirement manually
  - Confirm: No features lost during consolidation
  
- [ ] **Task 3.7:** Update dashboard file paths and references
  - Consolidate: File locations (keep one dashboard directory)
  - Update: References in documentation, configs, scripts
  - Remove: Unused dashboard files (archive, don't delete)

---

## Phase 4: Visual Progress Integration (UX Enhancement)

**Status:** ☐ NOT STARTED  
**Duration:** 40 minutes  
**Dependencies:** None (parallel with Phase 3)  
**Source:** Phase 4 from cortex-ux-enhancement-plan.md

### Objective
Add real-time progress visualization to dashboard consolidation orchestrator, showing percentage, phase number, ETA, and current operation.

### Tasks
- [ ] **Task 4.1:** Review existing progress monitoring in `src/utils/progress_decorator.py`
  - Verify: @with_progress decorator functionality
  - Check: Auto-activation for operations >5 seconds
  - Confirm: Thread-safe, <0.1% performance impact
  
- [ ] **Task 4.2:** Design progress bar format for dashboard consolidation
  - Format: `[████████░░] 80% - Phase 3 of 9 Complete`
  - ASCII blocks: █ (filled), ░ (empty)
  - Include: ETA, current operation, completed tasks
  
- [ ] **Task 4.3:** Create reusable progress bar YAML anchor in response-templates.yaml
  - Anchor: &dashboard_progress_bar
  - Reusable across all dashboard-related templates
  
- [ ] **Task 4.4:** Update dashboard consolidation template with progress component
  - Template: dashboard_consolidation_progress
  - Include: Progress bar, phase summary, ETA
  
- [ ] **Task 4.5:** Integrate with @with_progress decorator
  - Wrap: Each phase execution with progress tracking
  - Yield: Progress updates at task boundaries
  - Display: Real-time updates in VS Code terminal
  
- [ ] **Task 4.6:** Test rendering in VS Code markdown preview
  - Verify: Progress bars render correctly
  - Check: Clickable links work as expected
  
- [ ] **Task 4.7:** Document progress monitoring usage for dashboard operations
  - Add: Comments in response-templates.yaml
  - Update: Dashboard consolidation guide with progress examples

### Checkpoint
✓ Visual progress bars operational  
✓ Real-time ETA and phase tracking active  
✓ Progress monitoring integrated with decorator system

---

## Phase 5: Response Template Optimization (UX Enhancement)

**Status:** ☐ NOT STARTED  
**Duration:** 35 minutes  
**Dependencies:** Phase 4 (progress system)  
**Source:** Phase 5 from cortex-ux-enhancement-plan.md

### Objective
Show high-level summaries in chat, move detailed task/code information to plan file, auto-open plan file for user review.

### Tasks
- [ ] **Task 5.1:** Review current dashboard consolidation response templates
  - Identify: Templates showing excessive detail in chat
  - Issue: Chat becomes cluttered with granular task/code info
  
- [ ] **Task 5.2:** Design high-level chat format for dashboard operations
  - Format: Progress bar + Phase name + Link to plan file
  - Example: "Phase 3 Complete - [View Details](file:///path/to/plan.md)"
  
- [ ] **Task 5.3:** Update dashboard templates to write detailed updates to plan file
  - Templates write: Checkmarks + task details to plan file
  - Chat shows: Only phase summaries with progress bars
  
- [ ] **Task 5.4:** Implement auto-open plan file after template rendering
  - Plan file: Created and opened at execution start
  - User access: Clickable link anytime via chat message
  
- [ ] **Task 5.5:** Test template optimization with dashboard consolidation execution
  - Verify: Chat shows high-level summaries
  - Verify: Plan file has full task details
  - Confirm: No information loss
  
- [ ] **Task 5.6:** Document template optimization patterns for dashboard workflows
  - Pattern: Summary in chat, details in artifacts
  - Applies to: All multi-phase dashboard operations
  
- [ ] **Task 5.7:** Add clickable plan file links to all dashboard templates
  - Format: `📋 **Plan File:** [View in Editor](file:///path)`
  - Location: Immediately after CORTEX header in responses

### Checkpoint
✓ Chat responses optimized (high-level summaries only)  
✓ Plan file contains detailed task information  
✓ Auto-open functionality working for all dashboard operations

---

## Phase 6: Interactive Planning Mode (UX Enhancement)

**Status:** ☐ NOT STARTED  
**Duration:** 30 minutes  
**Dependencies:** Phase 5 (template system)  
**Source:** Phase 6 from cortex-ux-enhancement-plan.md

### Objective
Eliminate need to say "add to plan" during dashboard planning sessions, auto-assume user input is for plan until approval.

### Tasks
- [ ] **Task 6.1:** Design dashboard planning session state management
  - State: dashboard_planning_mode_active flag
  - Activated: On dashboard consolidation trigger engagement
  - Persists: Until "approve plan" or "finalize plan"
  
- [ ] **Task 6.2:** Add planning mode activation on dashboard orchestrator engagement
  - Trigger: "dashboard consolidation", "consolidate dashboards", etc.
  - Persists: Throughout planning session
  
- [ ] **Task 6.3:** Modify intent router to route all input to dashboard planning during session
  - All user input: Treated as plan refinement
  - No prefix: No need for "add to plan" or similar
  
- [ ] **Task 6.4:** Add planning mode exit commands for dashboard operations
  - Commands: "approve plan", "finalize plan", "plan approved"
  - Action: Exits planning mode, begins execution
  
- [ ] **Task 6.5:** Update dashboard response templates to indicate planning mode status
  - Header: "📋 Dashboard Planning Mode Active - Say 'approve plan' when ready"
  - Visual indicator: Clear separation between planning and execution
  
- [ ] **Task 6.6:** Test interactive planning with multiple user inputs
  - Test: User adds requirements without "add to plan" prefix
  - Verify: All inputs correctly integrated into plan
  
- [ ] **Task 6.7:** Document interactive planning mode for dashboard operations
  - Add to: Dashboard consolidation guide
  - Include: Examples of multi-turn planning sessions

### Checkpoint
✓ Interactive planning mode operational  
✓ Users can refine dashboard plan without explicit prefixes  
✓ Clear planning/execution mode separation

---

## Phase 7: Flask Removal & Cleanup

**Status:** ☐ NOT STARTED  
**Duration:** 75 minutes  
**Dependencies:** Phase 2 (Flask inventory), Phase 3 (dashboard consolidation)

### Objective
Remove ALL Flask code, configurations, and dependencies from the repository with clean git history.

### Tasks
- [ ] **Task 7.1:** Create pre-removal git checkpoint
  - Command: `git tag -a flask-removal-checkpoint-$(date +%Y%m%d-%H%M%S) -m "Before Flask removal"`
  - Verify: Checkpoint created successfully
  - Purpose: Easy rollback if issues discovered
  
- [ ] **Task 7.2:** Remove Flask imports from all files
  - Use: Impact matrix from Phase 2
  - Delete: All `import flask` and `from flask import` lines
  - Verify: No Flask imports remain (grep search)
  
- [ ] **Task 7.3:** Delete Flask app instances and route definitions
  - Remove: Flask app creation, blueprint definitions
  - Remove: All `@app.route` and `@blueprint.route` decorators
  - Remove: Flask-specific functions (render_template, jsonify, etc.)
  
- [ ] **Task 7.4:** Remove Flask templates from templates/ directory
  - Identify: Templates only used by Flask (Jinja2 syntax)
  - Archive: Move to `cortex-brain/archives/flask-templates/`
  - Document: Archived template inventory
  
- [ ] **Task 7.5:** Uninstall Flask from requirements.txt
  - Remove: `Flask==X.X.X` line
  - Remove: All Flask extensions (flask_cors, flask_sqlalchemy, etc.)
  - Verify: `pip freeze | grep -i flask` returns nothing
  
- [ ] **Task 7.6:** Remove Flask configuration files
  - Remove: Flask-specific configs (app.config, FLASK_ENV, etc.)
  - Update: Any configs referencing Flask settings
  
- [ ] **Task 7.7:** Update tests to remove Flask test client usage
  - Search: `app.test_client()`, `client.get()`, `client.post()`
  - Replace: With alternative testing strategy (requests library, pytest-mock)
  - Verify: All tests pass after update
  
- [ ] **Task 7.8:** Clean up Flask-related utility files
  - Remove: Flask helper modules, decorators, middleware
  - Archive: Keep in `cortex-brain/archives/flask-utils/`
  
- [ ] **Task 7.9:** Create Flask removal summary report
  - Document: Files deleted, lines removed, dependencies uninstalled
  - List: Archived files with restoration instructions
  - Save: `cortex-brain/documents/reports/flask-removal-report.md`

### Checkpoint
✓ All Flask code removed from repository  
✓ Flask dependencies uninstalled  
✓ Archived Flask files for historical reference  
✓ Git checkpoint created for rollback safety

---

## Phase 8: Deploy Validator Updates

**Status:** ☐ NOT STARTED  
**Duration:** 60 minutes  
**Dependencies:** Phase 7 (Flask removed)

### Objective
Update or remove deploy validators that depend on Flask, ensuring deployment pipeline remains functional.

### Tasks
- [ ] **Task 8.1:** Review Flask-dependent validators from Phase 2 inventory
  - List: All validators identified in Task 2.5
  - Categorize: Removable vs Replaceable
  
- [ ] **Task 8.2:** Identify validator replacement strategies
  - Category 1: Validators checking Flask routes → Replace with static file validation
  - Category 2: Validators checking Flask app startup → Remove (no longer applicable)
  - Category 3: Validators checking Flask dependencies → Replace with alternative checks
  
- [ ] **Task 8.3:** Remove Flask startup validators
  - Delete: Validators that check `app.run()`, Flask server startup
  - Rationale: No Flask server to validate
  - Update: Deployment checklist to remove Flask startup requirement
  
- [ ] **Task 8.4:** Replace Flask route validators
  - Old: Validators checking `@app.route` definitions
  - New: Validators checking static HTML files exist
  - Implement: File existence checks for dashboard HTML/JS/CSS
  
- [ ] **Task 8.5:** Update Flask dependency validators
  - Old: Validators checking Flask in requirements.txt
  - New: Validators ensuring Flask NOT in requirements.txt
  - Invert: Logic from "must have Flask" to "must not have Flask"
  
- [ ] **Task 8.6:** Test deploy validators with Flask removed
  - Run: Full deployment validation suite
  - Verify: No validators fail due to missing Flask
  - Fix: Any remaining Flask-related validator failures
  
- [ ] **Task 8.7:** Update deploy validator documentation
  - Document: Which validators were removed
  - Document: Which validators were replaced and why
  - Update: `docs/deployment/validators.md`
  
- [ ] **Task 8.8:** Create validator update summary
  - List: Removed validators with justification
  - List: Replaced validators with new implementation
  - Save: `cortex-brain/documents/reports/validator-update-report.md`

### Checkpoint
✓ All Flask-dependent validators updated or removed  
✓ Deployment pipeline functional without Flask  
✓ Validator documentation updated  
✓ Summary report generated

---

## Phase 9: Mock Data POC

**Status:** ☐ NOT STARTED  
**Duration:** 90 minutes  
**Dependencies:** Phase 3 (consolidated dashboard), Phase 7 (Flask removed)

### Objective
Create mock data subfolder with production-matching data structure to demonstrate dashboard functionality without live backend.

### Tasks
- [ ] **Task 9.1:** Analyze production data structure
  - Review: Live dashboard data sources (APIs, databases)
  - Document: Data schemas, field types, relationships
  - Identify: Critical data fields for dashboard rendering
  
- [ ] **Task 9.2:** Create mock data directory structure
  - Path: `cortex-brain/dashboards/mock-data/`
  - Subdirectories: Match production categories (metrics, users, events, etc.)
  
- [ ] **Task 9.3:** Generate sample JSON data files
  - Match: Production data schema exactly
  - Include: Representative sample data (10-50 records per category)
  - Format: Pretty-printed JSON for readability
  
- [ ] **Task 9.4:** Create mock data loading utility
  - File: `cortex-brain/dashboards/mock-data/load_mock_data.py`
  - Function: Load JSON files, validate schema, return data
  - Error handling: Graceful failures if files missing
  
- [ ] **Task 9.5:** Update consolidated dashboard to use mock data
  - Add: Mock data mode toggle (environment variable or config)
  - Modify: Data fetch functions to use mock data when enabled
  - Fallback: Graceful degradation if mock data unavailable
  
- [ ] **Task 9.6:** Test dashboard with mock data
  - Enable: Mock data mode
  - Verify: All dashboard features render correctly
  - Check: No console errors, proper data display
  
- [ ] **Task 9.7:** Document mock data structure
  - Create: `cortex-brain/dashboards/mock-data/README.md`
  - Explain: Mock data purpose, structure, usage
  - Include: Instructions to add new mock data files
  
- [ ] **Task 9.8:** Add mock data to .gitignore exceptions
  - Ensure: Mock data files tracked in git (not ignored)
  - Rationale: Mock data is reference implementation, not sensitive
  
- [ ] **Task 9.9:** Create POC demonstration script
  - Script: `scripts/demo_dashboard_with_mock_data.sh`
  - Actions: Start dashboard, enable mock data, open browser
  - Instructions: How to run POC demo

### Checkpoint
✓ Mock data subfolder created with production-matching structure  
✓ Dashboard renders correctly with mock data  
✓ POC demonstration script functional  
✓ Mock data documentation complete

---

## 🎯 Success Criteria

**Dashboard Consolidation:**
- [ ] Single consolidated dashboard operational
- [ ] All original requirements from both dashboards preserved
- [ ] Feature parity verified via manual testing
- [ ] Dashboard documentation updated

**Flask Removal:**
- [ ] Zero Flask imports in codebase (`grep -r "flask" --include="*.py"` returns nothing)
- [ ] Flask uninstalled from requirements.txt
- [ ] All Flask-related files archived (not deleted)
- [ ] Flask removal report generated

**Deploy Validators:**
- [ ] All Flask-dependent validators removed or replaced
- [ ] Deployment pipeline passes all validation gates
- [ ] Validator documentation updated
- [ ] Validator update report generated

**Mock Data POC:**
- [ ] Mock data directory created with production-matching structure
- [ ] Dashboard renders correctly with mock data
- [ ] POC demonstration script working
- [ ] Mock data documentation complete

**UX Enhancements:**
- [ ] Visual progress bars showing phase/ETA in real-time
- [ ] Response templates optimized (summaries in chat, details in plan file)
- [ ] Interactive planning mode active (no "add to plan" needed)
- [ ] Plan file with clickable links and checkboxes

---

## 📝 Execution Notes

**Session Restoration:**
This plan can be resumed from any chat window. To resume:
1. Open new Copilot Chat
2. Reference this plan file
3. Say "continue" or "resume plan"
4. CORTEX will resume from last checkpoint

**Progress Tracking:**
- Real-time progress bars show completion percentage and ETA
- Plan file updates with checkmarks as tasks complete
- Phase checkpoints include timestamp and summary

**Interactive Planning:**
Once this plan is active, all your input is assumed for the plan until you say "approve plan". No need to prefix with "add to plan".

**Parallel Execution:**
- Phases 4, 5, 6 (UX Enhancements) can run in parallel with Phases 1-3 (Dashboard work)
- Flask removal (Phase 7) must wait for dashboard consolidation (Phase 3)
- Deploy validators (Phase 8) must wait for Flask removal (Phase 7)
- Mock POC (Phase 9) can start after Phase 3 completes

---

## 📚 References

**Source Plans:**
- `cortex-brain/documents/planning/cortex-ux-enhancement-plan.md` (Phases 4-6)

**Documentation:**
- `.github/prompts/modules/planning-orchestrator-guide.md` - Planning System 2.0
- `.github/prompts/modules/response-format.md` - Response templates
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules

**Reports (To Be Generated):**
- `cortex-brain/documents/reports/flask-removal-report.md`
- `cortex-brain/documents/reports/validator-update-report.md`
- `cortex-brain/documents/reports/dashboard-consolidation-report.md`

---

**Plan Ready for Execution**  
Say "approve plan" to begin Phase 1
- Flask templates archived in `cortex-brain/archives/flask-templates/`
- Flask utilities archived in `cortex-brain/archives/flask-utils/`
- Restoration instructions in flask-removal-summary.md

**Deployment Safety:**
- Deploy validators prevent broken deployments
- Mock data POC allows testing before production changes

---

## Next Steps

1. **Start Phase 1:** Inventory dashboards and extract requirements
2. **Create git checkpoint:** Before any modifications
3. **Review Flask inventory:** Understand full scope of removal
4. **Begin consolidation:** Merge dashboards preserving all features
5. **Validate frequently:** Test after each phase completion

**Ready to proceed?** Say "start Phase 1" or "approve plan" to begin execution.

**Resume later?** This plan is saved at:  
📋 [View in Editor](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/dashboard-consolidation-plan.md)

---

**Plan Created:** December 4, 2025  
**Author:** Asif Hussain (via CORTEX)  
**Version:** 1.0  
**Session Restoration:** Enabled (reference this plan in new chat to continue)
