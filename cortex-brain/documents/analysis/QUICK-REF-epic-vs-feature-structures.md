# Quick Reference: EPIC vs FEATURE Structures

**Planning System v6 (Simplified)**

---

## 📊 Side-by-Side Comparison

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     EPIC PLAN                                              │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  cortex5-epic/                                                                             │
│  ├── CONTINUATION-PROMPT.md              ← Session resumption                             │
│  ├── plan-viewer.html                    ← Interactive viewer                             │
│  ├── launch_plan_viewer.py               ← Viewer launcher                                │
│  │                                                                                         │
│  ├── analysis/                           ← Epic-level analysis                            │
│  ├── architecture/                       ← Epic-level architecture                        │
│  ├── artifacts/                          ← Epic-level deliverables                        │
│  ├── context/                            ← Epic background                                │
│  ├── reports/                            ← Epic-level reports                             │
│  ├── scripts/                            ← Epic-level automation                          │
│  ├── tracking/                           ← Epic-level tracking                            │
│  │   └── epic-progress-tracker.json     ← Master tracker                                 │
│  │                                                                                         │
│  └── features/                           ← Feature implementations                        │
│      │                                                                                     │
│      ├── feat01-continuation-system/     ← Feature 1                                      │
│      │   ├── feature.yaml                ← 🆕 Phases defined in YAML                     │
│      │   ├── analysis/                   ← Feature analysis                               │
│      │   ├── artifacts/                  ← Feature outputs (implementation, tests)        │
│      │   ├── context/                    ← Feature context                                │
│      │   ├── reports/                    ← Feature reports (execution logs)               │
│      │   └── tracking/                   ← Feature progress                               │
│      │                                                                                     │
│      ├── feat02-goal-detection/          ← Feature 2 (same 7 items)                       │
│      ├── feat03-goal-inheritance/        ← Feature 3 (same 7 items)                       │
│      └── feat0X-{name}/                  ← Feature X (same 7 items)                       │
│                                                                                            │
│  📊 Stats:                                                                                 │
│  • Epic folders: 7                                                                         │
│  • Features: N (e.g., 11 in cortex5-epic)                                                 │
│  • Items per feature: 7 (feature.yaml + 6 folders)                                        │
│  • Total folders: 7 + (N × 7) = 78 for 11 features                                        │
│  • Depth: 4 levels                                                                         │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FEATURE PLAN                                             │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                            │
│  oauth2-auth-system/                                                                       │
│  ├── CONTINUATION-PROMPT.md              ← Session resumption                             │
│  ├── plan-viewer.html                    ← Interactive viewer                             │
│  ├── launch_plan_viewer.py               ← Viewer launcher                                │
│  │                                                                                         │
│  ├── feature.yaml                        ← 🆕 Phases defined in YAML (root level)        │
│  │                                                                                         │
│  ├── analysis/                           ← Feature analysis                               │
│  ├── architecture/                       ← Feature architecture                           │
│  ├── artifacts/                          ← Implementation outputs                         │
│  ├── context/                            ← Feature background                             │
│  ├── reports/                            ← Execution reports                              │
│  ├── scripts/                            ← Feature automation                             │
│  └── tracking/                           ← Progress tracking                              │
│      └── progress-tracker.json          ← Feature progress                                │
│                                                                                            │
│  📊 Stats:                                                                                 │
│  • Root files: 4 (prompt, viewer, launcher, feature.yaml)                                 │
│  • Standard folders: 7                                                                     │
│  • Total items: 11                                                                         │
│  • Depth: 4 levels                                                                         │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Differences

| Aspect | EPIC | FEATURE |
|--------|------|---------|
| **features/ folder** | ✅ YES (contains N features) | ❌ NO (single feature) |
| **feature.yaml location** | Inside each feat0X/ folder | At root level |
| **Root complexity** | 7 folders + features/ | 7 folders only |
| **Scalability** | N features, each with phases | 1 feature with phases |
| **Use case** | Multi-feature initiatives | Standalone features |

---

## 📋 feature.yaml Location

```
EPIC:
cortex5-epic/
└── features/
    ├── feat01-continuation-system/
    │   └── feature.yaml              ← HERE (inside feature folder)
    ├── feat02-goal-detection/
    │   └── feature.yaml              ← HERE (inside feature folder)
    └── feat0X-{name}/
        └── feature.yaml              ← HERE (inside feature folder)


FEATURE:
oauth2-auth-system/
└── feature.yaml                      ← HERE (at root level)
```

---

## 🆕 What's in feature.yaml?

**Core Content (Both EPIC & FEATURE):**

```yaml
feature_id: feat01-continuation-system
feature_name: Cross-Session Continuation System
priority: P1_HIGH
status: NOT_STARTED
progress: 0

# Phases (logical execution steps)
phases:
  - phase: 1
    name: Design & Architecture
    status: NOT_STARTED
    progress: 0
    tasks:
      - id: task-1.1
        name: Design CONTINUATION-PROMPT.md schema
        status: NOT_STARTED
      - id: task-1.2
        name: Design Tier 1 integration
        status: NOT_STARTED
    outputs:
      - path: analysis/continuation-architecture.yaml
      - path: architecture/tier1-integration.yaml
  
  - phase: 2
    name: Implementation
    status: NOT_STARTED
    tasks: [...]
    outputs: [...]
  
  - phase: 3
    name: Testing
    status: NOT_STARTED
    tasks: [...]
    outputs: [...]
  
  - phase: 4
    name: Documentation & Deployment
    status: NOT_STARTED
    tasks: [...]
    outputs: [...]

# Artifact tracking
artifacts:
  design: [...]
  implementation: [...]
  tests: [...]
  documentation: [...]

# Progress summary (auto-updated)
progress_summary:
  phases_total: 4
  phases_completed: 0
  tasks_total: 12
  tasks_completed: 0
```

**Key Point:** Phases are **defined in YAML** (logical), not as **folders** (physical)

---

## ❌ What's Deleted from v5?

**Removed from ALL features:**

```
features/feat0X-{name}/
└── phases/                              ❌ DELETE entire hierarchy
    ├── phase1-execution/                ❌ DELETE (empty)
    │   ├── artifacts/                   ❌ DELETE (empty)
    │   ├── reports/                     ❌ DELETE (empty)
    │   └── tracking/                    ❌ DELETE (empty)
    ├── phase2-execution/                ❌ DELETE (empty)
    ├── phase3-execution/                ❌ DELETE (empty)
    └── phase4-execution/                ❌ DELETE (empty)
```

**Per feature:** 17 folders deleted (1 phases/ + 4 phase{N}/ + 12 subfolders)  
**For cortex5-epic (11 features):** 187 folders deleted (100% empty, 0 bytes)

---

## ✅ What's Preserved?

**Everything else stays the same:**

1. **Folder names:** feat0X-, kebab-case conventions
2. **Standard folders:** analysis/, artifacts/, context/, reports/, tracking/
3. **Root files:** CONTINUATION-PROMPT.md, plan-viewer.html, launch_plan_viewer.py
4. **Execution outputs:** Still go to artifacts/, reports/, tracking/
5. **Continuation system:** Still reads epic-progress-tracker.json
6. **Plan viewer design:** Same UI, different data source (YAML instead of folders)

---

## 🎯 Mental Model

### OLD (v5): "Phases are folders"
```
❌ Create 17 folders per feature (16 stay empty)
❌ Navigate 6 levels deep to find phase info
❌ Implicit phase structure (folder names)
```

### NEW (v6): "Phases are YAML steps"
```
✅ Create 1 YAML file per feature
✅ Navigate 4 levels max
✅ Explicit phase structure (YAML definition)
✅ Master orchestrator reads YAML, executes tasks, outputs to artifacts/
```

---

## 📊 Complexity Reduction

| Metric | v5 (Phase Folders) | v6 (Phase YAML) | Reduction |
|--------|-------------------|-----------------|-----------|
| Folders per feature | 17 | 7 | **59%** ↓ |
| Empty folders | 16 per feature | 0 | **100%** ↓ |
| Folder depth | 6 levels | 4 levels | **33%** ↓ |
| Phase definition | Implicit (folders) | Explicit (YAML) | ✅ Better |
| Machine-readable | ❌ No | ✅ Yes | ✅ Better |

**For cortex5-epic (11 features):**
- v5: 260 folders (187 empty)
- v6: 78 folders (0 empty)
- **Reduction: 70%**

---

## 🚀 Quick Start

### Creating EPIC Plan (v6)

```bash
python3 -m src.main "plan cortex5-epic with features: continuation-system, goal-detection, governance-rules"

# Creates:
# cortex5-epic/
# ├── 3 root files (prompt, viewer, launcher)
# ├── 7 standard folders
# └── features/
#     ├── feat01-continuation-system/
#     │   ├── feature.yaml        ← Phases defined here
#     │   └── 6 folders
#     ├── feat02-goal-detection/
#     └── feat03-governance-rules/
```

### Creating FEATURE Plan (v6)

```bash
python3 -m src.main "plan oauth2-auth-system with JWT tokens, session management, database (users, roles, permissions)"

# Creates:
# oauth2-auth-system/
# ├── 4 root files (prompt, viewer, launcher, feature.yaml)
# └── 7 standard folders
```

---

## 📚 Full Documentation

**Detailed specs:** `cortex-brain/documents/analysis/planning-system-v6-folder-structures.md`  
**Visual comparison:** `cortex-brain/documents/analysis/cortex5-epic-structure-visual-comparison.md`  
**Simplification proposal:** `cortex-brain/documents/analysis/cortex5-epic-structure-simplification-proposal.md`

---

**Status:** ✅ READY FOR PLANNING SYSTEM v6  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
