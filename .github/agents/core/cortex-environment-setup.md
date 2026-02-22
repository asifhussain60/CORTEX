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
  → cortex_sample_tool responds in Copilot Chat
  → if no response → MCP not active → see MCP Config below

Step 4: Test Runner
  → python3 -m pytest tests/ -n auto --dist loadscope --co -q
  → confirm: collection passes with no errors

Step 5: Governance Rules
  → cortex_load_core_rules
  → confirm: 22 rules loaded from cortex-registry/core/
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

**Verify MCP:** Call `cortex_sample_tool` in Copilot Chat. If it responds → MCP active.

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
| MCP active | `cortex_sample_tool` (Copilot Chat) | Tool responds |
| Test collection | `pytest --co -q` | 0 collection errors |
| Governance rules | `cortex_load_core_rules` | 22 rules present |
| Dependencies | `cortex_check_dependency_drift` | 0 drift items |

**Enforcement:** Session HALTS if any P0 check fails for production operations.

---

## Common Failures + Fixes

| Failure | Fix |
|---|---|
| `ModuleNotFoundError: cortex` | Run `pip install -e ".[dev]"` from workspace root |
| MCP tools missing in Copilot Chat | Verify `.vscode/settings.json` MCP config, reload VS Code |
| Collection errors in pytest | Check: `pytest --co -q 2>&1 | grep ERROR` |
| Dependency drift | Run `pip install -r requirements.txt` |
| 22 rules not loading | Verify `cortex-registry/core/` YAML files are present |

---

## Test Commands

```bash
# Full suite parallel
python3 -m pytest tests/ -n auto --dist loadscope --tb=short

# Unit tests only
python3 -m pytest tests/unit/ -n auto --dist loadscope -v

# Serial debug
python3 -m pytest tests/ -p no:xdist --tb=long -v -s

# Golden tests (deterministic, serial)
python3 -m pytest tests/golden/ -p no:xdist --tb=short -v
```

---

## ⛔ Deleted Constructs — Never Reference

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
- MCP: 25 tools in `cortex/mcp/tools/`
- Governance rules: 22 in `cortex-registry/core/`
- Tests: 15,230 total, runner: `pytest -n auto --dist loadscope`
