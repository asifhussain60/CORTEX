---
scope: non-production-admin
prompt_id: cortex-sync
status: active
mode: SYNC
author: Asif Hussain
updated: 2026-03-04
phase: 127
agent: cortex-sync-agent.md
engine: cortex/tools/cortex_sync.py
workflow: cortex-registry/workflows/templates/lifecycle/sync-workflow.yaml
mcp_tools:
  - cortex_validate
  - cortex_workflow
token_cost_estimate: 3200
---

# 🛠️ CORTEX Architect Sync Prompt — Phase 127 Redesign

**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
**Updated:** 2026-03-04 | **Phase:** 127 | **Authority:** `.github/prompts/cortex-sync.prompt.md`
**Agent:** `.github/agents/core/cortex-sync-agent.md` | **Engine:** `cortex/tools/cortex_sync.py`

---

## 🎯 Purpose

One-way **deterministic, safe, Windows-first** sync from the **CORTEX repo root** into a
user-provided **target path**. No code ever flows back. No file is blindly overwritten.
The same inputs always produce the same outputs (deterministic). Running twice with no
upstream changes makes no changes the second time (idempotent). Target-side security
hardening (Veracode fixes, local patches) is preserved by design (non-destructive).

**Engine:** `cortex/tools/cortex_sync.py` — a prebuilt, parameterised CLI tool.
The prompt and agent orchestrate the engine; they never generate ad-hoc scripts.

---

## 🔌 Activation

```
/sync target=<absolute_path_to_target_folder>
```

**Examples:**

```
/sync target=C:\dev\CompanyCortex                  (Windows)
/sync target=/Users/asif/work/Cortex.Company       (macOS)
/sync target=/home/asif/company-cortex             (Linux)
/sync dry-run target=C:\dev\CompanyCortex          (preview — no writes)
```

The `target` parameter is the only required input. All other parameters use safe defaults.

---

## 🏗️ Architecture

```
User: /sync target=<path>
    ↓
cortex-sync.prompt.md          ← Session driver (you are here)
    ↓
cortex-sync-agent.md           ← 6-stage pipeline orchestrator
    ↓
cortex/tools/cortex_sync.py    ← Prebuilt deterministic engine (single implementation)
    ↓
  Stage 1: Scan      — Enumerate eligible files via SSOT allow/deny policy
  Stage 2: Plan      — Per-file decision: copy/update/merge/conflict/skip/danger
  Stage 3: Validate  — Security danger scan; block downgrade-risk files
  Stage 4: Apply     — Write files (dry-run skips this)
  Stage 5: Verify    — Re-checksum written files; confirm manifest written
  Stage 6: Report    — Render SYNC Response Template inline in Copilot Chat
    ↓
<target>/.cortex-sync/manifest.json    ← Proof artifact (checksums + decision log)
<target>/.cortex-sync/baselines/       ← Per-file baseline for three-way merge
<target>/.cortex-sync/patches/         ← Conflict + danger proposals for review
```

---

## 🔒 SSOT Allow/Deny Policy

**Single source of truth:** `cortex/tools/cortex_sync.py::SYNC_POLICY`
**Mirror (documentation only):** `cortex-registry/workflows/templates/lifecycle/sync-workflow.yaml § policy_mirror`

### Default Action: `allow`

All repo root files and directories are synced **unless** explicitly denied below.

### Explicit Deny Rules (P0 — never synced)

| Pattern | Reason |
|---|---|
| `_workspaces/**` | Private workspaces — architecturally excluded |
| `cortex-registry/company/repos/**` | Company-private repo artifacts |
| `cortex-registry/company/dashboards/repos/**` | Company-private dashboard artifacts |
| `cortex-docs/**` | **Default-deny all of cortex-docs** — sub-paths re-allowed below |
| `.cortex-runtime/**` | Runtime data — never sync |
| `.git/**` | Git internals |
| `**/__pycache__/**`, `**/*.pyc`, `**/*.pyo` | Python bytecode |
| `.env`, `.env.*` | Secrets |
| `.vscode/settings.json`, `.vscode/extensions.json` | Personal MCP config |
| `**/*.db`, `**/*.log` | Runtime artefacts |
| `**/.DS_Store`, `**/Thumbs.db` | OS artefacts |
| `.cortex-sync/**` | Sync-tool state — never round-trip |

### Allow Override (re-allows inside denied subtrees)

| Pattern | What It Permits |
|---|---|
| `cortex-docs/.content/**` | **Only** the `.content/` subdirectory from cortex-docs |

> ⛔ **Root `index.html` and all other cortex-docs web artifacts are NOT synced.**
> Only `cortex-docs/.content/**` is eligible.

### .github Allowlist (production-critical prompts only)

Admin prompts and tools under `.github/**` are **excluded by default**.
Only these paths are eligible:

- `.github/prompts/CORTEX.prompt.md`
- `.github/prompts/cortex-architect.prompt.md`
- `.github/agents/core/CORTEX.md`
- `.github/agents/core/cortex-executor.md`
- `.github/agents/core/cortex-auditor.md`
- `.github/agents/core/cortex-interactive.md`
- `.github/agents/core/cortex-debugger.md`
- `.github/agents/core/cortex-vacuum.md`
- `.github/copilot-instructions.md`

```yaml
# production_files: — files that MUST be synced to every target (never excluded)
production_files:
  - ".github/prompts/CORTEX.prompt.md"
  - ".github/prompts/cortex-architect.prompt.md"
  - ".github/agents/core/CORTEX.md"
  - ".github/agents/core/cortex-executor.md"
  - ".github/agents/core/cortex-auditor.md"
  - ".github/agents/core/cortex-interactive.md"
  - ".github/copilot-instructions.md"
```

**Guardrail:** `cortex-sync.prompt.md`, `cortex-sync-agent.md`, total-recall, trainer,
and all other admin-only prompts/agents are **never synced** — they cannot be used to
smuggle non-production tools into a downstream runtime.

---

## 🔀 Sync Strategy — Three-Way Merge with Tracked Baseline

### Problem

Target teams fix security/compliance issues (e.g., Veracode findings). A naive overwrite
would reintroduce those fixes. Standard `rsync` has no concept of "local edits vs upstream changes".

### Solution: Three-Way Merge + CORTEX Baseline

For each file, the engine computes:

```
A = Baseline checksum (last successful sync — stored in .cortex-sync/baselines/)
B = Current source checksum (upstream CORTEX repo)
C = Current target checksum (downstream file)
```

| Scenario | Decision |
|---|---|
| B == C | Skip — idempotent, nothing to do |
| A is missing + C exists | Skip + report — cannot safely merge without baseline |
| C == A (target unchanged since baseline) | Safe overwrite — target was not locally modified |
| C ≠ A (target was locally modified) | Three-way merge: base=A, ours=C, theirs=B |
| Three-way merge clean | Write merged result; update baseline |
| Three-way merge conflicts | Stage patch proposal in `.cortex-sync/patches/`; do NOT write |
| Security danger patterns detected in B | Block copy; stage patch proposal; require explicit approval |

### Non-Destructive Guarantees

- ✅ **Never silently clobber** — if target has local edits, merge or skip; never overwrite directly
- ✅ **Never delete target files** by default — upstream deletions are reported but not applied
- ✅ **Never propagate security downgrade patterns** — danger scan runs before apply
- ✅ **Never auto-merge conflicts** — conflicts produce patch proposals, not silent overwrites

---

## 🪟 Windows-First Considerations

The engine handles all of the following automatically:

| Complexity | Handling |
|---|---|
| Path separators | All internal logic uses forward-slash; OS paths normalised at boundaries |
| Long paths (>260 chars) | `\\?\` prefix auto-applied on Windows |
| Line endings | Text files: CRLF on Windows, LF on macOS/Linux |
| File locks | OSError on write → decision=SKIP with reason logged |
| Binary files | Detected via null bytes; line-ending logic skipped |
| Executable bits | Not propagated (Windows has no POSIX exec bit) |
| Symlinks | `followlinks=False` — symlinks to directories are not traversed |

---

## 🛡️ Security Danger Scan

Before any file is copied, its source content is scanned for patterns known to trigger
security scanners. If a match is found:

1. File decision is set to `DANGER` — it is **not** copied
2. A patch proposal is staged in `<target>/.cortex-sync/patches/<rel_path>.patch`
3. The SYNC Response Template shows the file in the **Conflicts/Warnings** section
4. User must explicitly `approve` with evidence before the file is accepted

**Danger patterns (examples):**

- Hardcoded credentials: `password = "..."`, `api_key = "..."`, `bearer <token>`
- AWS key patterns: `AKIA[0-9A-Z]{16}`
- Private key headers: `-----BEGIN RSA PRIVATE KEY-----`

---

## 📋 Proof Artifacts

Every sync run (apply mode) produces:

| Artifact | Location | Contents |
|---|---|---|
| `manifest.json` | `<target>/.cortex-sync/manifest.json` | All file decisions, checksums, sync metadata |
| Baseline records | `<repo-root>/.cortex-sync/baselines/` | Per-file baseline checksums for future three-way merge |
| Patch proposals | `<target>/.cortex-sync/patches/` | Conflict and danger-flagged files staged for review |

---

## 🚦 CLI Reference

```bash
# Preview — no writes
python3 -m cortex.tools.cortex_sync --target /path/to/target --dry-run

# Apply with manifest + safe merge
python3 -m cortex.tools.cortex_sync --target /path/to/target --apply --write-manifest --safe-merge

# Custom deny/allow overrides
python3 -m cortex.tools.cortex_sync --target /path/to/target --apply \
    --denylist "cortex/internal/**,scripts/personal/**" \
    --allowlist "cortex-docs/.content/extra/**"

# Override baseline directory
python3 -m cortex.tools.cortex_sync --target /path/to/target --apply \
    --baseline-dir /path/to/baselines
```

**Exit codes:**

| Code | Meaning |
|---|---|
| 0 | Success — no conflicts, no danger |
| 1 | Invocation error (missing required arg, bad path) |
| 2 | Sync completed with conflicts or danger-flagged files requiring resolution |

---

## ⚡ Command Reference (Copilot Chat)

| Command | Effect |
|---|---|
| `/sync target=<path>` | Full 6-stage sync (interactive — renders plan before apply) |
| `/sync dry-run target=<path>` | Preview plan only — no files written |
| `/sync status target=<path>` | Show manifest summary: last sync, file decisions, pending |
| `/sync resolve target=<path>` | Re-display patch proposals, guide user through conflict resolution |
| `/sync reset-baseline target=<path>` | ⚠️ Clear baselines — next sync treats everything as new |

---

## 🔗 Component Map

| Component | Path | Role |
|---|---|---|
| Sync engine | `cortex/tools/cortex_sync.py` | Deterministic CLI — all file operations |
| Sync agent | `.github/agents/core/cortex-sync-agent.md` | 6-stage pipeline orchestrator |
| Sync workflow | `cortex-registry/workflows/templates/lifecycle/sync-workflow.yaml` | Declarative stage definition |
| SYNC Response Template | `.github/templates/cortex-response-templates.md § 🔄 SYNC Mode` | Chat rendering |
| Phase plan | `cortex-registry/planning/phases/planned/phase-127-deterministic-sync-engine.yaml` | Implementation plan |

---

## ⛔ What This Is NOT

- ❌ Not a two-way sync — CORTEX ← target flow is architecturally blocked
- ❌ Not a CI/CD pipeline — runs interactively in Copilot Chat on demand
- ❌ Not a generated script — the engine is prebuilt and versioned, never invented per-session
- ❌ Not a git submodule or fork sync — no git history entanglement
- ❌ Not a blind file copy — every file goes through policy + danger scan + merge logic

---

## ✅ Governance Compliance

| Rule | Status |
|---|---|
| CORE-002 | ✅ All output inline — no .md/.txt report files created |
| CORE-011 | ✅ Type hints on all engine functions |
| CORE-012 | ✅ Docstrings on all public APIs |
| CORE-028 | ✅ snake_case file naming (cortex_sync.py) |
| CORE-035 | ✅ Single canonical sync implementation — no duplicates |
| CORE-049 | ✅ Progress bars in Chat; no terminal narration |
| CORE-064 | ✅ Sync session BLOCKED from AC_COMPLETE while conflicts remain |
