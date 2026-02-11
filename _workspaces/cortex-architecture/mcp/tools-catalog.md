# CORTEX MCP Tools Catalog

**Total Tools:** 86 | **Updated:** 2026-02-11  
**MCP Server:** stdio/HTTP (Port 8000) | **Protocol:** JSON-RPC 2.0

---

## Overview

This catalog documents all **86** MCP tools exposed by CORTEX. These tools enable AI assistants (GitHub Copilot, Claude, Cursor) to leverage CORTEX's cognitive capabilities through the Model Context Protocol.

### Tool Distribution

| Category | Count | Purpose |
|----------|-------|---------|
| **Core Operations** | 4 | Primary entry points for request processing |
| **LENS Intelligence** | 11 | Deep code analysis and intelligence |
| **Governance & Compliance** | 19 | Rule enforcement and validation |
| **Planning & Execution** | 7 | Phase management and autonomous execution |
| **Debugging & Analysis** | 7 | Debug injection, capture, and analysis |
| **Dashboard & Reporting** | 6 | Visualization and reporting generation |
| **Knowledge & Learning** | 3 | Knowledge base queries and learning |
| **Refactoring & Code Quality** | 3 | Code improvement and refactoring |
| **Utility & System** | 26 | System utilities and support |

---

## Tool Categories

### Core Operations (4 tools)

#### `cortex_challenge`

**Description:** Generate AI-driven challenge to user request using LENS analysis

**Usage Pattern:**
```json
{
  "tool": "cortex_challenge",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_process_remediation_selection`

**Description:** Process user's remediation execution mode selection (1-4). Returns execution mode and parameters for routing.

**Usage Pattern:**
```json
{
  "tool": "cortex_process_remediation_selection",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_process_request`

**Description:** Process user request through CORTEX challenge-driven interaction system

**Usage Pattern:**
```json
{
  "tool": "cortex_process_request",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_total_recall`

**Description:** Discover and recall CORTEX features and components

**Usage Pattern:**
```json
{
  "tool": "cortex_total_recall",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### LENS Intelligence (11 tools)

#### `analyze_governance_impact`

**Description:** Analyze governance impact of proposed operation

**Usage Pattern:**
```json
{
  "tool": "analyze_governance_impact",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `analyze_knowledge_gap`

**Description:** Analyze gaps in knowledge coverage

**Usage Pattern:**
```json
{
  "tool": "analyze_knowledge_gap",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_analyze_config`

**Description:** Analyze configuration file for security issues (secrets, insecure defaults)

**Usage Pattern:**
```json
{
  "tool": "cortex_analyze_config",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_analyze_governance`

**Description:** Analyze governance compliance metrics and trends over time

**Usage Pattern:**
```json
{
  "tool": "cortex_analyze_governance",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_analyze_repository_configs`

**Description:** Analyze all configuration files in a repository for security issues

**Usage Pattern:**
```json
{
  "tool": "cortex_analyze_repository_configs",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_analyze_test_performance`

**Description:** Analyze test suite performance and identify slow tests

**Usage Pattern:**
```json
{
  "tool": "cortex_analyze_test_performance",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_ast_analyze`

**Description:** Analyze Python AST structure, complexity, and dead code

**Usage Pattern:**
```json
{
  "tool": "cortex_ast_analyze",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_analyze`

**Description:** Analyze captured debug logs to detect race conditions, integration issues, and root causes.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_analyze",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_lens_analyze`

**Description:** Unified LENS code intelligence analysis combining git, AST, and comments

**Usage Pattern:**
```json
{
  "tool": "cortex_lens_analyze",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_lens_deep_analyze`

**Description:** Intelligent multi-tier LENS analysis with optional LLM enhancement and company domain context

**Usage Pattern:**
```json
{
  "tool": "cortex_lens_deep_analyze",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_vision_analyze`

**Description:** Analyze images via Vision API for UI elements, URLs, issues, and structural mappings

**Usage Pattern:**
```json
{
  "tool": "cortex_vision_analyze",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### Governance & Compliance (19 tools)

#### `cortex_approve_request`

**Description:** Approve classified request and execute from stored approval session

**Usage Pattern:**
```json
{
  "tool": "cortex_approve_request",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_dashboard_validate`

**Description:** Validate dashboard registry and folder structure

**Usage Pattern:**
```json
{
  "tool": "cortex_dashboard_validate",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_governance_detect`

**Description:** 
    🔍 Detect CORTEX governance violations in 10 iterative cycles.

    Performs comprehensive scanning for:
    - Tool Interception Gap (P0): Missing pre-hook validation
    - Enforcement Gap (P0): Enforcement not called in chat flow
    - MCP Bypass (P0): Direct file operations without MCP
    - Artifact Suppression (P0): Forbidden markdown files
    - Response Generation Gap (P1): No guards in response gen
    - User Validation Gap (P1): No approval gates
    - CI/CD Gap (P1): Missing pre-commit hooks
    - Instruction Violation (P2): File paths in instructions
    - TDD Bypass (P0): Test skip patterns not blocked
    - Audit Trail Gap (P2): AC marker enforcement missing

    Each cycle detects new violations and reports fix strategies.
    Stops when no new violations found or max cycles reached.
    

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_governance_detect",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_governance_fix`

**Description:** 
    🔧 Automatically fix detected governance violations.

    Applies automated fixes for:
    - Creating missing tool interception layer
    - Moving artifacts to correct locations
    - Creating missing CI/CD hooks
    - Cleaning up instruction files

    All fixes are:
    - Non-destructive (creates new files, doesn't delete)
    - Verified after application
    - Logged with AC markers for audit trail
    - Reversible via git

    Returns count of fixes applied and next verification steps.
    

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_governance_fix",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_governance_full_cycle`

**Description:** 
    🔄 Run full governance debugging cycle: Detect → Fix → Verify.

    Performs comprehensive governance violation debugging:
    1. Detect all 10 violation categories
    2. Apply automated fixes
    3. Verify fixes are complete
    4. Generate compliance report
    5. Commit changes with AC markers

    Entire cycle runs autonomously with progress reporting.
    All operations are audit-logged.
    

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_governance_full_cycle",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_governance_verify`

**Description:** 
    ✅ Verify that governance violations have been fixed.

    Re-runs detection after fixes applied to confirm:
    - All P0 violations resolved
    - No new violations introduced
    - Fix quality meets standards
    - No regressions detected

    Provides confidence score based on:
    - Coverage of fixed violations
    - No new violations introduced
    - Hash chain integrity
    - Audit trail completeness
    

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_governance_verify",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_execute_governance`

**Description:** Execute governance actions - enforcement, blocking, remediation, with audit logging

**Usage Pattern:**
```json
{
  "tool": "cortex_execute_governance",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_query_governance`

**Description:** Query governance state, rules, violations, and compliance data from registry

**Usage Pattern:**
```json
{
  "tool": "cortex_query_governance",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_reject_request`

**Description:** Reject classified request and close approval session

**Usage Pattern:**
```json
{
  "tool": "cortex_reject_request",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_report_governance`

**Description:** Generate comprehensive governance compliance reports

**Usage Pattern:**
```json
{
  "tool": "cortex_report_governance",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_validate_against_rules`

**Description:** Validate code/operation against CORE rules with enforcement level checks

**Usage Pattern:**
```json
{
  "tool": "cortex_validate_against_rules",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_validate_architecture`

**Description:** Validate user request against master plan to prevent regression

**Usage Pattern:**
```json
{
  "tool": "cortex_validate_architecture",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_validate_compliance`

**Description:** Validate code against CORE governance rules with real rule checking

**Usage Pattern:**
```json
{
  "tool": "cortex_validate_compliance",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_validate_holistically`

**Description:** Unified pre-implementation validation gate (Phase 48)

**Usage Pattern:**
```json
{
  "tool": "cortex_validate_holistically",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_validate_venv`

**Description:** Validate virtual environment activation

**Usage Pattern:**
```json
{
  "tool": "cortex_validate_venv",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `execute_governance_check`

**Description:** Execute comprehensive governance check on operation

**Usage Pattern:**
```json
{
  "tool": "execute_governance_check",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `query_governance_context`

**Description:** Query execution context for governance rules

**Usage Pattern:**
```json
{
  "tool": "query_governance_context",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `report_governance_status`

**Description:** Generate governance status report

**Usage Pattern:**
```json
{
  "tool": "report_governance_status",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `validate_governance_compliance`

**Description:** Validate operation against governance rules

**Usage Pattern:**
```json
{
  "tool": "validate_governance_compliance",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### Planning & Execution (7 tools)

#### `cortex_audit_remediation_plan`

**Description:** Generate structured remediation plan from audit results. Presents 4 execution options: [1] Autonomous [2] Interactive [3] Review [4] Cancel. Part of ENH-059: Audit-Driven Auto-Planning.

**Usage Pattern:**
```json
{
  "tool": "cortex_audit_remediation_plan",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_fix_plan`

**Description:** Generate a comprehensive fix plan based on debug analysis.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_fix_plan",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_plan_execute_autonomous`

**Description:** Execute entire phase autonomously through all stages with ASCII progress bars

**Usage Pattern:**
```json
{
  "tool": "cortex_plan_execute_autonomous",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_plan_resolve`

**Description:** Intelligently resolve phase operation from user request

**Usage Pattern:**
```json
{
  "tool": "cortex_plan_resolve",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_plan_setup`

**Description:** Execute setup hook before phase implementation

**Usage Pattern:**
```json
{
  "tool": "cortex_plan_setup",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_plan_sync`

**Description:** Manually trigger dashboard sync

**Usage Pattern:**
```json
{
  "tool": "cortex_plan_sync",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_plan_teardown`

**Description:** Execute teardown hook after phase completion

**Usage Pattern:**
```json
{
  "tool": "cortex_plan_teardown",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### Debugging & Analysis (7 tools)

#### `cortex_debug_capture`

**Description:** Capture console logs during test execution. Supports browser-based (Playwright) and CLI capture modes.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_capture",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_cleanup`

**Description:** Remove ALL CORTEX debug markers from injected files, leaving code production-ready.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_cleanup",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_full_cycle`

**Description:** Run complete debug workflow: inject → capture → analyze → fix-plan. Optionally cleanup after.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_full_cycle",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_inject`

**Description:** Inject CORTEX debug markers into repository files for comprehensive debugging. Supports JavaScript, TypeScript, Python, and HTML.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_inject",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_restore`

**Description:** Restore all files from backup (emergency recovery if cleanup fails).

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_restore",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_status`

**Description:** Get current debug session status and metadata.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_status",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_debug_verify`

**Description:** Verify no CORTEX debug markers remain in repository. Useful as pre-commit check.

**Usage Pattern:**
```json
{
  "tool": "cortex_debug_verify",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### Dashboard & Reporting (6 tools)

#### `cortex_dashboard_create_repo`

**Description:** Create a new repository dashboard from template

**Usage Pattern:**
```json
{
  "tool": "cortex_dashboard_create_repo",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_dashboard_delete_repo`

**Description:** Delete a repository dashboard

**Usage Pattern:**
```json
{
  "tool": "cortex_dashboard_delete_repo",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_dashboard_list_repos`

**Description:** List all registered repository dashboards

**Usage Pattern:**
```json
{
  "tool": "cortex_dashboard_list_repos",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_dashboard_update_repo`

**Description:** Update an existing repository dashboard data

**Usage Pattern:**
```json
{
  "tool": "cortex_dashboard_update_repo",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_generate_dashboard_suite`

**Description:** Generate complete static dashboard suite with landing + per-repo dashboards (GPT Spec compliant)

**Usage Pattern:**
```json
{
  "tool": "cortex_generate_dashboard_suite",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_generate_repo_dashboard`

**Description:** Generate single repo dashboard HTML with embedded data

**Usage Pattern:**
```json
{
  "tool": "cortex_generate_repo_dashboard",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### Knowledge & Learning (3 tools)

#### `cortex_ask`

**Description:** Ask educational questions about CORTEX architecture with truth-based verification

**Usage Pattern:**
```json
{
  "tool": "cortex_ask",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `generate_knowledge_summary`

**Description:** Generate knowledge summary for a domain

**Usage Pattern:**
```json
{
  "tool": "generate_knowledge_summary",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `search_knowledge_base`

**Description:** Search knowledge base for relevant information

**Usage Pattern:**
```json
{
  "tool": "search_knowledge_base",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### Refactoring & Code Quality (3 tools)

#### `cortex_refactor`

**Description:** Execute semantic refactoring operations (extract, rename, organize, etc.) across Python, C#, TypeScript/JavaScript

**Usage Pattern:**
```json
{
  "tool": "cortex_refactor",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_refactor_available_operations`

**Description:** List available refactoring operations for a language or all languages

**Usage Pattern:**
```json
{
  "tool": "cortex_refactor_available_operations",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_refactor_supported_languages`

**Description:** List supported languages and adapter availability status

**Usage Pattern:**
```json
{
  "tool": "cortex_refactor_supported_languages",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

### Utility & System (26 tools)

#### `cortex_check_dependency_drift`

**Description:** Check for dependency drift between requirements.txt and installed packages

**Usage Pattern:**
```json
{
  "tool": "cortex_check_dependency_drift",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_classify_request`

**Description:** Classify user request, display Definition of Ready (DoR), and create approval session

**Usage Pattern:**
```json
{
  "tool": "cortex_classify_request",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_detect_duplicates`

**Description:** Detect CORE-035 duplicate code violations

**Usage Pattern:**
```json
{
  "tool": "cortex_detect_duplicates",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_discover`

**Description:** Unified pre-execution discovery check that prevents duplicate implementations (ENH-047)

**Usage Pattern:**
```json
{
  "tool": "cortex_discover",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_extract_comments`

**Description:** Extract comments, TODOs, FIXMEs, and docstrings from Python files

**Usage Pattern:**
```json
{
  "tool": "cortex_extract_comments",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_generate_landing_page`

**Description:** Generate landing page HTML for dashboard suite

**Usage Pattern:**
```json
{
  "tool": "cortex_generate_landing_page",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_git_history`

**Description:** Analyze git commit history for a file or repository (24h context, blame, patterns)

**Usage Pattern:**
```json
{
  "tool": "cortex_git_history",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_load_audit_checklist`

**Description:** Load audit checklist with P0-P3 checks from YAML registry

**Usage Pattern:**
```json
{
  "tool": "cortex_load_audit_checklist",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_load_core_rules`

**Description:** Load CORE governance rules from YAML registry (CORE-002, CORE-008, etc.)

**Usage Pattern:**
```json
{
  "tool": "cortex_load_core_rules",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_load_modes`

**Description:** Load HEXA-MODE definitions from YAML registry

**Usage Pattern:**
```json
{
  "tool": "cortex_load_modes",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_load_response_format`

**Description:** Load response formatting standards from YAML registry

**Usage Pattern:**
```json
{
  "tool": "cortex_load_response_format",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_modify_request`

**Description:** Modify classified intent and re-generate DoR with corrections

**Usage Pattern:**
```json
{
  "tool": "cortex_modify_request",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_onboard_repository`

**Description:** Onboard repository with holistic LENS analysis + security assessment (P0/P1/P2)

**Usage Pattern:**
```json
{
  "tool": "cortex_onboard_repository",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_onboard_repository_v3`

**Description:** Onboard repository with LENS analysis + LLM business language + SQLite dashboard (Phase 21)

**Usage Pattern:**
```json
{
  "tool": "cortex_onboard_repository_v3",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_tools_catalog`

**Description:** Discover all MCP tools registered in CORTEX

**Usage Pattern:**
```json
{
  "tool": "cortex_tools_catalog",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_vacuum`

**Description:** Clean up markdown sprawl with automated archival and verification

**Usage Pattern:**
```json
{
  "tool": "cortex_vacuum",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_verify_claim`

**Description:** Verify claims about CORTEX implementation against live code

**Usage Pattern:**
```json
{
  "tool": "cortex_verify_claim",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `cortex_verify_environment`

**Description:** Verify CORTEX development environment setup. Checks Python version (3.9+), dependencies, development tools, and MCP server connectivity. Optionally attempts auto-fix for missing packages.

**Usage Pattern:**
```json
{
  "tool": "cortex_verify_environment",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `diagnose_orchestrator_issues`

**Description:** Diagnose issues in orchestrator operation

**Usage Pattern:**
```json
{
  "tool": "diagnose_orchestrator_issues",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `echo_tool`

**Description:** Echo tool for testing MCP connectivity

**Usage Pattern:**
```json
{
  "tool": "echo_tool",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `get_operation_status`

**Description:** Get status of ongoing operation

**Usage Pattern:**
```json
{
  "tool": "get_operation_status",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `get_tdd_guidance_for_module`

**Description:** Get comprehensive TDD guidance for module implementation with tier-based precedence

**Usage Pattern:**
```json
{
  "tool": "get_tdd_guidance_for_module",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `monitor_orchestrator_health`

**Description:** Monitor orchestrator health and metrics

**Usage Pattern:**
```json
{
  "tool": "monitor_orchestrator_health",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `optimize_orchestrator_config`

**Description:** Optimize orchestrator configuration based on metrics

**Usage Pattern:**
```json
{
  "tool": "optimize_orchestrator_config",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `sample_tool`

**Description:** Sample tool demonstrating basic MCP functionality

**Usage Pattern:**
```json
{
  "tool": "sample_tool",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---

#### `transform_tool`

**Description:** Transform data using specified transformation

**Usage Pattern:**
```json
{
  "tool": "transform_tool",
  "arguments": {
    // Tool-specific arguments
  }
}
```

---


## Quick Reference

### Most Used Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| `cortex_process_request` | Primary entry point | All IMPLEMENT/FIX/REFACTOR requests |
| `cortex_lens_analyze` | Deep code intelligence | Security, complexity, architecture analysis |
| `cortex_challenge` | Alternative generation | Design reviews, approach validation |
| `cortex_validate_holistically` | Pre-implementation validation | Phase 48 holistic validation gate |
| `cortex_plan_setup` | Phase initialization | Start new phase with hooks |
| `cortex_debug_full_cycle` | Complete debug workflow | Inject → Capture → Analyze → Fix |

### Tool Naming Convention

All CORTEX MCP tools follow this naming pattern:
- **Prefix:** `cortex_`
- **Domain:** Operation category (e.g., `lens`, `plan`, `debug`)
- **Action:** Verb describing the operation (e.g., `analyze`, `setup`, `validate`)

**Examples:**
- `cortex_lens_analyze` → LENS domain, analyze action
- `cortex_plan_setup` → Plan domain, setup action
- `cortex_debug_capture` → Debug domain, capture action

---

## Integration Examples

### GitHub Copilot Chat

```typescript
// Copilot invokes CORTEX tools automatically via MCP
// Example: User says "Implement login feature"

// Copilot → MCP → CORTEX
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_process_request",
    "arguments": {
      "request": "Implement login feature",
      "enable_challenge": true
    }
  },
  "id": 1
}
```

### Claude Desktop

```json
// .claude/mcp.json configuration
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex.mcp"],
      "env": {
        "CORTEX_MODE": "production"
      }
    }
  }
}
```

### Cursor IDE

```json
// settings.json
{
  "mcp.servers": {
    "cortex": {
      "transport": "stdio",
      "command": ["python", "-m", "cortex.mcp"]
    }
  }
}
```

---

## Development & Testing

### Testing MCP Tools Locally

```bash
# Start MCP server in stdio mode
python -m cortex.mcp

# Test with echo command
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m cortex.mcp
```

### Debugging Tool Execution

```python
from cortex.mcp.server import MCPServer

# Initialize server
server = MCPServer()

# List all tools
tools = server.list_tools()
print(f"Total tools: {len(tools)}")

# Call a specific tool
result = server.call_tool('cortex_lens_analyze', {
    'target': '.',
    'analysis_type': 'security'
})
```

---

**Last Updated:** 2026-02-11 06:35:29  
**Source:** Live MCP Server introspection  
**Accuracy:** 100% current (auto-generated from running system)
