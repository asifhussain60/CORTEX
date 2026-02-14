# 📋 CORTEX Master Registry

**Version:** 13.0 | **Updated:** 2026-02-14 | **Structure:** Symlink Hybrid

---

## 🎯 Design Philosophy

**Symlink-based registry** combining best of both worlds:
- ✅ **Git-friendly** — All phase YAMLs stay in `phases/` (no file moves on status change)
- ✅ **Visual browsing** — Status-based folders in `_views/` for quick navigation
- ✅ **Single source** — Update status field in YAML, script regenerates views
- ✅ **Sequential numbering** — 01-17 (not 06, 48, 66... original IDs preserved in metadata)

---

## 📁 Structure

```
_cortex-master/
├── README.md                  ← Navigation guide
├── master-index.yaml          ← Auto-generated stats
│
├── phases/                    ← SOURCE OF TRUTH (17 YAMLs)
│   ├── 01-business-wisdom-display-enhancement.yaml
│   ├── 02-registry-isolation.yaml
│   ├── 03-lens-knowledge-graph-domain-intelligence.yaml
│   └── ... (sequential 01-17)
│
├── _views/                    ← STATUS-BASED VIEWS (symlinks)
│   ├── active/               ← Currently executing (2 phases)
│   ├── completed/            ← Finished work (1 phase)
│   └── deferred/             ← Backlog (10 phases)
│
├── knowledge/                ← Reference material
│   ├── specifications/
│   ├── governance/
│   ├── guides/
│   └── config/
│
└── archive/                  ← Historical snapshots
```

---

## 🚀 Quick Navigation

### Browse by Status (Visual)
```bash
# Active work
open _views/active/

# Completed phases
open _views/completed/

# Backlog
open _views/deferred/
```

### Browse All Phases
```bash
# All 17 phases (source files)
open phases/
```

### Query by Index
```bash
# View stats
cat master-index.yaml
```

---

## 🔄 Updating Phase Status

### 1. Edit Phase YAML
```bash
# Example: Mark phase 03 as completed
vim phases/03-lens-knowledge-graph-domain-intelligence.yaml

# Change status field:
status: completed  # was: deferred
```

### 2. Regenerate Views
```bash
# From CORTEX root:
./scripts/update-phase-views.sh

# Output:
# ✅ Updated! 17 phases | 1 active | 2 completed | 10 deferred
```

### 3. Verify
```bash
# Check new symlink location
ls -1 _views/completed/ | grep "03-"
```

---

## 📊 Master Index

Auto-generated stats (updated via `update-phase-views.sh`):

```yaml
# master-index.yaml
metadata:
  total_phases: 17
  active: 2
  completed: 1
  deferred: 10
```

---

## 🎯 Phase YAML Schema

Each phase file contains:

```yaml
status: active  # active | completed | deferred
original_phase_id: 81  # Original phase number from design
name: Agent Architecture Holistic Redesign
priority: high  # critical | high | medium | low
started: 2026-02-12
target_completion: 2026-02-20
owner: TDDOrchestrator
dependencies: [03, 04]

# ... (phase specification details)
```

---

## 📚 Knowledge Base

Reference material organized by category:

| Folder | Contains |
|--------|----------|
| `knowledge/specifications/` | Technical specs (MCP, orchestrators, governance gates) |
| `knowledge/governance/` | CORE rules, audit checklists, anti-patterns |
| `knowledge/guides/` | How-to docs, best practices, deployment checklists |
| `knowledge/config/` | System configuration, master plan, workflows |

---

## 🗄️ Archive

Historical snapshots organized chronologically:

```
archive/
└── snapshots/
    ├── 2026-02-14-session/      ← Session artifacts
    ├── 2026-02-14-vacuum/        ← Cleanup operations
    ├── completed-waves/          ← Wave completion reports
    ├── obsolete-plans/     ← Deprecated wave docs
    └── superseded/               ← Replaced content
```

---

## ✅ Benefits

| Benefit | Explanation |
|---------|-------------|
| **Git History Preserved** | Phase files never move (only symlinks change) |
| **Visual Status Grouping** | Browse `_views/active/` to see current work |
| **Single Maintenance** | Edit status field once, script updates views |
| **Query-Friendly** | Filter by status field OR browse folders |
| **Zero Duplication** | Symlinks point to single source in `phases/` |
| **Sequential Discovery** | 01-17 numbering easier than 06, 48, 66, 81 |

---

## 🔧 Maintenance Commands

```bash
# Regenerate all views + master index
./scripts/update-phase-views.sh

# List active phases
ls -1 _views/active/

# Count by status
echo "Active: $(ls -1 _views/active/*.yaml | wc -l)"
echo "Completed: $(ls -1 _views/completed/*.yaml | wc -l)"
echo "Deferred: $(ls -1 _views/deferred/*.yaml | wc -l)"

# Find phase by original ID
grep -l "original_phase_id: 81" phases/*.yaml
```

---

**Navigation:**  
[View All Phases](phases/) | [Active Work](_views/active/) | [Completed](_views/completed/) | [Knowledge Base](knowledge/)
