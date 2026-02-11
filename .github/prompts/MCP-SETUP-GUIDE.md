# CORTEX MCP Integration Setup Guide

**Version:** 1.0 | **Authority:** Phase 25 + Phase 48 + Phase 49  
**Status:** ✅ PRODUCTION | **Zero-Exception Requirement:** YES  
**Last Updated:** 2026-02-08

---

## 🎯 Executive Summary

CORTEX now includes a **zero-exception MCP integration setup** that:

- ✅ Automatically configures VS Code MCP integration on first run
- ✅ Ensures all users have identical MCP setup (no manual steps)
- ✅ Validates Python environment and dependencies
- ✅ Injects MCP configuration into `.vscode/settings.json`
- ✅ Logs all setup actions for debugging
- ✅ Idempotent (safe to run multiple times)
- ✅ Fails gracefully with clear error messages

**Result:** Every user gets MCP tools in Copilot Chat with ZERO manual configuration steps.

---

## 🚀 Automatic Setup (Triggered at Session Start)

### Trigger Points

MCP setup is triggered **automatically** at these points:

1. **First Copilot Chat in new workspace** — cortex-architect.md runs pre-flight check
2. **After CORTEX ecosystem upgrade** — cortex-environment-setup.md runs MCP setup
3. **Manual trigger** — Run `.cortex/setup-mcp.py` in terminal

### Setup Flow

```
Session Start
    ↓
PRE-FLIGHT VALIDATION (cortex-environment-setup.md)
    ├─ Check Python >= 3.9.0
    ├─ Check .venv/bin/python exists
    ├─ Check cortex/mcp module found
    ├─ Check .vscode directory writable
    └─ [All checks pass] → Proceed to MCP setup
    ↓
MCP INTEGRATION SETUP (.cortex/setup-mcp.py)
    ├─ STEP 1: Workspace root resolution
    ├─ STEP 2: Virtual environment detection
    ├─ STEP 3: Create/update .vscode/settings.json
    ├─ STEP 4: Inject MCP configuration
    ├─ STEP 5: Verify MCP module exists
    ├─ STEP 6: Log setup results to .cortex/setup.log
    ├─ STEP 7: Notify user
    └─ [Success] → "Restart Copilot for changes to take effect"
    ↓
USER ACTION: Restart Copilot
    ├─ Command Palette → Developer: Reload Window
    └─ [Reload completes] → MCP tools available in Copilot Chat
    ↓
✅ READY: cortex_process_request and 27 other MCP tools available (28 total)
```

---

## 📋 What Gets Configured

### .vscode/settings.json Injection

The following configuration is injected into `.vscode/settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "cortex.mcp"],
      "env": {
        "CORTEX_ENV": "development",
        "CORTEX_MCP_SERVER": "true",
        "PYTHONPATH": "${workspaceFolder}",
        "PATH": "${workspaceFolder}/.venv/bin:$PATH"
      }
    }
  }
}
```

**Key Points:**
- `${workspaceFolder}` is resolved to absolute path at setup time
- `.venv/bin/python` is the virtual environment Python interpreter
- Environment variables ensure CORTEX can find all dependencies
- Configuration is merged with existing settings (non-destructive)

---

## ✅ Validation Checklist

Before MCP setup completes, these checks MUST pass:

| Check | Requirement | Failure Behavior |
|-------|-------------|------------------|
| **Python Version** | >= 3.9.0 | Error: Upgrade Python |
| **Virtual Environment** | `.venv/bin/python` exists | Error: Run `python -m venv .venv` |
| **MCP Module** | `cortex/mcp/__init__.py` exists | Error: Reinstall CORTEX package |
| **.vscode Directory** | Writable | Error: Check permissions |
| **.vscode/settings.json** | Valid JSON syntax | Error: Fix JSON or delete file |
| **MCP Module Files** | `cortex/mcp/__main__.py` readable | Error: Reinstall CORTEX package |

**CRITICAL:** All checks MUST pass or setup HALTS.

---

## 🔍 Logging & Debugging

### Setup Log Location

All setup actions are logged to: `.cortex/setup.log`

**Example log output:**

```
[2026-02-08 14:40:01,984] INFO: ===================================================================================
[2026-02-08 14:40:01,984] INFO: CORTEX MCP Integration Setup
[2026-02-08 14:40:01,984] INFO: Workspace: /Users/asifhussain/PROJECTS/CORTEX
[2026-02-08 14:40:01,984] INFO: User: asifhussain
[2026-02-08 14:40:01,984] INFO: ===================================================================================
[2026-02-08 14:40:01,984] INFO: ✅ Python 3.9.6 (>= 3.9.0)
[2026-02-08 14:40:01,984] INFO: ✅ Virtual environment: /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python
[2026-02-08 14:40:01,984] INFO: ✅ MCP module found: cortex/mcp/__init__.py
[2026-02-08 14:40:01,984] INFO: ✅ .vscode directory exists: /Users/asifhussain/PROJECTS/CORTEX/.vscode
[2026-02-08 14:40:01,984] INFO: ✅ JSON valid: .vscode/settings.json
[2026-02-08 14:40:01,984] INFO: ✅ MCP configuration injected into .vscode/settings.json
[2026-02-08 14:40:01,984] INFO: ✅ MCP server __main__.py module verified
[2026-02-08 14:40:01,984] INFO:    (Server will start when invoked by Copilot)
[2026-02-08 14:40:01,984] INFO: ===================================================================================
[2026-02-08 14:40:01,984] INFO: ✅ SETUP COMPLETE - MCP integration configured successfully
[2026-02-08 14:40:01,984] INFO: ⚡ Next: Restart Copilot for changes to take effect
```

### Troubleshooting with Logs

**To debug setup issues:**

1. Check `.cortex/setup.log` for error messages
2. Verify each check passed (✅ or ❌)
3. Address the first FAILED check
4. Re-run setup: `python .cortex/setup-mcp.py`

---

## 🛠️ Manual Setup (If Automatic Setup Fails)

### Prerequisites

```bash
# Verify Python
python --version  # Should be >= 3.9.0

# Verify virtual environment
source .venv/bin/activate
pip list  # Should show installed packages
```

### Manual MCP Configuration

If automatic setup fails, you can manually configure MCP:

1. **Create `.vscode/settings.json` if missing:**
   ```bash
   mkdir -p .vscode
   echo '{}' > .vscode/settings.json
   ```

2. **Add MCP server configuration:**
   ```bash
   # Use your favorite editor to edit .vscode/settings.json
   # Add the following to the JSON object:
   ```
   ```json
   {
     "github.copilot.chat.mcpServers": {
       "cortex": {
         "command": "${workspaceFolder}/.venv/bin/python",
         "args": ["-m", "cortex.mcp"],
         "env": {
           "CORTEX_ENV": "development",
           "CORTEX_MCP_SERVER": "true",
           "PYTHONPATH": "${workspaceFolder}",
           "PATH": "${workspaceFolder}/.venv/bin:$PATH"
         }
       }
     }
   }
   ```

3. **Verify JSON syntax:**
   ```bash
   python -m json.tool .vscode/settings.json > /dev/null && echo "✅ JSON valid"
   ```

4. **Restart Copilot:**
   - Command Palette (Cmd+Shift+P)
   - Type: "Developer: Reload Window"
   - Press Enter

---

## 🔧 Running Setup Manually

If you need to re-run setup for any reason:

```bash
# From workspace root
python .cortex/setup-mcp.py
```

**Output:**
```
🔌 CORTEX MCP INTEGRATION SETUP COMPLETE
============================================================================
✅ Configuration Status: SUCCESS

What was configured:
  ✅ .vscode/settings.json updated with cortex MCP server
  ✅ Python interpreter: ${workspaceFolder}/.venv/bin/python
  ✅ MCP module: cortex.mcp ready
  ✅ Environment variables configured
  ✅ Server startup verification passed

NEXT STEP:
⚡ **Restart Copilot for changes to take effect**
```

---

## 📦 Available MCP Tools (After Restart) — 28 Tools Total

Once setup is complete and Copilot is restarted, these tools become available:

**Core Orchestrator Tools (3):**
| Tool | Purpose |
|------|---------|
| `cortex_process_request` | Main TDD implementation + routing |
| `cortex_total_recall` | Feature discovery + capability search |
| `cortex_challenge` | Challenge gate + disagreement detection |

**LENS Analysis Tools (5):**
| Tool | Purpose |
|------|---------|
| `cortex_lens_analyze` | Unified code intelligence (git+AST+comments) |
| `cortex_git_history` | Git context analysis (24h window) |
| `cortex_ast_analyze` | AST structure + complexity analysis |
| `cortex_extract_comments` | Comment/TODO/FIXME extraction |
| `cortex_detect_duplicates` | CORE-035 violation detection |

**Plan Lifecycle Tools (4):**
| Tool | Purpose |
|------|---------|
| `cortex_plan_setup` | Pre-execution phase hook |
| `cortex_plan_execute_autonomous` | Multi-stage autonomous execution |
| `cortex_plan_teardown` | Post-execution cleanup + sync |
| `cortex_plan_sync` | Manual dashboard synchronization |

**Validation Tools (1):**
| Tool | Purpose |
|------|---------|
| `cortex_validate_holistically` | Phase 48 holistic validation gate |

**Governance Tools (5):**
| Tool | Purpose |
|------|---------|
| `check_phase_lock` | Phase lock verification |
| `validate_ac_id` | AC-ID validation |
| `canonicalize_intent` | Intent normalization |
| `enforce_operation` | Governance enforcement |
| `get_phase_status` | Phase status query |

**Knowledge Tools (3):**
| Tool | Purpose |
|------|---------|
| `search_knowledge_base` | Knowledge base search |
| `analyze_knowledge_gap` | Gap analysis |
| `generate_knowledge_summary` | Knowledge summarization |

**Orchestrator Operations Tools (4):**
| Tool | Purpose |
|------|---------|
| `monitor_orchestrator_health` | Health monitoring |
| `diagnose_orchestrator_issues` | Issue diagnostics |
| `optimize_orchestrator_config` | Config optimization |
| `get_operation_status` | Operation status query |

**Utility Tools (1):**
| Tool | Purpose |
|------|---------|
| `transform_tool` | Data format transformation (JSON/YAML/XML) |

**Note:** sample_tool and echo_tool removed (dev-only, Phase 54 cleanup)

---

## ⚠️ Common Issues & Fixes

### Issue: "MCP tools not appearing in Copilot Chat"

**Cause:** VS Code needs reload to register MCP server  
**Fix:**
1. Command Palette → Developer: Reload Window
2. Wait 10 seconds for VS Code to reload
3. Try using an MCP tool in Copilot Chat

### Issue: "Python version error (need >= 3.9.0)"

**Cause:** System Python is older version  
**Fix:**
1. Install Python 3.9+ from python.org
2. Verify: `python --version`
3. Re-run setup: `python .cortex/setup-mcp.py`

### Issue: "Virtual environment not found"

**Cause:** `.venv` directory doesn't exist  
**Fix:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python .cortex/setup-mcp.py
```

### Issue: "Invalid JSON in .vscode/settings.json"

**Cause:** JSON syntax error in settings file  
**Fix:**
```bash
# Backup current file
cp .vscode/settings.json .vscode/settings.json.backup

# Validate JSON
python -m json.tool .vscode/settings.json

# If error, either:
# 1. Fix the JSON syntax manually, or
# 2. Delete the file and re-run setup
rm .vscode/settings.json
python .cortex/setup-mcp.py
```

### Issue: "MCP module initialization failed"

**Cause:** cortex/mcp module is broken or missing dependencies  
**Fix:**
```bash
# Reinstall CORTEX package
pip install -e .

# Re-run setup
python .cortex/setup-mcp.py
```

---

## 📊 Setup Idempotency

**Important:** MCP setup is **idempotent** — safe to run multiple times.

**Guarantees:**
- ✅ Running setup twice produces same result
- ✅ No duplicate MCP server entries created
- ✅ Existing settings preserved (merge, not overwrite)
- ✅ No errors if already configured

**Example:**
```bash
# First run
python .cortex/setup-mcp.py
# Result: ✅ SETUP COMPLETE

# Second run (same session)
python .cortex/setup-mcp.py
# Result: ✅ SETUP COMPLETE (no duplicates, no errors)
```

---

## 🔄 Integration with CORTEX Prompts & Agents

### cortex-architect.prompt.md

**Pre-flight section** now includes:
- MCP configuration requirements
- Zero-exception setup mandate
- Tool list after setup

### cortex-environment-setup.md

**New MCP Setup section** includes:
- 7-step automatic configuration process
- Validation checklist
- Failure recovery instructions
- Idempotency guarantees

### .cortex/setup-mcp.py

**Automated setup script** that:
- Validates environment prerequisites
- Creates/updates .vscode/settings.json
- Injects MCP server configuration
- Logs all actions to .cortex/setup.log
- Notifies user with next steps

---

## 🎯 Success Criteria

MCP integration is **complete and successful** when:

1. ✅ `.vscode/settings.json` contains MCP server configuration
2. ✅ `cortex_process_request` appears in Copilot Chat tools
3. ✅ All 28 MCP tools appear in tool list
4. ✅ Setup log shows "✅ SETUP COMPLETE"
5. ✅ User can invoke MCP tools without errors

**Verification command in Copilot Chat:**
```
/list cortex tools
```

Should show all 28 MCP tools as available (organized by 8 categories).

---

## 📚 Related Documentation

- **cortex-architect.prompt.md** — PRE-FLIGHT AUTO-SETUP section
- **cortex-environment-setup.md** — MCP Integration Setup section
- **.cortex/setup-mcp.py** — Automated setup script
- **.cortex/setup.log** — Setup execution log

---

## 🚀 Next Steps

1. **Verify setup:** Check `.cortex/setup.log` for success
2. **Restart Copilot:** Command Palette → Developer: Reload Window
3. **Test MCP tools:** Try `/list cortex tools` in Copilot Chat
4. **Start using CORTEX:** Use `cortex_process_request` for implementations

---

**Questions?** Check `.cortex/setup.log` for detailed setup information, or manually verify JSON syntax in `.vscode/settings.json`.
