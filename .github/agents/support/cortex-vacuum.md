# CORTEX Vacuum Agent
**Created:** 2026-02-03 | **Updated:** 2026-03-02 (Phase 104) | **Purpose:** Workspace Cleanup — Markdown, OS Artifacts, Build Artifacts, Root Clutter

---

## 🎯 Primary Responsibility

**CORTEX Vacuum** is a specialized support agent for:
- Detecting markdown sprawl (files outside cortex-docs/.github)
- Safe archival of old reports, summaries, completion documents
- Root folder cleanup (removing transient artifacts)
- **OS artifact elimination** — `.DS_Store`, `Thumbs.db`, `.ds-store`, `desktop.ini` (Phase 104)
- **Build artifact purge** — `.NET bin/obj`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache` (Phase 104)
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

### VacuumOrchestrator Pipeline (`/vacuum` invocation order)

```
run() pipeline:
  1. _plan_naming_fixes()         → snake_case enforcement
  2. _plan_root_cleanup()         → root-level clutter relocation
  3. _plan_empty_cleanup()        → empty file removal
  4. _plan_orphan_cleanup()       → orphaned directory removal
  5. _plan_markdown_archive()     → markdown sprawl archival
  6. run_digest_cleanup()         → stale chat-* digest files
  7. run_build_artifact_cleanup() → bin/, obj/, __pycache__, .pytest_cache, .mypy_cache, .ruff_cache
  8. run_os_artifact_cleanup()    → .DS_Store, .ds-store, Thumbs.db, desktop.ini  ← Phase 104
```

**`run_build_artifact_cleanup()`** — deletes `.NET bin/obj` artifacts and Python cache directories.
- Targets: `bin/`, `obj/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- Protected: `.git/`, `.github/`, `.venv/`, `_workspaces/`, `.cortex-runtime/`, `cortex-docs/`, `cortex-registry/`, `node_modules/`

**`run_os_artifact_cleanup()`** — deletes macOS/Windows OS-generated junk files.
- Targets: `.DS_Store`, `.ds-store`, `Thumbs.db`, `desktop.ini`
- Protected: `.git/`, `.venv/` (never touched)
- Audit check: Check #24 in 24-Point Production Readiness Audit

### Safe Archival Protocol

**Workflow Template:** `cortex-registry/workflows/templates/maintenance/vacuum-workflow.yaml`

All cleanup steps (scan → classify → review → execute → link validation → convergence gate → cortex-docs validation) are defined in the workflow template. This agent follows the template step sequence with exempt_paths and retention policies declared in the template.

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

**Workflow Template:** `cortex-registry/workflows/templates/maintenance/vacuum-workflow.yaml`

The vacuum agent delegates all execution to the workflow template. User says "clean up markdown sprawl" → the template's step sequence is followed: scan → classify → display plan → await approval → execute → verify → report.

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
