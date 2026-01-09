# ✅ CORRECTED CORTEX 6.0 Epic Folder Structure

**Date:** 2026-01-09 | **Version:** Final Approved Structure

---

## 📁 EPIC PLAN STRUCTURE (Flattened Model)

```
cortex-brain/documents/planning/active/cortex6-build-epic/
│
├── CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml    # ✅ Master file (NO "00-" prefix)
├── epic.yaml                              # Epic config (constraints, handoff, progress)
├── continuation-prompt.md                 # Session resumption context
├── plan-viewer.html                       # ✅ Interactive visual dashboard (ROOT)
├── thoughts.txt                           # ✅ Intermittent thoughts/notes (ROOT)
│
├── features/                              # ✅ ALL FEATURES HERE (flattened)
│   │
│   ├── feat01-foundation/
│   │   ├── feature.yaml                   # Feature metadata, phases list, dependencies
│   │   ├── requirements.yaml              # Detailed requirements
│   │   ├── context/                       # Feature-specific docs
│   │   │   └── foundation-overview.md
│   │   ├── phases/                        # ✅ PHASE JSON FILES (numbered, snake_case)
│   │   │   ├── 01-phase-test-infrastructure.json
│   │   │   ├── 02-phase-state-manager.json
│   │   │   ├── 03-phase-audit-logger.json
│   │   │   └── 04-phase-pattern-router.json
│   │   └── tracking/                      # Per-feature progress
│   │       └── progress-tracker.json
│   │
│   ├── feat02-todo-orchestrator/
│   │   ├── feature.yaml
│   │   ├── requirements.yaml
│   │   ├── context/
│   │   │   └── todo-orchestrator-overview.md
│   │   ├── phases/
│   │   │   ├── 01-phase-dag-engine.json
│   │   │   ├── 02-phase-dependency-resolver.json
│   │   │   ├── 03-phase-task-executor.json
│   │   │   └── 04-phase-state-persistence.json
│   │   └── tracking/
│   │       └── progress-tracker.json
│   │
│   ├── feat03-governance-system/
│   │   ├── feature.yaml
│   │   ├── requirements.yaml
│   │   ├── context/
│   │   │   └── governance-overview.md
│   │   ├── phases/
│   │   │   ├── 01-phase-skull-rules.json
│   │   │   ├── 02-phase-validation-engine.json
│   │   │   └── 03-phase-compliance-tracker.json
│   │   └── tracking/
│   │       └── progress-tracker.json
│   │
│   ├── feat04-core-orchestration/
│   │   ├── feature.yaml
│   │   ├── requirements.yaml
│   │   ├── context/
│   │   │   └── orchestration-overview.md
│   │   ├── phases/
│   │   │   ├── 01-phase-base-orchestrator.json
│   │   │   ├── 02-phase-master-orchestrator.json
│   │   │   ├── 03-phase-registry.json
│   │   │   └── 04-phase-middleware.json
│   │   └── tracking/
│   │       └── progress-tracker.json
│   │
│   ├── feat05-resilience-performance/
│   │   ├── feature.yaml
│   │   ├── requirements.yaml
│   │   ├── context/
│   │   │   └── resilience-overview.md
│   │   ├── phases/
│   │   │   ├── 01-phase-retry-logic.json
│   │   │   ├── 02-phase-circuit-breaker.json
│   │   │   └── 03-phase-performance-cache.json
│   │   └── tracking/
│   │       └── progress-tracker.json
│   │
│   ├── feat06-mcp-multi-repo/
│   │   ├── feature.yaml
│   │   ├── requirements.yaml
│   │   ├── context/
│   │   │   └── mcp-overview.md
│   │   ├── phases/
│   │   │   ├── 01-phase-mcp-server.json
│   │   │   ├── 02-phase-multi-repo-detect.json
│   │   │   └── 03-phase-repo-isolation.json
│   │   └── tracking/
│   │       └── progress-tracker.json
│   │
│   ├── feat07-integration-polish/
│   │   ├── feature.yaml
│   │   ├── requirements.yaml
│   │   ├── context/
│   │   │   └── integration-overview.md
│   │   ├── phases/
│   │   │   ├── 01-phase-orchestrator-wire.json
│   │   │   ├── 02-phase-end-to-end-tests.json
│   │   │   └── 03-phase-documentation.json
│   │   └── tracking/
│   │       └── progress-tracker.json
│   │
│   └── feat08-vacuum-cleanup/
│       ├── feature.yaml
│       ├── requirements.yaml
│       ├── context/
│       │   └── vacuum-overview.md
│       ├── phases/
│       │   ├── 01-phase-duplicate-detector.json
│       │   ├── 02-phase-orphan-cleanup.json
│       │   └── 03-phase-archive-manager.json
│       └── tracking/
│           └── progress-tracker.json
│
├── analysis/                              # Epic-level analysis
│   ├── domain-knowledge.json              # 🧠 ACCUMULATED KNOWLEDGE GRAPH
│   ├── ast-insights.yaml                  # Code structure insights
│   ├── dependencies-graph.mermaid         # Feature dependencies visualization
│   └── gap-analysis.md                    # Identified gaps
│
├── artifacts/                             # Epic-level deliverables
│   ├── architecture-diagrams.md
│   └── design-documents/
│
├── tracking/                              # Epic-level tracking
│   ├── progress-tracker.json              # Overall epic progress
│   ├── effort-log.md                      # Time tracking per feature/phase
│   ├── stage1-status.md                   # Stage-based status
│   └── audit-log.jsonl                    # Audit trail (JSONL format)
│
└── reports/                               # Epic-level reports
    ├── status-reports/
    │   └── weekly-status-YYYY-MM-DD.md
    ├── completion-reports/
    │   └── feature-completion-feat01.md
    └── holistic-reviews/
        └── epic-review-YYYY-MM-DD.md
```

---

## 📋 NAMING CONVENTIONS

### ✅ **Master File:**
- **Format:** `{EPIC-ID}-MASTER-SOURCE-OF-TRUTH.yaml`
- **Example:** `CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml`
- **NO** `00-` prefix

### ✅ **Feature Folders:**
- **Format:** `feat{NN}-{name-snake-case}/`
- **Examples:**
  - `feat01-foundation/`
  - `feat02-todo-orchestrator/`
  - `feat03-governance-system/`
- **Max Length:** 25 characters (after `feat##-`)

### ✅ **Phase JSON Files:**
- **Format:** `{NN}-phase-{name-snake-case}.json`
- **Examples:**
  - `01-phase-test-infrastructure.json`
  - `02-phase-state-manager.json`
  - `03-phase-dag-engine.json`
- **Max Length:** 25 characters for `{name-snake-case}` portion
- **Location:** `features/feat##-{name}/phases/`

### ✅ **Root Files (Required):**
- `plan-viewer.html` - Interactive dashboard
- `thoughts.txt` - Intermittent notes/thoughts
- `continuation-prompt.md` - Session resumption

---

## 📄 PHASE JSON FILE STRUCTURE

**Example:** `01-phase-test-infrastructure.json`

```json
{
  "phase_id": "01-phase-test-infrastructure",
  "phase_number": 1,
  "name": "Test Infrastructure Setup",
  "feature_id": "feat01-foundation",
  "epic_id": "cortex6-build-epic",
  "status": "NOT_STARTED",
  "progress": 0,
  "estimated_hours": 16,
  "actual_hours": 0,
  "metadata": {
    "created_date": "2026-01-07",
    "last_updated": "2026-01-07",
    "executor": "GitHub Copilot"
  },
  "objectives": [
    "Create tests/ folder with proper structure",
    "Setup pytest configuration",
    "Create shared fixtures",
    "Migrate existing tests"
  ],
  "entry_criteria": [
    "Access to repository",
    "Python environment configured"
  ],
  "exit_criteria": [
    "tests/ folder exists with subdirs",
    "pytest --collect-only discovers tests",
    "No test files outside tests/ folder"
  ],
  "tasks": [
    {
      "id": "1.1",
      "name": "Create test folder structure",
      "priority": "P0_CRITICAL",
      "estimated_minutes": 30,
      "status": "NOT_STARTED",
      "tdd_required": false,
      "dependencies": [],
      "validation": {
        "type": "directory_exists",
        "paths": ["tests/", "tests/unit/", "tests/integration/"]
      }
    },
    {
      "id": "1.2",
      "name": "Create pytest.ini configuration",
      "priority": "P0_CRITICAL",
      "estimated_minutes": 20,
      "status": "NOT_STARTED",
      "dependencies": ["1.1"],
      "validation": {
        "type": "file_contains",
        "path": "tests/pytest.ini",
        "contains": ["[pytest]", "testpaths", "markers"]
      }
    }
  ],
  "outputs": [
    {
      "path": "tests/",
      "type": "directory",
      "description": "Test folder structure"
    },
    {
      "path": "tests/pytest.ini",
      "type": "config",
      "description": "Pytest configuration"
    }
  ],
  "audit": {
    "correlation_id": "FEAT01-P1",
    "validation": [
      "All operations logged with VALIDATION category",
      "Zero ERROR entries",
      "Folder creation events recorded"
    ]
  }
}
```

---

## 🎯 FEATURE PLAN STRUCTURE (Standalone)

**When creating a standalone FEATURE plan** (not part of epic):

```
cortex-brain/documents/planning/active/feat-user-authentication/
│
├── FEAT-USER-AUTH-MASTER-SOURCE-OF-TRUTH.yaml   # ✅ Master file (NO "00-")
├── feature.yaml                                  # Feature config
├── requirements.yaml                             # Requirements breakdown
├── continuation-prompt.md                        # Session resumption
├── plan-viewer.html                              # ✅ Interactive dashboard (ROOT)
├── thoughts.txt                                  # ✅ Notes (ROOT)
│
├── phases/                                       # ✅ PHASE JSON FILES
│   ├── 01-phase-design-architecture.json
│   ├── 02-phase-implementation.json
│   ├── 03-phase-testing.json
│   └── 04-phase-deployment.json
│
├── context/                                      # Feature context
│   └── authentication-overview.md
│
├── analysis/                                     # Feature analysis
│   ├── domain-knowledge.json                     # 🧠 LEARNED KNOWLEDGE
│   └── ast-insights.yaml
│
├── artifacts/                                    # Feature deliverables
│   └── design-docs/
│
├── tracking/                                     # Feature tracking
│   └── progress-tracker.json
│
└── reports/                                      # Feature reports
    └── status-reports/
```

---

## 📝 KEY DIFFERENCES FROM PREVIOUS VERSIONS

### ❌ **REMOVED:**
- `00-` prefix on master files
- Nested phase folders (e.g., `phases/phase1-design/`)
- Phase files as YAML in feature.yaml

### ✅ **ADDED:**
- `plan-viewer.html` at root
- `thoughts.txt` at root
- `phases/` folder with numbered JSON files
- Snake_case naming (max 25 chars)
- Consistent `NN-phase-{name}.json` format

### ✅ **KEPT:**
- Flattened epic structure (no nested features→phases folders)
- `features/feat##-{name}/` organization
- `domain-knowledge.json` in analysis/
- Progress tracking per feature

---

## 🎨 VISUAL TREE (Simplified)

```
cortex6-build-epic/
├── 📄 CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml
├── 📄 epic.yaml
├── 📄 continuation-prompt.md
├── 🌐 plan-viewer.html
├── 📝 thoughts.txt
├── 📁 features/
│   ├── 📁 feat01-foundation/
│   │   ├── feature.yaml
│   │   ├── 📁 phases/
│   │   │   ├── 01-phase-test-infra.json
│   │   │   ├── 02-phase-state-mgr.json
│   │   │   ├── 03-phase-audit-log.json
│   │   │   └── 04-phase-pattern-route.json
│   │   └── 📁 tracking/
│   ├── 📁 feat02-todo-orchestrator/
│   └── 📁 feat08-vacuum-cleanup/
├── 📁 analysis/
│   └── 🧠 domain-knowledge.json
├── 📁 tracking/
└── 📁 reports/
```

---

## ✅ VALIDATION CHECKLIST

- [x] Master file: `{EPIC-ID}-MASTER-SOURCE-OF-TRUTH.yaml` (NO `00-`)
- [x] Root has: `plan-viewer.html`
- [x] Root has: `thoughts.txt`
- [x] Root has: `continuation-prompt.md`
- [x] Features: `feat##-{name}/` (snake_case, max 25 chars)
- [x] Phases: `phases/NN-phase-{name}.json` (snake_case, max 25 chars)
- [x] No nested phase folders (phases as JSON, not directories)
- [x] Knowledge graph: `analysis/domain-knowledge.json`
- [x] Flattened structure (no epic→features→phases folder nesting)

---

**This is the FINAL, APPROVED folder structure for CORTEX 6.0 planning system.**

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
