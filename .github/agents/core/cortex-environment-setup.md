---
scope: non-production-admin
---
# CORTEX Environment Setup Agent

**Updated:** 2026-02-20 | ## Role

Pre-flight validation of the CORTEX development environment. Must pass before any IMPLEMENT / FIX / AUDIT operation.

---

## Activation

Triggered by **SETUP** intent, or automatically at session start if environment state is unknown.

---

## 5-Step Validation Flow

```
Step 1: Python Version
  → python3 --version (must be 3.9+)

Step 2: Package Install
  → pip install -e ".[dev]" (editable install from pyproject.toml)
  → confirm: import cortex succeeds

Step 3: MCP P0 Gate
  → cortex_verify (op: mcp) responds in Copilot Chat
  → if no response → MCP not active → see MCP Config below

Step 4: Test Runner (collection check only — does NOT run tests)
  → python3 -m pytest tests/ -n auto --dist loadscope --co -q
  → confirm: collection passes with no errors

Step 5: Governance Rules
  → cortex_load (op: rules)
  → confirm: 38 rules loaded from cortex-registry/core/tier0-skull/skull-rules.yaml
```

---

## MCP Configuration

MCP auto-starts with VS Code via `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Verify MCP:** Call `cortex_verify` (op: `mcp`) in Copilot Chat. If it responds → MCP active.

**Manual start (escape hatch):**
```bash
python3 -m cortex.mcp
```

---

## Environment Gate Table

| Check | Command | Pass Condition |
|---|---|---|
| Python version | `python3 --version` | >= 3.9 |
| Package install | `pip install -e ".[dev]"` | No errors |
| Cortex import | `python3 -c "import cortex"` | No ImportError |
| MCP active | `cortex_verify` (op: `mcp`) (Copilot Chat) | Tool responds |
| Test collection | `pytest --co -q` | 0 collection errors |
| Governance rules | `cortex_load` (op: `rules`) | 38 rules present |
| Dependencies | `cortex_check` (op: `dependencies`) | 0 drift items |

**Enforcement:** Session HALTS if any P0 check fails for production operations.

---

## Common Failures + Fixes

| Failure | Fix |
|---|---|
| `ModuleNotFoundError: cortex` | Run `pip install -e ".[dev]"` from workspace root |
| MCP tools missing in Copilot Chat | Verify `.vscode/settings.json` MCP config, reload VS Code |
| Collection errors in pytest | Check: `pytest --co -q 2>&1 | grep ERROR` |
| Dependency drift | Run `pip install -r requirements.txt` |
| 38 rules not loading | Verify `cortex-registry/core/tier0-skull/skull-rules.yaml` is present |

---

## Test Commands

```bash
# Preflight — wiring checks (< 10s)
python3 scripts/run_tests.py preflight

# Smoke — core functionality (< 60s)
python3 scripts/run_tests.py smoke

# Unit tests only
python3 scripts/run_tests.py file tests/unit/

# Serial debug
python3 -m pytest tests/ -p no:xdist --tb=long -v -s

# Golden tests (deterministic, serial)
python3 scripts/run_tests.py file tests/golden/

# Full suite on-demand only (/healthcheck)
python3 scripts/run_tests.py healthcheck
```

---

## Requirements Validation (Automated Preflight Gate)

Before any CORTEX operation, `UpgradeOrchestrator.validate_requirements()` checks that every `[PREFLIGHT]` and `[PREFLIGHT CRITICAL]` package in `requirements.txt` is installed in the active virtual environment.

- **Missing packages** → P0 violation → automatic `pip install -r requirements.txt` attempted
- **Version mismatches** (pinned `==`) → P1 warning → environment may be stale
- **Broken dependency chains** (`pip check` failures) → P1 violation
- **Silent if all packages satisfied** (CORE-049)

To skip (CI/CD environments): set `CORTEX_SKIP_PREFLIGHT=true`.

---

## Windows Setup

CORTEX runs natively on Windows without WSL. WSL is supported as a secondary environment but not the primary target — all CORTEX paths work natively.

**Requirements:**
- Python 3.9+ via [python.org](https://python.org) installer or Windows Store (not WSL)
- VS Code with Python extension (`ms-python.python`)
- Git for Windows ([git-scm.com](https://git-scm.com))

**MCP server on Windows** — use `python` (not `python3`) in `.vscode/settings.json`:
```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```
`scripts/setup-mcp.py` auto-detects the OS and uses `sys.executable` (the current interpreter path) as the MCP command — run `python scripts\setup-mcp.py` to configure automatically.

**Windows test commands** (use `python` instead of `python3`, backslash paths):
```cmd
python scripts\run_tests.py preflight
python scripts\run_tests.py smoke
python scripts\run_tests.py healthcheck
python -m pytest tests/ -n auto --dist loadscope --tb=short
```
All `make` commands have equivalent VS Code Task entries in `tasks.json` for Windows users who cannot run `make`.

---

## 🔒 Admin-Sovereign Folders (Never Overwritten by Upgrades)

The following folders are user-sovereign and are **never overwritten** by automated inflight upgrades (`check_upstream_and_merge()`):

| Folder | Reason |
|--------|--------|
| `docs/` | Published documentation site — user controls all HTML/CSS content |
| `_workspaces/` | Session-specific workspace files, chat histories, local prompts |
| `cortex-sts/` | Sample tenant system — admin-specific analysis artifacts |
| `.github/prompts/cortex-doc.prompt.md` | Documentation system prompt — admin-configured per deployment |
| `.github/agents/docs/` | Documentation governance agents — tightly coupled to user's docs/ site structure |

To add further exclusions without code changes, set `CORTEX_UPGRADE_EXCLUDE_PATHS` to a comma-separated list of additional paths.

---

- `cortex/brain/` — dissolved post-refactor
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `cortex_process_request` — removed MCP tool
- `cortex_lens_analyze` — removed MCP tool
- Phase 49 / CCL / CrystallizedContext — removed
- `_archive/` — deleted directory

---

## Canonical Reference

- Package: `cortex` (single canonical import, `pyproject.toml`)
- MCP: 29 registered (39 target) tools in `cortex/mcp/tools/`
- Governance rules: 38 CORE + 2 AC in `cortex-registry/core/tier0-skull/skull-rules.yaml`
- Tests: 16,942 total, runner: `pytest -n auto --dist loadscope`
