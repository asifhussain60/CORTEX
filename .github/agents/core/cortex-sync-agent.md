---
agent_id: cortex-sync-agent
version: "1.0"
status: active
layer: core
modes_served:
  - DESIGN
  - INVESTIGATE
capabilities:
  - pull_upstream
  - diff_extraction
  - privacy_sanitization
  - intelligent_three_way_merge
  - conflict_surface
  - state_tracking
  - sync_dry_run
  - sync_status_report
orchestrators_used:
  - GitOrchestrator
  - SanitizationOrchestrator
  - GitPublishOrchestrator
mcp_tools:
  - cortex_validate
  - cortex_governance
  - cortex_git
priority: P0
token_cost_estimate: 3200
created_date: "2026-02-25"
last_updated: "2026-02-25"
maintainer: "Asif Hussain"
---

# CORTEX Sync Agent

**Author:** Asif Hussain | **Orchestrator:** SyncSessionOrchestrator ✅  
**Updated:** 2026-02-25 | **Authority:** `.github/agents/core/cortex-sync-agent.md`  
**Prompt:** `.github/prompts/cortex-sync.prompt.md`

---

## Purpose

Executes the 4-gate one-way sync pipeline from the CORTEX repository into a target
company folder. No code flows back. Privacy-safe (Gate 3 sanitization). Merge-safe
(Gate 4 three-way merge). Human-in-the-loop on all conflicts.

**Activation trigger:** User invokes `/sync target=<path>` in Copilot Chat.

---

## Pre-Flight Gate (P0 — runs before Gate 1)

```
AC_START: AC-SYNC-{TIMESTAMP}
```

Execute these checks in order. Any P0 failure halts with inline error — no gates execute.

| # | Check | Command | P0 Halt Condition |
|---|-------|---------|-------------------|
| 1 | CORTEX workspace is open | `pwd` matches CORTEX root | Not in CORTEX workspace |
| 2 | Target path exists | `os.path.isdir(target)` | Path does not exist |
| 3 | Target path is not inside CORTEX | `target not in cortex_root` | Path overlap detected |
| 4 | CORTEX has no uncommitted merge conflicts | `git diff --check` | Conflict markers present |
| 5 | No open conflicts in target | `grep -rn "<<<<<<" target/` | Conflicts found — must resolve first |
| 6 | SanitizationOrchestrator importable | Python import check | Import fails |

If all checks pass → display pre-flight summary:
```
✅ Pre-flight passed
   CORTEX root: /Users/asif/PROJECTS/CORTEX
   Target:      /Users/asif/work/Cortex.Company
   State file:  <target>/.cortex-sync-state.yaml [exists | first-run]
   Last sync:   <SHA> at <timestamp> | never
```

---

## Gate 1 — PULL (Upstream Update)

**Purpose:** Bring local CORTEX branch up to date with origin.

```bash
# Executed in CORTEX workspace
git fetch origin
git pull origin CORTEX --ff-only
```

**Rules:**
- `--ff-only` is mandatory — if a merge would be required, halt and surface the conflict inline
- If already up to date → display `✅ Gate 1: Already at latest (SHA: {HEAD})` and continue
- Record `pull_sha = git rev-parse HEAD` after pull

**Output:**
```
✅ Gate 1: PULL complete
   Branch: CORTEX → origin/CORTEX
   SHA before: {prev_sha}
   SHA after:  {pull_sha}
   Commits pulled: N
```

**Failure handling:**
```
🔴 Gate 1: PULL failed — {error}
   Likely cause: non-fast-forward (local commits not in origin)
   Action required: run `git rebase origin/CORTEX` manually, then re-run /sync
```

---

## Gate 2 — DIFF (Changed File Extraction)

**Purpose:** Identify exactly which files changed between the previous state and the new HEAD.

### Case A — State file exists (routine sync)

```bash
last_sync_sha = read from <target>/.cortex-sync-state.yaml → last_sync_sha
changed_files = git diff {last_sync_sha}..HEAD --name-only --diff-filter=ACM
```

- `A` = Added, `C` = Copied, `M` = Modified
- `D` = Deleted files are collected separately as `deleted_files` (not auto-propagated)

### Case B — No state file (first sync)

```bash
changed_files = git ls-files --cached   # all tracked files
```

### Exclusion filter (applied after diff)

Remove from `changed_files` any path matching:
```
.git/**
.cortex-runtime/**
*.log
*.db
.env*
cortex_brain/state/**
.vscode/settings.json
.vscode/extensions.json
__pycache__/**
*.pyc
*.pyo
```

**Output:**
```
✅ Gate 2: DIFF complete
   Changed files:  N
   Deleted files:  N (will be flagged, not auto-propagated)
   Excluded:       N (matched exclusion list)
   Proceeding with N files to Gate 3
```

If `changed_files` is empty after exclusion:
```
✅ Gate 2: Nothing to sync — no file changes since last sync SHA {sha}
   AC_COMPLETE: AC-SYNC-{TIMESTAMP} ✅ {elapsed_ms}ms — 0 files synced
```
Session ends cleanly.

---

## Gate 3 — SANITIZE (Privacy Boundary)

**Purpose:** Strip PII, secrets, and proprietary patterns from every file in `changed_files`
before it crosses the CORTEX → Company boundary.

**Engine:** `SanitizationOrchestrator` from `cortex/orchestrators/git/sanitization_orchestrator.py`

### Invocation Pattern

For each file in `changed_files`:

```python
from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator

orchestrator = SanitizationOrchestrator()
result = orchestrator.sanitize_content(
    content=file_content,
    file_path=relative_path,
    context="sync"
)
# result.sanitized_content  → use this for Gate 4
# result.substitution_count → log for summary
# result.integrity_valid    → if False, halt on this file
```

### Pattern Categories Applied

| Category | Examples | Action |
|----------|---------|--------|
| `secret` | API keys, bearer tokens, AWS keys | Replace with `<REDACTED>` |
| `pii` | Emails, phone numbers, usernames in configs | Replace with `<ANONYMIZED>` |
| `proprietary` | Internal hostnames, internal service URLs | Replace with `<INTERNAL>` |

### Integrity Validation

After sanitization, `SanitizationOrchestrator` runs `IntegrityValidator` to confirm the
sanitized content is syntactically valid (Python AST check for `.py` files, YAML parse
for `.yaml`/`.yml`, JSON parse for `.json`). If integrity fails:

```
🔴 Gate 3: Integrity validation failed for {file_path}
   Substitution count: N
   Error: {error_detail}
   Action: File skipped — review manually before adding to Company folder
```

Skipped files are recorded in the state file with `status: skipped`.

**Output:**
```
✅ Gate 3: SANITIZE complete
   Files sanitized: N
   Total substitutions: N
   Integrity failures (skipped): N
```

---

## Gate 4 — MERGE (Intelligent 3-Way Merge)

**Purpose:** Write sanitized CORTEX content into the target folder without destroying
any existing work the company team has done in that folder.

### Per-File Decision Logic

For each sanitized file:

```
target_file = <target>/<relative_path>
```

**Case 1 — File does not exist in target** (net-new from CORTEX):
```
Action: Write directly. No merge needed.
State:  status = "clean"
```

**Case 2 — File exists in target AND matches last-synced CORTEX content** (company untouched):
```
Action: Overwrite with sanitized CORTEX version. CORTEX is authoritative.
State:  status = "clean"
```

**Case 3 — File exists in target AND differs from last-synced content** (company has local edits):
```
Base:   CORTEX content at last_sync_sha (the version company started from)
Ours:   Current content of target file (company edits)
Theirs: Sanitized new CORTEX version

Action: Run 3-way merge
  - If auto-merge succeeds with no conflicts → write merged result
    State: status = "clean"
  - If conflicts exist → surface inline (see Conflict Surface below)
    State: status = "conflict" (do NOT write until resolved)
```

### 3-Way Merge Execution

```bash
# Extract base content (CORTEX file at last sync SHA)
git show {last_sync_sha}:{relative_path} > /tmp/cortex_base_{hash}

# Files already in memory:
#   /tmp/cortex_ours_{hash}   = current content of target/<relative_path>
#   /tmp/cortex_theirs_{hash} = Gate 3 sanitized output

git merge-file \
    /tmp/cortex_ours_{hash} \
    /tmp/cortex_base_{hash} \
    /tmp/cortex_theirs_{hash}
# Exit code 0 = clean merge | Exit code > 0 = conflicts present
```

### Conflict Surface Format

Each conflict is shown inline in Copilot Chat:

```
⚠️ CONFLICT: cortex/orchestrators/core/master_orchestrator.py

┌─ BASE (last synced CORTEX) ──────────────────────────────┐
│  def coordinate_operation(self, request: str) -> Result:  │
│      ...original CORTEX code...                           │
└───────────────────────────────────────────────────────────┘
┌─ YOURS (Company edits) ──────────────────────────────────┐
│  def coordinate_operation(self, request: str,             │
│      company_context: CompanyCtx) -> Result:              │
│      ...company-specific additions...                     │
└───────────────────────────────────────────────────────────┘
┌─ THEIRS (New CORTEX version) ────────────────────────────┐
│  def coordinate_operation(self, request: str) -> Result:  │
│      ...updated CORTEX logic...                           │
└───────────────────────────────────────────────────────────┘

Choose resolution:
  [A] Accept CORTEX version (discard company edits for this section)
  [B] Keep Company version (skip CORTEX update for this section)
  [M] Manual — I will type the merged result
  [S] Skip this file entirely this sync run
```

User responds per conflict hunk. Agent writes the resolved content after all hunks
in a file are resolved.

**Output (when all files processed):**
```
✅ Gate 4: MERGE complete
   Written (clean):        N files
   Written (auto-merged):  N files
   Conflicts resolved:     N files
   Conflicts pending:      N files (session will not AC_COMPLETE until resolved)
   Deleted (flagged only): N files
```

---

## Deletion Handling (after Gate 4)

Files that appeared in `deleted_files` (from Gate 2, `--diff-filter=D`) are listed
as a post-sync advisory — never auto-deleted from the Company folder:

```
⚠️ DELETION ADVISORY — These files were deleted in CORTEX but NOT removed from Company:
   cortex/legacy/old_module.py
   cortex/tools/deprecated_tool.py

To apply these deletions in Company:
  rm <target>/cortex/legacy/old_module.py
  rm <target>/cortex/tools/deprecated_tool.py

Confirm? [Y/N]
```

Only on explicit `Y` does the agent delete.

---

## State File Update (Post Gate 4)

After all conflicts are resolved and all files written:

```yaml
# <target>/.cortex-sync-state.yaml — written by sync agent
cortex_sync_state:
  format_version: "1.0"
  last_sync_at: "{ISO8601_TIMESTAMP}"
  last_sync_sha: "{pull_sha}"          # SHA from Gate 1
  cortex_branch: "CORTEX"
  cortex_remote: "origin"
  target_path: "{absolute_target_path}"
  files:
    "{relative_path}":
      synced_sha: "{pull_sha}"
      synced_at: "{ISO8601_TIMESTAMP}"
      status: "clean"                  # clean | conflict | skipped | excluded
```

**Gitignore recommendation** (display once after first sync):
```
# Add to <target>/.gitignore
.cortex-sync-state.yaml
```

---

## AC_COMPLETE

```
AC_COMPLETE: AC-SYNC-{TIMESTAMP} ✅ {elapsed_ms}ms
Summary:
  Gate 1 PULL:      ✅ {N} commits pulled (SHA: {sha})
  Gate 2 DIFF:      ✅ {N} files in scope
  Gate 3 SANITIZE:  ✅ {N} files, {N} substitutions, {N} skipped
  Gate 4 MERGE:     ✅ {N} clean, {N} auto-merged, {N} manual, {N} pending
  State file:       ✅ Updated at <target>/.cortex-sync-state.yaml
  Deletions:        ℹ️  {N} flagged (not auto-applied)
```

If any conflicts remain unresolved:
```
AC_COMPLETE: AC-SYNC-{TIMESTAMP} ⚠️ PARTIAL {elapsed_ms}ms
  {N} files pending conflict resolution
  Run `/sync resolve target=<path>` to resume
```

---

## Dry-Run Mode (`/sync dry-run target=<path>`)

Runs Gates 1–3 only. Gate 4 produces a preview table — no files are written.

```
DRY-RUN PREVIEW (no files written)
┌─────────────────────────────────────────┬──────────────┬────────────┬───────────────┐
│ File                                    │ Diff Status  │ Sanitized  │ Merge Outcome │
├─────────────────────────────────────────┼──────────────┼────────────┼───────────────┤
│ cortex/orchestrators/core/master_*.py   │ Modified     │ 0 changes  │ Clean write   │
│ cortex/mcp/tools/new_tool.py            │ Added        │ 1 change   │ Net-new copy  │
│ cortex/intelligence/provider.py         │ Modified     │ 0 changes  │ ⚠️ Conflict   │
└─────────────────────────────────────────┴──────────────┴────────────┴───────────────┘
Run /sync target=<path> to apply (conflicts will be surfaced for manual resolution)
```

---

## Status Mode (`/sync status target=<path>`)

Reads state file only — no git operations.

```
SYNC STATUS — <target>
  Last sync:    2026-02-25T14:30:00Z
  Last SHA:     abc123def456
  Files tracked: N
  Clean:         N
  Conflict:      N  ← run /sync resolve to resume
  Skipped:       N
  Excluded:      N
```

---

## Error Taxonomy

| Code | Gate | Condition | User Action |
|------|------|-----------|-------------|
| `SYNC-E001` | Pre-flight | Target path not found | Create the folder or correct the path |
| `SYNC-E002` | Gate 1 | `git pull` non-fast-forward | `git rebase origin/CORTEX` then retry |
| `SYNC-E003` | Gate 1 | Network unreachable | Check VPN / network, retry |
| `SYNC-E004` | Gate 2 | Invalid last_sync_sha in state file | Run `/sync reset-state` (⚠️ next sync = full copy) |
| `SYNC-E005` | Gate 3 | `SanitizationOrchestrator` import failed | Run `python3 -m cortex.mcp` to verify environment |
| `SYNC-E006` | Gate 3 | Integrity validation failed | Review file manually; it is skipped for this run |
| `SYNC-E007` | Gate 4 | `git merge-file` binary | Binary files are excluded from 3-way merge; CORTEX version wins |
| `SYNC-E008` | Gate 4 | Target file not writable | Check file permissions in Company folder |

---

## Governance Compliance

| Rule | Compliance |
|------|-----------|
| CORE-002 | ✅ All output inline — this agent never creates `.md`/`.txt` report files |
| CORE-011 | ✅ All gate functions carry type hints (implementation in prompt session) |
| CORE-012 | ✅ All public methods documented inline |
| CORE-027 | ✅ `AC_START` / `AC_COMPLETE` markers emitted per session |
| CORE-035 | ✅ Single canonical sync implementation — no duplicate agents |
| CORE-049 | ✅ Silent progress bars in Chat; no terminal narration |
| CORE-064 | ✅ Session is BLOCKED from AC_COMPLETE while any conflict remains unresolved |

---

## Integration with Existing Git Orchestrators

This agent **delegates** to existing wired orchestrators — it does not reimplement them:

| Existing Orchestrator | Used In | How |
|----------------------|---------|-----|
| `SanitizationOrchestrator` | Gate 3 | `orchestrator.sanitize_content(content, file_path, context="sync")` |
| `GitOrchestrator` | Gate 1 | `orchestrator.pull(branch="CORTEX", remote="origin", ff_only=True)` |
| `GitPublishOrchestrator` | Gate 1 (pull phase) | `orchestrator.async_pull()` for network resilience |

No new Python orchestrator is created. The agent spec is the implementation layer.
The existing `git/` orchestrator domain handles all runtime git operations.

---

## Customization Points

| Variable | Default | Override |
|----------|---------|---------|
| `target` | *(required)* | `/sync target=<path>` |
| `branch` | `CORTEX` | `/sync target=<path> branch=main` |
| `remote` | `origin` | `/sync target=<path> remote=upstream` |
| `exclusions` | See Gate 2 list | Add patterns to `<target>/.cortex-sync-ignore` |
| `sanitize` | `true` | `/sync target=<path> sanitize=false` ⚠️ Not recommended |

### `.cortex-sync-ignore` (optional, lives in target)

```
# Custom exclusion patterns for this company's sync session
# Glob patterns relative to CORTEX workspace root
cortex/internal-only/**
scripts/personal/**
```

Agent reads this file from the target root before Gate 2 exclusion filtering.
