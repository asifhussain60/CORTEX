# CORTEX Orchestrators Quick Reference

**Version:** 5.0.0 | **Date:** 2026-01-03  
**Purpose:** Comprehensive orchestrator documentation (externalized from CORTEX.prompt.md)  
**Audience:** GitHub Copilot + CORTEX Master Orchestrator

---

## 📚 Overview

CORTEX uses **10 orchestrators** organized into **2 categories**:
- **🛡️ AUTONOMOUS (5):** Python-implemented, self-executing with progress tracking
- **📋 GUIDED (5):** Manifest-driven, Copilot interprets and executes

### 🛡️ Shield Icon Meaning

When you see the **🛡️ shield icon**:
- Master Orchestrator has **handed off execution** to Python
- GitHub Copilot's role is **complete** (routing only)
- Progress updates come from **autonomous Python orchestrator**
- User should expect **different response format** (progress tracking)

**Visual Indicator:** Response headers for autonomous orchestrators use `## 🛡️🧠 CORTEX {Name}` format.

---

## 🛡️ AUTONOMOUS Orchestrators

### 1. Planning System v5

**Pattern:** `^(plan|create a plan|make a plan).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`  
**Implementation:** `src/orchestrators/planning/planning_orchestrator_v5.py`  
**Template:** `response-templates-v4.yaml:1449` (`autonomous_execution_progress`)

#### Purpose
Creates structured execution plans with context discovery, folder organization, and state tracking.

#### Behavior
1. **Context Discovery:** Search workspace for relevant files (semantic + grep)
2. **Architecture Analysis:** Parse codebase and analyze dependencies
3. **Plan Generation:** Generate master plan from templates (Jinja2)
4. **Folder Creation:** Create 5-subfolder structure (`analysis/`, `artifacts/`, `context/`, `reports/`, `tracking/`)
5. **Validation:** Validate plan structure and content

#### Inputs
- `feature_name` (string): Feature to plan (e.g., "user authentication")
- `user_request` (string): Original user request
- `complexity_tier` (1-5): Complexity estimate (optional, default: auto-detect)

#### Outputs
```
cortex-brain/documents/planning/active/{plan-name}/
├── 00-{plan-name}.md          # Master plan (meaningful filename, max 22 chars)
├── README.md                   # Quick start guide
├── analysis/                   # Deep analysis and investigation reports
├── artifacts/                  # Generated artifacts
├── context/                    # Context discovery documents
│   ├── discovery.md
│   └── architecture-analysis.md
├── reports/                    # Progress reports
│   └── validation-report.md
└── tracking/                   # State tracking
    ├── progress-tracker.json
    └── CONTINUATION-PROMPT.md
```

#### Progress Display
```markdown
## 🛡️🧠 CORTEX Plan Execution
**Author:** Asif Hussain | **Plan:** user-authentication | **Orchestrator:** Planning System v5 ✅

---

### 📊 Execution Progress

**Overall Progress:** `████████░░░░░░░░░░░░` **40%** ⏳ IN PROGRESS

| # | Phase | Progress | Deliverables | Time |
|---|-------|----------|--------------|------|
| 1 | ✅ **Context Discovery** | `██████████` 100% | 2/2 | 0.5h |
| 2 | ⏳ **Architecture Analysis** | `████░░░░░░` 40% | 0/1 | 0.2h |
| 3 | ⏸️ **Plan Generation** | `░░░░░░░░░░` 0% | 0/2 | 0h |
| 4 | ⏸️ **Folder Creation** | `░░░░░░░░░░` 0% | 0/5 | 0h |
| 5 | ⏸️ **Validation** | `░░░░░░░░░░` 0% | 0/1 | 0h |

**Next:** Complete architecture analysis → Parse codebase
```

#### Key Features
- ✅ AST-based code parsing
- ✅ Tier 0 Governance integration (61 rules)
- ✅ Tier 2 Knowledge Graph queries
- ✅ Cross-session continuation prompts
- ✅ State persistence via PlanningStateDB
- ✅ Meaningful filenames (max 22 chars, kebab-case)

---

### 2. ADO Operations v2

**Pattern:** `^(ado|ado story|ado feature).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml`  
**Implementation:** `src/orchestrators/ado/ado_orchestrator_v2.py`  
**Template:** `response-templates-v4.yaml:1514` (`ado_execution_progress`)

#### Purpose
Generates Azure DevOps work items (Epics, Features, User Stories, Tasks) from feature descriptions.

#### Behavior (Dual-Mode)

**Mode 1: Wizard (Interactive)**
1. Ask feature name
2. Ask story point estimate
3. Ask acceptance criteria
4. Ask dependencies
5. Generate work items
6. Save to ADO-compatible JSON

**Mode 2: Auto (Single Shot)**
1. Extract all details from user request
2. Generate work items immediately
3. Save to ADO-compatible JSON

#### Inputs
- `feature_name` (string): Feature to create work items for
- `mode` (string): `"wizard"` or `"auto"` (default: auto if all details provided)
- `story_points` (int, optional): Total story points estimate
- `acceptance_criteria` (list, optional): Acceptance criteria list

#### Outputs
```
cortex-brain/documents/ado/work-items/{feature-name}/
├── epic-{name}.json            # Epic JSON
├── feature-{name}.json         # Feature JSON
├── story-{name}-{id}.json      # User Story JSON (5-8 stories)
├── task-{name}-{id}.json       # Task JSON (12-20 tasks)
└── README.md                   # Summary report
```

#### Progress Display
```markdown
## 🛡️🧠 CORTEX ADO Work Item Generation
**Author:** Asif Hussain | **Feature:** user-authentication | **Orchestrator:** ADO v2 ✅

---

### 📊 ADO Generation Progress

**Overall Progress:** `████████████████████` **100%** ✅ COMPLETE

| # | Phase | Progress | Deliverables | Time |
|---|-------|----------|--------------|------|
| 1 | ✅ **Feature Analysis** | `██████████` 100% | 1/1 | 0.5h |
| 2 | ✅ **Story Generation** | `██████████` 100% | 5/5 | 1.2h |
| 3 | ✅ **Task Breakdown** | `██████████` 100% | 12/12 | 0.8h |

### 🎫 Work Item Summary

| Type | Count | Story Points | Status |
|------|-------|--------------|--------|
| **Epic** | 1 | - | ✅ Created |
| **Feature** | 1 | 21 SP | ✅ Created |
| **User Story** | 5 | 21 SP | ✅ Created |
| **Task** | 12 | - | ✅ Created |
```

#### Key Features
- ✅ Dual-mode routing (wizard vs auto)
- ✅ Conversational wizard with state tracking
- ✅ ADO-compatible JSON output
- ✅ Story point estimation
- ✅ Dependency tracking

---

### 3. Vacuum v2

**Pattern:** `^(vacuum|deep clean|organize files).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml`  
**Implementation:** `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`  
**Template:** `response-templates-v4.yaml:1449` (`autonomous_execution_progress`)

#### Purpose
Deep filesystem cleanup with duplicate detection, safe deletion, and reorganization.

#### Behavior
1. **Scan Filesystem:** Walk directory tree, collect file metadata
2. **Detect Duplicates:** Progressive hashing (size → quick → full)
3. **Risk Classification:** 5-level risk assessment (SAFE/LOW/MEDIUM/HIGH/CRITICAL)
4. **Organize:** Move files to category-based structure
5. **Cleanup:** Safe deletion with checkpoint system
6. **Validate:** Verify integrity post-cleanup

#### Inputs
- `target_path` (string): Path to clean (default: workspace root)
- `mode` (string): `"scan"`, `"organize"`, `"cleanup"`, or `"full"` (default: scan)
- `dry_run` (bool): Simulate without changes (default: true)

#### Outputs
```
reports/vacuum-{timestamp}/
├── scan-report.md              # File inventory
├── duplicates-report.md        # Duplicate analysis
├── risk-classification.md      # Risk assessment
├── cleanup-plan.md             # Proposed actions
├── cleanup-log.md              # Execution log
└── validation-report.md        # Integrity check
```

#### Progress Display
```markdown
## 🛡️🧠 CORTEX Vacuum Execution
**Author:** Asif Hussain | **Target:** /workspace | **Orchestrator:** Vacuum v2 ✅

---

### 📊 Vacuum Progress

**Overall Progress:** `███████████░░░░░░░░░` **55%** ⏳ IN PROGRESS

| # | Phase | Progress | Deliverables | Time |
|---|-------|----------|--------------|------|
| 1 | ✅ **Scan** | `██████████` 100% | 1/1 | 2.5h |
| 2 | ✅ **Duplicate Detection** | `██████████` 100% | 1/1 | 3.2h |
| 3 | ⏳ **Risk Classification** | `█████░░░░░` 50% | 0/1 | 1.1h |
| 4 | ⏸️ **Organization** | `░░░░░░░░░░` 0% | 0/1 | 0h |
| 5 | ⏸️ **Cleanup** | `░░░░░░░░░░` 0% | 0/1 | 0h |
| 6 | ⏸️ **Validation** | `░░░░░░░░░░` 0% | 0/1 | 0h |
```

#### Key Features
- ✅ Progressive hashing (size → quick → full)
- ✅ 5-level risk classification
- ✅ Checkpoint system for rollback
- ✅ Dry-run mode (safe preview)
- ✅ Category-based organization

---

### 4. Cleanup v2

**Pattern:** `^(cleanup|cleanup cache|cleanup logs).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml`  
**Implementation:** `src/orchestrators/cleanup/cleanup_orchestrator_v2.py`  
**Template:** `response-templates-v4.yaml:1449` (`autonomous_execution_progress`)

#### Purpose
Selective cleanup of cache, logs, artifacts, or full workspace with safe execution order.

#### Behavior (Mode-Based)

**Mode: `cache`**
1. Identify cache directories (`.cache/`, `__pycache__/`, `node_modules/`, etc.)
2. Calculate space to reclaim
3. Delete cache files
4. Validate no dependency breakage

**Mode: `logs`**
1. Find log files (`*.log`, `logs/`, etc.)
2. Archive old logs (>30 days)
3. Delete archived logs
4. Validate no critical logs lost

**Mode: `artifacts`**
1. Find generated artifacts (build outputs, temp files)
2. Classify by last access time
3. Delete stale artifacts (>7 days)
4. Validate no active artifacts deleted

**Mode: `full`**
1. Execute all modes in safe order: cache → logs → artifacts
2. Validate after each step
3. Generate comprehensive report

**Mode: `git`**
1. Clean untracked files (`git clean -fdx`)
2. Reset working tree
3. Validate no uncommitted work lost

#### Inputs
- `mode` (string): `"cache"`, `"logs"`, `"artifacts"`, `"full"`, or `"git"` (default: cache)
- `dry_run` (bool): Simulate without changes (default: true)
- `aggressive` (bool): Enable aggressive cleanup (default: false)

#### Outputs
```
reports/cleanup-{mode}-{timestamp}/
├── cleanup-plan.md             # Proposed actions
├── cleanup-log.md              # Execution log
├── space-reclaimed.md          # Space savings
└── validation-report.md        # Integrity check
```

#### Progress Display
```markdown
## 🛡️🧠 CORTEX Cleanup Execution
**Author:** Asif Hussain | **Mode:** full | **Orchestrator:** Cleanup v2 ✅

---

### 📊 Cleanup Progress

**Overall Progress:** `████████████████████` **100%** ✅ COMPLETE

| Mode | Progress | Space Reclaimed | Status |
|------|----------|-----------------|--------|
| **Cache** | `██████████` 100% | 1.2 GB | ✅ Complete |
| **Logs** | `██████████` 100% | 450 MB | ✅ Complete |
| **Artifacts** | `██████████` 100% | 800 MB | ✅ Complete |

**Total Space Reclaimed:** 2.45 GB
```

#### Key Features
- ✅ Selective modes (cache/logs/artifacts/full/git)
- ✅ Safe execution order (prevents dependency issues)
- ✅ Atomic operations (rollback on error)
- ✅ Space calculation before/after
- ✅ Dry-run mode (safe preview)

---

### 5. Investigation v2

**Pattern:** `^(investigate|find root cause|why is|debug architecture|fix brittleness).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/investigation-orchestrator.yaml`  
**Implementation:** `src/orchestrators/investigation/investigation_orchestrator.py`  
**Template:** `response-templates-v4.yaml:1449` (`autonomous_execution_progress`)

#### Purpose
Deep root cause analysis for architectural issues, brittleness, and systemic problems with architecture-level fixes.

#### Behavior
1. **Symptom Analysis:** Collect error patterns, failure modes
2. **Context Discovery:** Search for related code, config, docs
3. **Hypothesis Generation:** LLM-assisted hypothesis ranking
4. **Evidence Collection:** Gather supporting/refuting evidence
5. **Root Cause Identification:** Determine underlying cause
6. **Fix Strategy:** Propose architecture-level solution
7. **Master Orch Integration:** Update routing + state if applicable

#### Inputs
- `symptom` (string): Observed problem (e.g., "routing failures")
- `context` (string, optional): Additional context
- `scope` (string): `"code"`, `"config"`, `"architecture"`, or `"system"` (default: system)

#### Outputs
```
cortex-brain/documents/investigations/{issue-name}/
├── 00-investigation-report.md  # Master report
├── symptom-analysis.md         # Symptom breakdown
├── context-discovery.md        # Related context
├── hypotheses.md               # Ranked hypotheses
├── evidence-log.md             # Evidence trail
├── root-cause-summary.md       # Root cause
└── fix-strategy.md             # Solution proposal
```

#### Progress Display
```markdown
## 🛡️🧠 CORTEX Investigation Execution
**Author:** Asif Hussain | **Issue:** routing-failures | **Orchestrator:** Investigation v2 ✅

---

### 📊 Investigation Progress

**Overall Progress:** `█████████████░░░░░░░` **65%** ⏳ IN PROGRESS

| # | Phase | Progress | Deliverables | Time |
|---|-------|----------|--------------|------|
| 1 | ✅ **Symptom Analysis** | `██████████` 100% | 1/1 | 0.8h |
| 2 | ✅ **Context Discovery** | `██████████` 100% | 1/1 | 1.2h |
| 3 | ✅ **Hypothesis Generation** | `██████████` 100% | 1/1 | 0.5h |
| 4 | ⏳ **Evidence Collection** | `███████░░░` 70% | 0/1 | 0.9h |
| 5 | ⏸️ **Root Cause ID** | `░░░░░░░░░░` 0% | 0/1 | 0h |
| 6 | ⏸️ **Fix Strategy** | `░░░░░░░░░░` 0% | 0/1 | 0h |
```

#### Key Features
- ✅ LLM-assisted hypothesis ranking
- ✅ Evidence-based analysis
- ✅ Architecture-level fixes
- ✅ Master Orchestrator integration (updates routing)
- ✅ Systemic problem detection

---

## 📋 GUIDED Orchestrators

### 6. TDD Mastery v4

**Pattern:** `^(tdd|start tdd|run tests).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`  
**Implementation:** Copilot interprets manifest  
**Template:** N/A (direct execution, no progress bars)

#### Purpose
Test-Driven Development workflow enforcing RED→GREEN→REFACTOR cycle.

#### Behavior
1. **RED Phase:** Write failing test first
2. **GREEN Phase:** Implement minimal code to pass
3. **REFACTOR Phase:** Clean up while keeping tests green
4. **Repeat:** Continue until feature complete

#### Inputs
- `module_path` (string): Path to module to test
- `feature` (string): Feature to implement

#### Outputs
- Test files (`tests/test_{module}.py`)
- Implementation files (`src/{module}.py`)
- No progress bars (direct execution)

#### Key Features
- ✅ TDD_ENFORCEMENT (brain-protection-rules.yaml)
- ✅ Test-first approach
- ✅ Minimal implementation principle
- ✅ Continuous refactoring

---

### 7. Sanitization v2

**Pattern:** `^(sanitize|make generic).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/sanitization-orchestrator-v2.yaml`  
**Implementation:** Copilot interprets manifest  
**Template:** N/A (single-pass, no progress bars)

#### Purpose
Remove sensitive information from code/docs for public sharing.

#### Behavior
1. **Scan:** Identify sensitive patterns (PII, secrets, paths)
2. **Replace:** Substitute with generic placeholders
3. **Validate:** Ensure no sensitive data remains

#### Inputs
- `target` (string): File or directory to sanitize
- `mode` (string): `"code"` or `"docs"` (default: code)

#### Outputs
- Sanitized files (in-place or new location)
- Sanitization report

#### Key Features
- ✅ Pattern-based detection (regex + LLM)
- ✅ Placeholder generation
- ✅ Validation checks

---

### 8. Debug Orchestrator

**Pattern:** `^(debug|fix bug|troubleshoot).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml`  
**Implementation:** Copilot interprets manifest  
**Template:** N/A (analysis output, no progress bars)

#### Purpose
Debug code issues with systematic analysis.

#### Behavior
1. **Reproduce:** Understand error context
2. **Analyze:** Inspect code, logs, stack traces
3. **Hypothesize:** Generate potential fixes
4. **Test:** Validate fixes

#### Inputs
- `error_message` (string): Error to debug
- `file_path` (string, optional): File with error

#### Outputs
- Debug analysis report
- Fix suggestions

#### Key Features
- ✅ Stack trace analysis
- ✅ Code inspection
- ✅ Fix validation

---

### 9. Refinement v2

**Pattern:** `^(refine|improve|optimize).*$`  
**Manifest:** `cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml`  
**Implementation:** Copilot interprets manifest  
**Template:** N/A (incremental, no progress bars)

#### Purpose
Improve code quality through refactoring, optimization, and best practices.

#### Behavior
1. **Analyze:** Identify improvement opportunities
2. **Refactor:** Apply best practices
3. **Optimize:** Improve performance
4. **Validate:** Ensure functionality preserved

#### Inputs
- `target` (string): File or module to refine
- `focus` (string): `"readability"`, `"performance"`, or `"both"` (default: both)

#### Outputs
- Refined code (in-place)
- Refinement report

#### Key Features
- ✅ Bloat detection
- ✅ Decomposition strategies
- ✅ Performance optimization

---

### 10. Maintenance v2

**Pattern:** `^(system maintenance|health check).*$`  
**Manifest:** `.github/prompts/maintenance/index.prompt.md`  
**Implementation:** Copilot interprets manifest (modular v2.0)  
**Template:** N/A (12-phase pipeline, custom progress format)

#### Purpose
System-wide health check with 12-phase validation pipeline.

#### Behavior
1. **Pre-Flight:** Validate workspace
2. **Git Health:** Check repository status
3. **Python Environment:** Validate dependencies
4. **Type Checking:** Run mypy
5. **Test Suite:** Run pytest
6. **Documentation:** Validate docs
7. **Configuration:** Check configs
8. **Security:** Scan for vulnerabilities
9. **Performance:** Profile critical paths
10. **Integration:** Validate integrations
11. **Compliance:** Check brain protection rules
12. **Final Report:** Generate summary

#### Inputs
- None (runs on entire workspace)

#### Outputs
```
reports/maintenance-{timestamp}/
├── 00-maintenance-report.md    # Master report
├── phase-{N}-{name}.md         # Per-phase reports (12)
└── summary.json                # Machine-readable summary
```

#### Key Features
- ✅ 12-phase pipeline
- ✅ Modular v2.0 architecture (80% faster loading)
- ✅ Atomic phase execution
- ✅ Comprehensive validation

---

## 📊 Progress Bar Rendering Guide

**⚠️ CRITICAL:** Only 🛡️ AUTONOMOUS orchestrators display progress bars.

### Format Rules

**ASCII Characters:**
- Filled: `█` (U+2588 Full Block)
- Empty: `░` (U+2591 Light Shade)

**Status Emojis:**
- ✅ Completed
- ⏳ In Progress
- ⏸️ Pending
- ❌ Failed

**Progress Bar Width:** 10 characters (fixed)

**Percentage Calculation:**
```
percentage = (completed_tasks / total_tasks) × 100
filled_blocks = round(percentage / 10)
empty_blocks = 10 - filled_blocks
```

### Example
```markdown
**Overall Progress:** `████████░░░░░░░░░░░░` **40%** ⏳ IN PROGRESS

| # | Phase | Progress | Deliverables | Time |
|---|-------|----------|--------------|------|
| 1 | ✅ **Discovery** | `██████████` 100% | 3/3 | 1.2h |
| 2 | ⏳ **Analysis** | `████░░░░░░` 40% | 1/3 | 0.5h |
| 3 | ⏸️ **Implementation** | `░░░░░░░░░░` 0% | 0/5 | 0h |
```

---

## 🔄 Orchestrator Selection Logic

```
User Request
    ↓
Parse + Clean (remove meta-directives)
    ↓
Pattern Matching (Intent Router)
    ↓ (match found)
    ↓
Orchestrator Type?
    ├─ 🛡️ AUTONOMOUS
    │     ↓
    │  Route to Master Orchestrator
    │     ↓
    │  Display Progress Header
    │     ↓
    │  Python Executes Autonomously
    │     ↓
    │  Update Progress Bars (live)
    │     ↓
    │  Return Results
    │
    └─ 📋 GUIDED
          ↓
       Load Manifest YAML
          ↓
       Copilot Interprets Instructions
          ↓
       Execute Workflow
          ↓
       Return Results (no progress bars)
```

---

## 📋 Quick Reference Table

| Orchestrator | Type | Pattern Prefix | Progress Bars | State Tracking | Outputs |
|--------------|------|----------------|---------------|----------------|---------|
| Planning v5 | 🛡️ | `plan` | ✅ YES | ✅ Database | Plan folders |
| ADO v2 | 🛡️ | `ado` | ✅ YES | ✅ Database | Work item JSON |
| Vacuum v2 | 🛡️ | `vacuum` | ✅ YES | ✅ Database | Cleanup reports |
| Cleanup v2 | 🛡️ | `cleanup` | ✅ YES | ✅ Database | Cleanup reports |
| Investigation | 🛡️ | `investigate` | ✅ YES | ✅ Database | Investigation reports |
| TDD v4 | 📋 | `tdd` | ❌ NO | ❌ None | Tests + code |
| Sanitization v2 | 📋 | `sanitize` | ❌ NO | ❌ None | Sanitized files |
| Debug | 📋 | `debug` | ❌ NO | ❌ None | Debug analysis |
| Refinement v2 | 📋 | `refine` | ❌ NO | ❌ None | Refined code |
| Maintenance v2 | 📋 | `system maintenance` | ❌ NO | ❌ None | Maintenance reports |

---

## 🚀 Adding New Orchestrators

### For 🛡️ AUTONOMOUS Orchestrators

1. **Create Implementation:** `src/orchestrators/{name}/{name}_orchestrator.py`
2. **Create Manifest:** `cortex-brain/manifests/orchestrators/{name}-v2.yaml`
3. **Register in Master Orch:** Update `cortex-brain/config/master-orchestrator.yaml`
4. **Add Pattern:** Add to Intent Router table in `CORTEX.prompt.md`
5. **Implement Progress:** Use `autonomous_execution_progress` template
6. **Add to Quick Ref:** Update this document

### For 📋 GUIDED Orchestrators

1. **Create Manifest:** `cortex-brain/manifests/orchestrators/{name}-manifest.yaml`
2. **Add Pattern:** Add to Intent Router table in `CORTEX.prompt.md`
3. **Add to Quick Ref:** Update this document

---

## 📚 Related Documentation

- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Planning System Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`

---

**Last Updated:** 2026-01-03  
**Maintained By:** CORTEX Planning System v5  
**Total Orchestrators:** 10 (5 AUTONOMOUS + 5 GUIDED)
