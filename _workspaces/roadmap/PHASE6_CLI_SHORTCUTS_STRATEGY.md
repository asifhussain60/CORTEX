# Phase 6: CLI Shortcuts & Developer Experience

## Overview
Create 5 critical CLI shortcuts to surface CORTEX capabilities to developers.

## CLI Shortcuts

### 1. `/test {module}` - Run Test Suite
**Purpose:** Quick test execution with results
```bash
Usage: /test orchestrators
       /test mcp
       /test governance
       /test all

Implementation:
- Parses test module name
- Calls pytest programmatically
- Returns: pass/fail count, coverage, time
- Entry point: CLIOrchestrator → TDDOrchestrator
```

### 2. `/doc {feature}` - Generate Documentation
**Purpose:** Auto-generate docs for feature
```bash
Usage: /doc orchestrators
       /doc mcp_tools
       /doc governance
       /doc workflows

Implementation:
- Discovers feature components
- Generates markdown docs
- Includes examples and usage
- Entry point: CLIOrchestrator → DocumentationOrchestrator
```

### 3. `/refactor {target}` - Refactoring Workflow
**Purpose:** Interactive refactoring with TDD
```bash
Usage: /refactor extract_function src/file.py:100-150
       /refactor rename_class OldName NewName
       /refactor organize_imports cortex/

Implementation:
- Analyzes target code
- Suggests improvements
- Generates tests first (TDD)
- Executes refactoring
- Entry point: CLIOrchestrator → RefactoringOrchestrator
```

### 4. `/status` - System Status Report
**Purpose:** Health check and capability discovery
```bash
Usage: /status
       /status verbose
       /status json

Output:
- Orchestrators wired: 23/23 ✓
- MCP tools available: 15
- Tests passing: 7169/7547 (95%)
- Governance: 29/29 CORE rules satisfied ✓
- All systems operational ✓

Implementation:
- Queries MasterOrchestrator
- Calls get_wiring_registry()
- Calls get_mcp_tools()
- Runs governance validation
- Entry point: CLIOrchestrator → MasterOrchestrator
```

### 5. `/recall {feature}` - Feature Discovery
**Purpose:** Find implementation details for any feature
```bash
Usage: /recall orchestrators
       /recall mcp_tools
       /recall governance_rules
       /recall best_practices

Output:
- Lists all matching features
- Shows: entry point, type, dependencies, examples
- Links to documentation
- Links to tests

Implementation:
- Uses TotalRecallAgent for feature discovery
- Queries knowledge repository (35+ YAML files)
- Returns: feature metadata, usage examples, related docs
- Entry point: CLIOrchestrator → TotalRecallAgent
```

## Implementation Timeline

| Task | Duration | Priority |
|------|----------|----------|
| CLI scaffold (argparse/click) | 30m | HIGH |
| `/test` implementation | 20m | HIGH |
| `/status` implementation | 20m | HIGH |
| `/recall` implementation | 30m | MEDIUM |
| `/doc` implementation | 20m | MEDIUM |
| `/refactor` integration | 20m | MEDIUM |
| Testing & validation | 40m | HIGH |

**Total: ~3 hours**

## File Structure

```
cortex/cli/
├── orchestrator.py       (NEW - CLIOrchestrator)
├── commands/
│   ├── test.py           (NEW - TestCommand)
│   ├── status.py         (NEW - StatusCommand)
│   ├── recall.py         (NEW - RecallCommand)
│   ├── doc.py            (NEW - DocCommand)
│   └── refactor.py       (NEW - RefactorCommand)
└── formatter.py          (UPDATED - output formatting)

cortex/tools/
└── total_recall_agent.py (EXISTING - feature discovery)
```

## Success Criteria

✅ All 5 commands implemented and wired to orchestrators
✅ Each command has comprehensive help (`--help`)
✅ All commands tested with unit tests
✅ Integration tests verify end-to-end workflow
✅ Error handling: graceful fallback and helpful messages
✅ Documentation: usage examples in `/docs/CLI-SHORTCUTS.md`

---

**Next Steps:** After Phase 6, proceed to Phase 7 (documentation & rollout)
