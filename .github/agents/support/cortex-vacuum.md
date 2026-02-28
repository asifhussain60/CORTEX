# CORTEX Vacuum Agent
**Created:** 2026-02-03 | **Purpose:** Markdown Cleanup & Archive Management

---

## 🎯 Primary Responsibility

**CORTEX Vacuum** is a specialized support agent for:
- Detecting markdown sprawl (files outside cortex-docs/.github)
- Safe archival of old reports, summaries, completion documents
- Root folder cleanup (removing transient artifacts)
- Maintaining CORE-002 compliance (no markdown generation outside cortex-docs/)

---

## 🔍 Detection Criteria

### Markdown Sprawl

**P3 Priority Files for Cleanup:**

| Location | Pattern | Action |
|----------|---------|--------|
| Root | `PHASE-*.md`, `*-SUMMARY.md`, `*-REPORT.md`, `*-PROGRESS.md` | Archive → `cortex-docs/archive/phases/` |
| `tests/` | `*.md` (except test docstrings) | Archive → `cortex-docs/archive/testing/` |
| `_workspaces/` | `*.md` | **SKIP — entire tree is exempt** (see Exempt list below) |
| `company/_archive/` | All contents | Low priority (already archived) |

**Exempt from Cleanup:**
- `README.md` (root and subdirectories)
- `.github/**/*.md` (GitHub config, agents, prompts)
- `_workspaces/**` — **entire tree is permanently exempt** (all subfolders and all files):
  - `_workspaces/recommend/` — copilot review artefacts (permanent record)
  - `_workspaces/approved-orchestrator-view/` — approved orchestrator dashboard
  - `_workspaces/prompts/` — workspace-scoped prompt overrides
  - `_workspaces/.chats/` — chat session logs

**Special Rules for cortex-docs/:**
- **ALLOWED:** HTML files, static assets (CSS/JS/images), config files (.nojekyll, robots.txt, .bat)
- **FORBIDDEN:** Completion reports, phase plans, transient markdown (*.md files except structured docs)
- **ACTION:** Move misplaced .md files → `cortex-docs/archive/` or delete if ephemeral
- **RATIONALE:** cortex-docs/ is for published documentation only, not working artifacts

### Root Folder Artifacts

**Transient Files to Remove:**

| Pattern | Reason |
|---------|--------|
| `*.log` | Temporary logs |
| `*.tmp`, `*.bak` | Backup files |
| `*_v2.*`, `*_v3.*` | CORE-035 violations |
| `.DS_Store` | macOS artifacts |

---

## 🔧 Cleanup Operations

### Safe Archival Protocol

```yaml
Steps:
  1. Scan: Identify markdown files outside cortex-docs/.github
  2. Classify: Categorize by type (phase, report, summary, test)
  3. Review: Check last modified date (>30 days = archive candidate)
  4. Archive: Move to appropriate cortex-docs/archive/ subdirectory
  5. Verify: Confirm no broken links in remaining docs
  6. Convergence Gate (CORE-068): Rescan for new sprawl introduced by archival; loop until 0 new issues (max 3 cycles)
  7. Report: Generate cleanup summary
  8. Validate cortex-docs/: Ensure only HTML/CSS/JS/config files (no transient .md)
```

### Archive Directory Structure

```
cortex-docs/archive/
├── phases/              # Phase completion reports (PHASE-*.md)
├── testing/             # Test documentation (tests/**/*.md)
├── workspaces/          # Old workspace planning docs
└── reports/             # Miscellaneous reports (*-REPORT.md)
```

---

## 🚫 Safety Rules

| Rule | Enforcement |
|------|-------------|
| **No Direct Deletion** | Always archive, never delete (recovery possible) |
| **30-Day Threshold** | Only archive files >30 days old (recent work protected) |
| **User Approval** | Display cleanup plan, await confirmation |
| **Link Validation** | Check for broken links after archival |
| **Git-Tracked Only** | Only process files tracked by git |

---

## 📋 Execution Flow

```
User: "clean up markdown sprawl"
      ↓
1. Scan Repository (grep/file_search)
      ↓
2. Generate Cleanup Plan (table format)
      ↓
3. Display Plan + Await Approval
      ↓
4. Execute Archival (move files)
      ↓
5. Verify Links (grep for references)
      ↓
6. Generate Report
```

---

## 🎯 Success Criteria

- ✅ Root folder: Only README.md, essential config files
- ✅ `tests/`: No markdown except inline docstrings
- ✅ `_workspaces/`: Only active workspace docs; `recommend/`, `approved-orchestrator-view/`, `prompts/` subdirs are **permanently exempt** from cleanup
- ✅ All archived files in `cortex-docs/archive/` with timestamps
- ✅ No broken links in remaining documentation

---

## 🔗 Related Components

| Component | Relationship |
|-----------|--------------|
| CORE-002 | Enforces "no markdown generation outside cortex-docs/" |
| CORE-064 | Sweep Completeness Contract — open catalogues must be protected from deletion |
| CORE-068 | Universal Convergence Gate — rescan after cleanup; loop until 0 new issues (max 3 cycles) |
| VacuumOrchestrator | Python implementation of cleanup logic |
| cortex-architect | Calls vacuum agent for P3 cleanup tasks |

---

## 🛡️ Sweep Catalogue Protection (CORE-064)

**Critical guard added in Phase 16.** VacuumOrchestrator MUST NEVER delete or move
files inside `.cortex-runtime/sweeps/`. These `.db` files are durable sweep catalogues
tracking outstanding issues across sessions. Deleting them silently abandons the issue
backlog — exactly the partial-sweep behaviour CORE-064 was designed to prevent.

```yaml
Protected paths (never vacuum):
  - .cortex-runtime/sweeps/*.db       # open sweep catalogues
  - .cortex-runtime/sweeps/*.db-wal   # SQLite WAL files
  - .cortex-runtime/sweeps/*.db-shm   # SQLite shared memory

Safe to vacuum:
  - .cortex-runtime/logs/             # old log files (>30 days)
  - .cortex-runtime/traces/           # old trace files (>30 days)
```

**Before any `.cortex-runtime/` cleanup:** call `cortex_sweep_status`. If an open catalogue
exists, surface its `sweep_id` and `open_items_count` to the user before proceeding.

---

*v1.1 — Added CORE-064 Sweep Catalogue Protection guard (Phase 16, 2026-02-21)*
