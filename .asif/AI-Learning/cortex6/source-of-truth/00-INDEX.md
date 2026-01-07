# CORTEX 6.0 Build Epic - Complete Index

## 📋 Epic Overview

This index provides the complete map of the CORTEX 6.0 Build Epic source of truth.
All files are designed for GitHub Copilot autonomous execution with gradual handoff to CORTEX.

---

## 🎯 Start Here

| Purpose | File | Description |
|---------|------|-------------|
| **New Session** | `CONTINUATION-PROMPT.md` | Copy to start new Copilot session |
| **Execution Guide** | `EXECUTION-GUIDE.yaml` | Detailed execution instructions |
| **Track Progress** | `todo/00-TODO-CONTINUITY-TRACKER.yaml` | Current work state |

---

## 📁 Complete File Map

### Root Level
```
source-of-truth/
├── 00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml  # Architecture & requirements
├── 00-INDEX.md                              # This file
├── CONTINUATION-PROMPT.md                   # Session start prompt
├── EXECUTION-GUIDE.yaml                     # Execution instructions
├── README.md                                # Original documentation
├── 01-EXECUTIVE-OVERVIEW.md                 # Business summary
├── 02-COPILOT-BUILD-PROMPT.md              # Clean slate prompt
```

### Epic Definition
```
epic/
└── 00-CORTEX6-BUILD-EPIC.yaml              # Epic specification
    - 8 features
    - Snowball strategy
    - Success criteria
    - Audit checkpoints
```

### Work Tracking
```
todo/
└── 00-TODO-CONTINUITY-TRACKER.yaml         # TODO tracker
    - Session management
    - Current position
    - feat01 & feat02 detailed tasks
    - Checkpoint history
```

### Risk Management
```
risk/
└── 00-RISK-REGISTRY.yaml                   # Risk registry
    - 48 identified risks
    - Edge cases (5)
    - Failure modes (5)
    - Race conditions (4)
    - Security vulnerabilities (5)
    - Performance bottlenecks (4)
    - Scalability limits (2)
    - Rollback scenarios (3)
    - Data integrity (3)
    - Dependencies (3)
    - Maintainability (3)
    - Improvement recommendations (5)
```

### Feature Specifications
```
features/
├── feat01-foundation/
│   └── feature.yaml                        # Foundation layer
│       - Phase 1: Test infrastructure
│       - Phase 2: Database layer
│       - Phase 3: Audit logger enhancement
│       - Phase 4: Pattern router
│
├── feat02-todo-orchestrator/
│   └── feature.yaml                        # TODO orchestrator (HANDOFF)
│       - Phase 1: DAG core
│       - Phase 2: TODO manager
│       - Phase 3: Checkpoint/recovery
│       - Phase 4: Self-management (HANDOFF POINT)
│
└── feat03-to-feat08/
    └── features-summary.yaml               # Remaining features
        - feat03: 4-Category Governance
        - feat04: Core Orchestration
        - feat05: Resilience & Performance
        - feat06: MCP & Multi-Repo
        - feat07: Integration & Polish
        - feat08: Vacuum & Cleanup
```

### Supporting Documentation
```
diagrams/
├── 01-governance-merge-flow.mmd            # Governance merge diagram
├── 02-system-architecture.mmd              # System architecture
├── 03-multi-repo-topology.mmd              # Multi-repo topology
└── 04-todo-dag-example.mmd                 # DAG example

human-readable/
├── 01-governance-framework.md              # Governance explained
└── 02-architecture-overview.md             # Architecture docs

machine-readable/
└── 01-folder-structure.yaml                # Directory structure

implementation-plan/
├── 01-BACKUP-MIGRATION.sh                  # Backup script
└── 02-phase-checklist.md                   # Phase checklist
```

---

## 🔄 Execution Flow

```
1. NEW SESSION
   └── Read CONTINUATION-PROMPT.md
       └── Load TODO tracker
           └── Find current_position
               └── Load feature.yaml
                   └── Execute task
                       └── Update tracker
                           └── Checkpoint (every 5 tasks)

2. PHASE COMPLETION
   └── Holistic audit review
       └── Check for ERRORs
           └── Remediate gaps
               └── Mark phase complete

3. FEATURE COMPLETION
   └── Full audit trace analysis
       └── All exit criteria met
           └── Move to next feature

4. HANDOFF (feat02 Phase 4 Task 4.5)
   └── Run validation tests
       └── Update executor to CORTEX
           └── CORTEX takes over feat03+
```

---

## 📊 Progress Tracking

### Feature Status Template
```yaml
feat01-foundation:        NOT_STARTED  → IN_PROGRESS → COMPLETED
feat02-todo-orchestrator: NOT_STARTED  → IN_PROGRESS → COMPLETED → HANDOFF
feat03-governance:        NOT_STARTED  → (CORTEX executes)
feat04-core-orchestration: NOT_STARTED → (CORTEX executes)
feat05-resilience:        NOT_STARTED  → (CORTEX executes)
feat06-mcp:               NOT_STARTED  → (CORTEX executes)
feat07-integration:       NOT_STARTED  → (CORTEX executes)
feat08-cleanup:           NOT_STARTED  → (CORTEX executes)
```

---

## ⚡ Quick Reference

### Mandatory Rules
1. **Audit Logging** - All operations logged
2. **TDD** - Tests fail before implementation
3. **Holistic Review** - Audit trace at phase/feature end
4. **Checkpoints** - Every 5 tasks

### Key Paths
- Audit Logs: `cortex-brain/audit-logs/`
- State DB: `cortex-brain/state/`
- Tests: `tests/`
- Source: `src/`

### Handoff Criteria
- feat02 Phase 4 Task 4.5 complete
- All validation tests pass
- Audit trail verified

---

## 📝 Version

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-07 | Initial epic creation |

---

**Next Action:** Start with `CONTINUATION-PROMPT.md`
