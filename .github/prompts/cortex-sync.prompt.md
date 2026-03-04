---
scope: non-production-admin
prompt_id: cortex-sync
status: active
mode: DESIGN
author: Asif Hussain
updated: 2026-02-25
agent: cortex-sync-agent.md
orchestrators_used:
  - GitOrchestrator (cortex/orchestrators/git/git_orchestrator.py)
  - SanitizationOrchestrator (cortex/orchestrators/git/sanitization_orchestrator.py)
  - GitPublishOrchestrator (cortex/orchestrators/git/git_publish_orchestrator.py)
mcp_tools:
  - cortex_validate
  - cortex_governance
  - cortex_git
token_cost_estimate: 2800
production_files:
  # These files ARE production-core — NEVER excluded from sync targets
  - ".github/prompts/CORTEX.prompt.md"
  - ".github/prompts/cortex-architect.prompt.md"
  - ".github/agents/core/CORTEX.md"
  - ".github/agents/core/cortex-executor.md"
  - ".github/agents/core/cortex-architect.md"
  - ".github/copilot-instructions.md"
---

# CORTEX Sync Prompt

**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
**Updated:** 2026-02-25 | **Authority:** `.github/prompts/cortex-sync.prompt.md`  
**Agent:** `.github/agents/core/cortex-sync-agent.md`

---

## 🎯 Purpose

One-way intelligent sync from the **CORTEX** repository (upstream, personal) into a
**target company folder** (downstream, write-only from CORTEX's perspective). No code
ever flows back from the company folder into CORTEX.

**Privacy guarantee:** Every file passes through `SanitizationOrchestrator` before
it crosses the CORTEX → Company boundary. PII, secrets, and proprietary patterns are
stripped or morphed before copy.

**Merge guarantee:** Files already edited in the company folder are never blindly
overwritten. A 3-way merge (base = last sync SHA, ours = company edits, theirs = new
CORTEX version) is performed. Conflicts surface inline in Copilot Chat — you decide.

---

## 🔌 Activation

Invoke from Copilot Chat:

```
/sync target=<absolute_path_to_company_folder>
```

**Examples:**
```
/sync target=/Users/asif/work/Cortex.Company
/sync target=~/projects/company-cortex
/sync target=/c/dev/CompanyCortex          (Windows WSL)
```

> The `target` parameter is the only required input. It replaces the `Cortex.Company`
> placeholder throughout the agent pipeline. The path must be an absolute path to the
> locally cloned company repository folder.

---

## 🏗️ Architecture Overview

```
User: /sync target=<path>
    ↓
cortex-sync.prompt.md          ← You are here (session driver)
    ↓
cortex-sync-agent.md           ← 4-gate pipeline executor
    ↓
  Gate 1: PULL         git pull origin/CORTEX (CORTEX local branch only)
  Gate 2: DIFF         git diff HEAD@{1}..HEAD --name-only (changed files only)
  Gate 3: SANITIZE     SanitizationOrchestrator (strip PII/secrets per pattern registry)
  Gate 4: MERGE        3-way merge (base=last-sync-SHA, ours=company, theirs=CORTEX)
    ↓
<target>/.cortex-sync-state.yaml  ← State file updated per-file with synced commit SHA
<target>/<file>                   ← Merged output written (conflict-free or surfaced)
```

---

## 📋 Pre-Flight Requirements

Before the agent runs Gate 1, the following must be true:

| Check | Validation | Blocking |
|-------|-----------|---------|
| CORTEX workspace open | VS Code workspace = `/PROJECTS/CORTEX` | ✅ P0 |
| Target path exists | `os.path.isdir(target)` | ✅ P0 |
| CORTEX branch clean or stashable | `git status --porcelain` | ✅ P0 |
| No open conflicts in target | No `<<<<<<` markers in target files | ✅ P0 |
| `SanitizationOrchestrator` importable | `from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator` | ✅ P0 |
| `cortex_validate` MCP tool active | `cortex_verify` op=`mcp` responds | 🟡 P1 warn |

---

## 🔄 Session Flow

### Step 1 — Session Init

```
AC_START: AC-SYNC-{TIMESTAMP}
Load: .cortex-sync-state.yaml from <target> (or create empty if first run)
Display: sync state summary (last sync SHA, file count, pending conflicts)
```

### Step 2 — Gate Execution (via cortex-sync-agent.md)

Agent runs 4 gates sequentially. Each gate must PASS before the next opens.
See `cortex-sync-agent.md` for full gate specifications.

### Step 3 — Conflict Resolution

If Gate 4 produces merge conflicts:
- Each conflicted file is shown inline with 3-way diff
- User decides per file: **accept CORTEX version** | **keep Company version** | **manual merge**
- No file is written until user resolves all conflicts

### Step 4 — State Update + AC_COMPLETE

```
Write: <target>/.cortex-sync-state.yaml (update per-file SHA map)
Emit:  AC_COMPLETE: AC-SYNC-{TIMESTAMP} ✅ {elapsed_ms}ms
       Files synced: N | Sanitized: N | Conflicts resolved: N | Skipped: N
```

---

## 🔒 Privacy Boundary Rules

These rules are P0 — enforced by `SanitizationOrchestrator` in Gate 3:

| Category | Patterns Stripped | Replacement |
|----------|-----------------|-------------|
| Secrets | API keys, tokens, `.env` values | `<REDACTED>` |
| PII | Names, emails, internal user IDs | `<ANONYMIZED>` |
| Proprietary | Internal hostnames, internal service names | `<INTERNAL>` |
| CORTEX-specific | Personal git config, personal SSH config | Excluded from sync entirely |

**Files excluded from sync unconditionally:**
```
.git/
.cortex-runtime/
*.log
*.db
.env*
cortex_brain/state/
.vscode/settings.json    ← personal MCP config — never synced
```

---

## 📁 State File Schema

Location: `<target>/.cortex-sync-state.yaml`  
Owner: Sync agent writes it; gitignore it in the company repo.

```yaml
# CORTEX Sync State — DO NOT EDIT MANUALLY
# Generated by cortex-sync-agent
cortex_sync_state:
  last_sync_at: "2026-02-25T14:30:00Z"
  last_sync_sha: "abc123def456..."
  cortex_branch: "CORTEX"
  cortex_remote: "origin"
  target_path: "/absolute/path/to/company/folder"
  files:
    cortex/orchestrators/core/master_orchestrator.py:
      synced_sha: "abc123..."
      synced_at: "2026-02-25T14:30:00Z"
      status: "clean"          # clean | conflict | skipped | excluded
    cortex/mcp/tools/sync_tool.py:
      synced_sha: "def456..."
      synced_at: "2026-02-25T14:30:00Z"
      status: "clean"
```

---

## ⚡ Quick Reference — Common Scenarios

| Scenario | What Happens |
|----------|-------------|
| First sync (no state file) | All CORTEX files copied after sanitization; state file created |
| Routine sync (company unchanged) | Only diff'd files copied; fast path |
| Company edited a file CORTEX also changed | 3-way merge surfaced inline for human decision |
| Company edited a file CORTEX did NOT change | File is left untouched — not in diff set |
| File deleted in CORTEX | Deletion is NOT propagated to company (safe default) |
| New file added in CORTEX | Copied after sanitization |

> **Deletion safety:** CORTEX deletions are flagged inline but not auto-propagated.
> You explicitly confirm any deletion to apply in the company folder.

---

## 🚦 Command Reference

| Command | Effect |
|---------|--------|
| `/sync target=<path>` | Run full 4-gate sync session |
| `/sync status target=<path>` | Show state file summary, pending conflicts, last SHA |
| `/sync dry-run target=<path>` | Run Gates 1–3, show diff + sanitization preview — no writes |
| `/sync resolve target=<path>` | Resume interrupted sync, show remaining conflicts |
| `/sync reset-state target=<path>` | ⚠️ Clears state file — next run treats everything as first sync |

---

## 🔗 Related Components

| Component | Path | Role |
|-----------|------|------|
| `SanitizationOrchestrator` | `cortex/orchestrators/git/sanitization_orchestrator.py` | Gate 3 privacy engine |
| `GitOrchestrator` | `cortex/orchestrators/git/git_orchestrator.py` | Gate 1 pull pipeline |
| `GitPublishOrchestrator` | `cortex/orchestrators/git/git_publish_orchestrator.py` | Git operations base |
| `cortex-sync-agent.md` | `.github/agents/core/cortex-sync-agent.md` | Gate spec + merge logic |
| CORTEX registry pattern | `cortex-registry/core/` | Sanitization pattern registry |
| `.cortex-runtime/traces/` | `.cortex-runtime/traces/orchestrator-traces.db` | AC marker persistence |

---

## ⛔ What This Is NOT

- ❌ Not a two-way sync — CORTEX ← Company flow is architecturally blocked
- ❌ Not a CI/CD pipeline — runs interactively in Copilot Chat on demand
- ❌ Not a shell script — no terminal automation; human-in-the-loop on conflicts
- ❌ Not a git submodule — no git history entanglement between repos
- ❌ Not a fork sync — does not use GitHub's fork/PR mechanism (privacy boundary)

---

## 🔒 Prompt Classification — Production vs Administrative

During synchronization, the sync agent copies **only production-critical prompts**
to the target runtime path.  All other prompts and agents are classified as
**non-production administrative tools** and remain in the source repository for
maintenance workflows but are **never** copied to the deployed runtime.

### Production Prompts (copied to `<target>`)

| Prompt / Agent | Path |
|---|---|
| `CORTEX.prompt.md` | `.github/prompts/CORTEX.prompt.md` |
| `cortex-architect.prompt.md` | `.github/prompts/cortex-architect.prompt.md` |
| Core agents used by Architect | `.github/agents/core/cortex-executor.md`, `cortex-auditor.md`, `cortex-interactive.md`, `cortex-debugger.md`, `cortex-vacuum.md` |

### Administrative Prompts (NOT copied — maintenance-only)

| Prompt / Agent | Reason |
|---|---|
| `cortex-sync.prompt.md` | Sync infrastructure — not needed at target |
| `cortex-total-recall.prompt.md` | Certification pipeline — source-only |
| `cortex-trainer.prompt.md` | Training pipeline — source-only |
| `cortex-doc.prompt.md` | Documentation generation — source-only |
| All agents under `.github/agents/docs/` | Documentation tooling — source-only |
| All agents under `.github/agents/certification/` | Certification — source-only |
| All agents under `.github/agents/education/` | Education — source-only |
| `MCP-SETUP-GUIDE.md`, `MCP-ORCHESTRATOR-MAPPING.md` | Setup references — source-only |
| `phase-creation-standards.md`, `master-planner.md` | Planning tools — source-only |

**Gate 3 enforcement:** `SanitizationOrchestrator` skips any file path matching the
administrative prompt patterns above.  This ensures the deployed runtime contains
only production-critical prompts with zero maintenance overhead.
