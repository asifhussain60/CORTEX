---
scope: non-production-admin
agent_id: cortex-sync-agent
status: active
layer: core
phase: 127
modes_served:
  - SYNC
capabilities:
  - deterministic_sync
  - allow_deny_policy
  - three_way_merge
  - security_danger_scan
  - baseline_tracking
  - conflict_surface
  - patch_proposals
  - proof_manifest
  - windows_path_safety
engine: cortex/tools/cortex_sync.py
workflow: cortex-registry/workflows/templates/lifecycle/sync-workflow.yaml
response_template: "cortex-response-templates.md § 🔄 SYNC Mode"
priority: P0
token_cost_estimate: 3200
created_date: "2026-03-04"
last_updated: "2026-03-04"
maintainer: "Asif Hussain"
---

# CORTEX Sync Agent — Phase 127

**Author:** Asif Hussain | **Phase:** 127
**Updated:** 2026-03-04 | **Authority:** `.github/agents/core/cortex-sync-agent.md`
**Prompt:** `.github/prompts/cortex-sync.prompt.md`
**Engine:** `cortex/tools/cortex_sync.py`

---

## Purpose

Orchestrates the 6-stage deterministic sync pipeline from the CORTEX repo root into
a user-provided target folder. Delegates all file operations to the prebuilt
`cortex_sync.py` engine. Never generates ad-hoc scripts. Never invents logic
that is already in the engine.

**Activation trigger:** `/sync target=<path>` in Copilot Chat.

---

## Pre-Flight Gate (P0 — runs before Stage 1)

```
AC_START: AC-SYNC-{TIMESTAMP}
```

| # | Check | On Failure |
|---|-------|-----------|
| 1 | CORTEX repo root exists and contains `cortex/` | ❌ Abort with error |
| 2 | Target path is an existing directory | ❌ Abort with error |
| 3 | Target is NOT inside CORTEX repo root | ❌ Abort — circular path |
| 4 | `cortex.tools.cortex_sync` importable | ❌ Abort — check environment |
| 5 | Platform detected (Windows/macOS/Linux) | 🟡 Warn if unknown |

Pre-flight display (on pass):

```
✅ Pre-flight passed
   Repo root   : {repo_root}
   Target      : {target_path}
   Platform    : {Windows | macOS | Linux}
   Baseline dir: {baseline_dir}
   Manifest    : {target}/.cortex-sync/manifest.json [exists | first-run]
```

---

## Stage 1 — Scan

**Command:**

```bash
python3 -m cortex.tools.cortex_sync \
    --repo-root "{repo_root}" \
    --target "{target_path}" \
    --dry-run \
    --baseline-dir "{baseline_dir}"
```

**Output:**

```
✅ Stage 1: Scan complete
   Files scanned : {N}
   Files eligible: {N}
   Excluded      : {N} (matched deny rules)
```

---

## Stage 2 — Plan

Display decision table inline in Copilot Chat:

```
📋 Sync Plan — {N} files
┌─────────────────────────────────┬──────────┬──────────────────────────────────────┐
│ File                            │ Decision │ Reason                               │
├─────────────────────────────────┼──────────┼──────────────────────────────────────┤
│ cortex/core/master.py           │ update   │ target unchanged from baseline        │
│ cortex/mcp/tools/new_tool.py    │ copy     │ net-new file                         │
│ cortex/intelligence/provider.py │ merged   │ three-way merge clean                 │
│ .github/prompts/CORTEX.prompt.md│ update   │ target unchanged from baseline        │
│ cortex-docs/.content/guide.md   │ copy     │ net-new file                         │
│ cortex-docs/index.html          │ excluded │ denied by policy pattern              │
│ _workspaces/old_project/        │ excluded │ denied by policy pattern              │
└─────────────────────────────────┴──────────┴──────────────────────────────────────┘

Conflicts  : {N} — patch proposals ready in {target}/.cortex-sync/patches/
Danger     : {N} — security scan flagged; staged for review
```

If `files_planned == 0`:

```
✅ Stage 2: Nothing to sync — all files are idempotent (no changes detected)
AC_COMPLETE: AC-SYNC-{TIMESTAMP} ✅ {elapsed_ms}ms — 0 files synced
```

Session ends cleanly.

---

## Stage 3 — Validate

Run security danger pattern check and policy version audit:

```bash
python3 -c "from cortex.tools.cortex_sync import SYNC_POLICY; assert SYNC_POLICY['version']=='2.0'"
```

If danger-flagged files exist, display **before** proceeding to user approval:

```
🔴 Security/Compliance Downgrade Risk Detected

The following files were blocked because their source content matches known
security scanner trigger patterns:

  {rel_path_1} — matched: {pattern_description}
  {rel_path_2} — matched: {pattern_description}

These files will NOT be copied. Patch proposals are staged in:
  {target}/.cortex-sync/patches/

To approve a specific file after reviewing the patch:
  /sync approve-danger file={rel_path} --evidence="<your_justification>"
```

---

## User Approval Gate

Display before apply:

```
🔄 Ready to sync {N} files to {target}

  Files to copy     : {N}
  Files to update   : {N}
  Files to merge    : {N}
  Files to skip     : {N}
  Conflicts pending : {N}
  Danger-staged     : {N}

Type `proceed` to apply, or `cancel` to abort.
```

---

## Stage 4 — Apply

**Command:**

```bash
python3 -m cortex.tools.cortex_sync \
    --repo-root "{repo_root}" \
    --target "{target_path}" \
    --apply \
    --write-manifest \
    --baseline-dir "{baseline_dir}" \
    --safe-merge
```

Progress display (phase-list+bar format — CORE-049):

```
- ✅ Stage 1: Scan — {N} files eligible
- ✅ Stage 2: Plan — {N} planned ({N} copy, {N} update, {N} merge)
- ✅ Stage 3: Validate — {N} danger-flagged (staged for review)
- 🔵 Stage 4: Apply — writing {N} files to target...
- ⚪ Stage 5: Verify
- ⚪ Stage 6: Report
```

**Output:**

```
✅ Stage 4: Apply complete
   Copied    : {N}
   Updated   : {N}
   Merged    : {N}
   Skipped   : {N}
   Conflicts : {N}
   Danger    : {N}
```

---

## Stage 5 — Verify

1. Confirm `{target}/.cortex-sync/manifest.json` exists
2. Spot-check 5 random written files: re-checksum and compare to manifest
3. Report any verification failures inline

```
✅ Stage 5: Verify complete
   Manifest        : ✅ {target}/.cortex-sync/manifest.json
   Spot-check      : ✅ 5/5 files verified
   Pending patches : {N} in {target}/.cortex-sync/patches/
```

---

## Stage 6 — Report

Render the **SYNC Response Template** inline in Copilot Chat.
See `cortex-response-templates.md § 🔄 SYNC Mode` for the canonical template.

```
AC_COMPLETE: AC-SYNC-{TIMESTAMP} ✅ {elapsed_ms}ms
  Stage 1 Scan    : ✅ {N} files eligible
  Stage 2 Plan    : ✅ {N} planned
  Stage 3 Validate: ✅ {N} danger-staged
  Stage 4 Apply   : ✅ {N} copied, {N} updated, {N} merged, {N} skipped
  Stage 5 Verify  : ✅ manifest confirmed
  Stage 6 Report  : ✅ template rendered
```

If conflicts remain unresolved:

```
AC_COMPLETE: AC-SYNC-{TIMESTAMP} ⚠️ PARTIAL {elapsed_ms}ms
  {N} files pending conflict resolution
  Run `/sync resolve target={target}` to resume
```

---

## Conflict Resolution Flow

When `files_conflicted > 0`, display each conflict:

```
⚠️ CONFLICT: {relative_path}

Decision: three-way merge conflict — patch staged for review

📄 Patch proposal: {target}/.cortex-sync/patches/{rel_path}.patch

The patch file contains upstream CORTEX changes. Your local version
is preserved as-is. To resolve:
  [A] Accept upstream (CORTEX) version
  [K] Keep local version (skip this update)
  [M] Open patch file and merge manually, then run `/sync resolve target={target}`
```

---

## Deletion Advisory (Post-Apply)

Files deleted upstream but not removed from target are reported as advisory only:

```
ℹ️ DELETION ADVISORY — {N} upstream deletions NOT applied to target:
   {rel_path_1}
   {rel_path_2}

To apply these deletions, run:
  rm "{target}/{rel_path_1}"
  rm "{target}/{rel_path_2}"

Or type `delete-advisory` to apply all deletions (⚠️ irreversible).
```

---

## Dry-Run Mode

Runs Stages 1–3 only. Stage 4 (apply) is skipped. Renders a plan preview table.
At the end:

```
🔍 DRY-RUN COMPLETE — No files were written.
Run /sync target={target} to apply.
```

---

## Status Mode (`/sync status target=<path>`)

Reads `manifest.json` from target. No engine invocation.

```
SYNC STATUS — {target}
  Last sync     : {timestamp}
  Sync ID       : {SYNC-id}
  Files tracked : {N}
  Copied        : {N}
  Updated       : {N}
  Merged        : {N}
  Skipped       : {N}
  Conflicts     : {N}  ← run /sync resolve to resume
  Danger-staged : {N}
```

---

## Error Taxonomy

| Code | Stage | Condition | User Action |
|---|---|---|---|
| `SYNC-E001` | Pre-flight | Target path not found | Create folder or correct path |
| `SYNC-E002` | Pre-flight | Target inside repo root | Use a path outside CORTEX root |
| `SYNC-E003` | Pre-flight | Engine import failed | Run `python3 -m cortex.mcp` to verify |
| `SYNC-E004` | Stage 1 | No eligible files | Check policy — all files may be excluded |
| `SYNC-E005` | Stage 4 | Write failed (file lock / permissions) | Check file locks; run as correct user |
| `SYNC-E006` | Stage 5 | Manifest not written | Check target write permissions |
| `SYNC-E007` | Stage 4 | Baseline save failed | Check baseline-dir write permissions |

---

## Governance Compliance

| Rule | Status |
|---|---|
| CORE-002 | ✅ All output inline — no .md/.txt files created |
| CORE-011 | ✅ Type hints on all engine functions |
| CORE-012 | ✅ Docstrings on all public APIs |
| CORE-028 | ✅ snake_case: cortex_sync.py |
| CORE-035 | ✅ Single canonical sync engine — no duplicates |
| CORE-049 | ✅ Phase-list+bar progress in Chat; no terminal narration |
| CORE-064 | ✅ Session BLOCKED from AC_COMPLETE while conflicts unresolved |

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
