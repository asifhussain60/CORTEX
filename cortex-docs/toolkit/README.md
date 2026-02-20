# CORTEX Toolkit

**Unified toolkit modules exposed via MCP for operational excellence.**

**Feature:** 90 (Toolkit Centralization)  
**Status:** Production  
**MCP Tools:** 5 (diagnose, verify, cleanup, validate, analyze)

---

## Overview

The CORTEX Toolkit consolidates 20+ operational scripts into 5 reusable modules, each exposed via MCP tools for Copilot Chat integration. This eliminates script sprawl and provides consistent, tested interfaces for common operations.

### Modules

| Module | Purpose | MCP Tool | Tests |
|--------|---------|----------|-------|
| **Diagnostics** | MCP health checking | `toolkit_diagnose` | 19/20 |
| **Setup** | Environment verification | `toolkit_verify` | 18/18 |
| **Cleanup** | Automated cleanup strategies | `toolkit_cleanup` | 15/15 |
| **Validation** | Governance & production readiness | `toolkit_validate` | 18/18 |
| **Analysis** | Audit trace & performance analysis | `toolkit_analyze` | N/A |

**Total:** 84/85 tests passing (98.8%) | **Duration:** 0.42s

---

## Module Reference

### 1. Diagnostics (`cortex/toolkit/diagnostics/`)

**Purpose:** Comprehensive MCP environment health checking.

**Class:** `MCPHealthChecker`

**Methods:**
- `check_all()` — Run all diagnostic checks
- `check_mcp_configuration()` — Verify MCP server config
- `check_virtual_environment()` — Validate venv setup
- `check_vscode_settings()` — Check .vscode/settings.json
- `check_tool_availability()` — Verify MCP tools registered

**Example:**
```python
from cortex.toolkit.diagnostics import MCPHealthChecker

checker = MCPHealthChecker()
result = checker.check_all()
print(f"Status: {result['status']}")
print(f"Issues: {len(result['failed_checks'])}")
```

---

### 2. Setup Verification (`cortex/toolkit/setup/`)

**Purpose:** Cross-platform environment verification.

**Class:** `SetupVerifier`

**Methods:**
- `verify_environment(platform='auto')` — Full environment check
- `check_python_version()` — Verify Python ≥3.9
- `check_virtual_environment()` — Validate venv exists
- `check_dependencies()` — Verify requirements.txt
- `check_vscode_settings()` — Cross-platform MCP config
- `check_mcp_configuration()` — MCP server setup
- `check_git_configuration()` — Git hooks configured

**Example:**
```python
from cortex.toolkit.setup import SetupVerifier

verifier = SetupVerifier()
result = verifier.verify_environment()
print(f"Platform: {result['platform']}")
print(f"Verified: {result['all_passed']}")
```

---

### 3. Cleanup Automation (`cortex/toolkit/cleanup/`)

**Purpose:** Automated cleanup strategies (CORE-002 enforcement).

**Class:** `VacuumAutomation`

**Strategies:**
1. **Markdown Cleanup** — Remove sprawl outside .github/
2. **Debug Markers** — Clean CORTEX_DEBUG comments
3. **Pycache** — Remove __pycache__ directories
4. **Session Data** — Archive old session files
5. **Build Artifacts** — Clean .pyc, .egg-info, etc.

**Methods:**
- `execute_all_strategies(dry_run=False)` — Run all cleanup
- `cleanup_markdown_sprawl(dry_run=False)` — CORE-002 enforcement
- `cleanup_debug_markers(dry_run=False)` — Remove debug code
- `cleanup_pycache(dry_run=False)` — Python cache cleanup
- `cleanup_session_artifacts(dry_run=False)` — Session archival
- `cleanup_build_artifacts(dry_run=False)` — Build cleanup

**Example:**
```python
from cortex.toolkit.cleanup import VacuumAutomation

vacuum = VacuumAutomation(dry_run=True)
result = vacuum.execute_all_strategies()
print(f"Files to clean: {result['files_affected']}")
```

---

### 4. Governance Validation (`cortex/toolkit/validation/`)

**Purpose:** Production readiness and compliance checking.

**Class:** `GovernanceValidator`

**Methods:**
- `validate_production_readiness(dry_run=False)` — Full assessment (8 categories)
- `check_governance_alignment()` — CORE rules compliance
- `assess_security_posture()` — OWASP checks
- `generate_readiness_report(report)` — Formatted output

**Categories:**
1. Infrastructure (Python, directories)
2. Dependencies (requirements.txt)
3. MCP Server (configuration, tools)
4. Docker Deployment (Dockerfile, compose)
5. Security Configuration (OWASP, secrets)
6. Monitoring (Prometheus, Grafana)
7. Tests (coverage, suite)
8. Governance Files (.github structure)

**Example:**
```python
from cortex.toolkit.validation import GovernanceValidator

validator = GovernanceValidator()
report = validator.validate_production_readiness()
print(f"Status: {report.overall_status}")
print(f"Score: {report.readiness_score:.1f}%")

formatted = validator.generate_readiness_report(report)
print(formatted)
```

---

### 5. Analysis (`cortex/toolkit/analysis/`)

**Purpose:** Audit trace and performance analysis.

**Class:** `ToolkitAnalyzer`

**Analysis Types:**
- **Traces** — AC_START/AC_COMPLETE audit markers
- **Performance** — Execution metrics (future)
- **Usage** — Tool usage patterns (future)
- **Health** — System health indicators

**Example:**
```python
from cortex.toolkit.analysis import ToolkitAnalyzer

analyzer = ToolkitAnalyzer()
result = analyzer.analyze_audit_traces()
print(f"Started: {result['total_started']}")
print(f"Completed: {result['total_completed']}")
print(f"Completion Rate: {result['completion_rate']:.1f}%")
```

---

## MCP Tool Usage

All toolkit modules are exposed via MCP tools for Copilot Chat integration.

### `toolkit_diagnose`

**Purpose:** Run MCP diagnostics

**Parameters:**
- `operation` (optional): `full`, `mcp`, `venv`, `settings`, `tools` (default: `full`)

**Example:**
```
User: /toolkit_diagnose operation=mcp
AI: [Runs MCPHealthChecker.check_mcp_configuration()]
```

---

### `toolkit_verify`

**Purpose:** Verify environment setup

**Parameters:**
- `platform` (optional): `auto`, `windows`, `macos`, `linux` (default: `auto`)

**Example:**
```
User: /toolkit_verify platform=macos
AI: [Runs SetupVerifier.verify_environment(platform='macos')]
```

---

### `toolkit_cleanup`

**Purpose:** Run automated cleanup

**Parameters:**
- `strategy` (optional): `markdown`, `pycache`, `debug`, `sessions`, `builds`, `all` (default: `all`)
- `dry_run` (optional): `true`, `false` (default: `false`)

**Example:**
```
User: /toolkit_cleanup strategy=markdown dry_run=true
AI: [Runs VacuumAutomation.cleanup_markdown_sprawl(dry_run=True)]
```

---

### `toolkit_validate`

**Purpose:** Validate governance and production readiness

**Parameters:**
- `validation_type` (optional): `governance`, `production`, `security`, `compliance`, `all` (default: `all`)
- `dry_run` (optional): `true`, `false` (default: `false`)

**Example:**
```
User: /toolkit_validate validation_type=security
AI: [Runs GovernanceValidator.assess_security_posture()]
```

---

### `toolkit_analyze`

**Purpose:** Analyze audit traces and performance

**Parameters:**
- `analysis_type` (optional): `traces`, `performance`, `usage`, `health` (default: `traces`)
- `path` (optional): Path to analyze (default: workspace root)

**Example:**
```
User: /toolkit_analyze analysis_type=traces
AI: [Runs ToolkitAnalyzer.analyze_audit_traces()]
```

---

## CLI Fallback Commands (DEPRECATED)

**⚠️ WARNING:** Direct script usage is deprecated. Use MCP tools via Copilot Chat instead.

**Migration Path:**

| Old Command | New MCP Tool |
|-------------|--------------|
| `python .cortex-runtime/diagnose-mcp.py` | `toolkit_diagnose` |
| `python .cortex-runtime/setup-mcp.py --verify` | `toolkit_verify` |
| `python scripts/vacuum.py` | `toolkit_cleanup` |
| `python scripts/validate-production.py` | `toolkit_validate validation_type=production` |
| `python scripts/audit_traces.py` | `toolkit_analyze analysis_type=traces` |

**Why MCP?**
- ✅ Consistent interface (all operations through Copilot Chat)
- ✅ Tested (84/85 tests passing)
- ✅ Integrated (governance, TDD, audit trail)
- ✅ Discoverable (cortex_tools_catalog)

---

## Testing

### Run All Toolkit Tests

```bash
pytest tests/toolkit/ tests/mcp/tools/test_toolkit_tools.py -v
```

**Expected:** 84/85 passing (98.8%)

### Run Specific Module Tests

```bash
# Diagnostics
pytest tests/toolkit/test_mcp_health_checker.py -v

# Setup
pytest tests/toolkit/test_setup_verifier.py -v

# Cleanup
pytest tests/toolkit/test_vacuum_automation.py -v

# Validation
pytest tests/toolkit/test_governance_validator.py -v

# MCP Integration
pytest tests/mcp/tools/test_toolkit_tools.py -v
```

---

## Architecture

### Before Iteration 90 (Script Sprawl)

```
scripts/
├── diagnose-mcp.py
├── setup-mcp.py
├── vacuum.py
├── validate-production.py
├── validate_governance_alignment.py
├── audit_traces.py
├── check-env.py
└── ... 15+ more scripts
```

**Issues:**
- ❌ Duplication (similar logic in multiple scripts)
- ❌ No tests (scripts not tested systematically)
- ❌ Inconsistent interfaces (different CLI args)
- ❌ Hard to maintain (scattered across repository)

### After Iteration 90 (Toolkit Centralization)

```
cortex/toolkit/
├── diagnostics/        → MCPHealthChecker
├── setup/             → SetupVerifier
├── cleanup/           → VacuumAutomation
├── validation/        → GovernanceValidator
└── analysis/          → ToolkitAnalyzer

cortex/mcp/tools/toolkit/
├── diagnose.py        → toolkit_diagnose
├── verify.py          → toolkit_verify
├── cleanup.py         → toolkit_cleanup
├── validate.py        → toolkit_validate
└── analyze.py         → toolkit_analyze
```

**Benefits:**
- ✅ Consolidated (20+ scripts → 5 modules)
- ✅ Tested (84/85 tests, 98.8% coverage)
- ✅ MCP-integrated (Copilot Chat usage)
- ✅ Maintainable (single source of truth)
- ✅ Reusable (modules used by multiple tools)

---

## Maintenance

### Adding New Toolkit Module

1. **Create Module** — `cortex/toolkit/new_module/`
2. **Write Tests** — `tests/toolkit/test_new_module.py`
3. **Create MCP Tool** — `cortex/mcp/tools/toolkit/new_tool.py`
4. **Register Tool** — Update `cortex/mcp/tools/__init__.py`
5. **Document** — Update this README

### Deprecating Old Scripts

1. Add deprecation warning to script header
2. Add runtime warning message
3. Provide migration path (MCP tool replacement)
4. Archive to `.cortex-runtime/archive/pre-toolkit/`

---

## direction

### Iteration 90 (Current)
- ✅ S1-S5: MCPHealthChecker, SetupVerifier, VacuumAutomation
- ✅ S6: GovernanceValidator
- ✅ S7: 5 MCP tools (diagnose, verify, cleanup, validate, analyze)
- 🔵 S8: Testing & documentation (this file)
- ⚪ S9: Migration & cleanup (deprecate old scripts)

### Future Enhancements
- Performance analysis (toolkit_analyze performance)
- Usage patterns (toolkit_analyze usage)
- Automated remediation (auto-fix common issues)
- Dashboard integration (visualize toolkit metrics)

---

## Support

**Issues?** Check diagnostics first:
```
User: /toolkit_diagnose operation=full
```

**Environment issues?** Verify setup:
```
User: /toolkit_verify platform=auto
```

**Need cleanup?** Run dry-run first:
```
User: /toolkit_cleanup strategy=all dry_run=true
```

**Production readiness?** Full assessment:
```
User: /toolkit_validate validation_type=all
```

---

**Iteration 90:** Toolkit Centralization  
**Status:** 70% Complete (S1-S7 done, S8-S9 pending)  
**Tests:** 84/85 passing (98.8%)  
**MCP Tools:** 31 total (26 existing + 5 toolkit)
