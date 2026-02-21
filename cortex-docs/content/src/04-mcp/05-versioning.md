# MCP Versioning & Evolution

---
title: MCP Versioning & Lifecycle
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex/mcp/ + cortex-registry/planning/cortex-refactor-master.yaml
order: 5
---

> **Brain analogy:** Versioning is **neuroplasticity** — the brain's ability to reorganize itself over time. New reflexes are added, old ones refined, but the spinal cord (transport) stays the same. A baby's reflexes evolve into adult motor skills without replacing the nervous system.

---

## Current Version

| Property | Value |
|----------|-------|
| MCP Version | v2 |
| Protocol | JSON-RPC 2.0 |
| Transport | stdio |
| Canonical Tools | 23 |
| Tool Files | 37 Python files |
| Tool Base Class | `ConsolidatedTool` |

---

## Version History

### v1 → v2 Migration (Phase 03)

The 12-phase Cohesive Brain Refactor consolidated tools:

| Aspect | v1 | v2 |
|--------|----|----|
| Package | `cortex_intelligence`, `cortex_lens` (separate) | `cortex` (single canonical) |
| Tool registration | Scattered across modules | `ConsolidatedTool` base class |
| Transport | Mixed (HTTP + stdio) | stdio only |
| Governance | Optional validation | Mandatory governance gates |
| Entry point | Any tool directly | `cortex_process_request` mandatory |

### Phase 12 Consolidation (Planned)

Phase 12 of the Cohesive Brain Refactor targets consolidation of tool files:

- **Current:** 37 Python files across `tools/`, `deployment/`, `multi_repo/`, `toolkit/`
- **Target:** Consolidate to 23 canonical files (one per tool)
- **Approach:** Merge specialized modules into their parent tools

---

## Tool Naming Convention

All canonical MCP tools follow the pattern:

```
cortex_{domain}_{action}
```

| Pattern | Examples |
|---------|----------|
| `cortex_{action}` | `cortex_verify`, `cortex_ask`, `cortex_vacuum` |
| `cortex_{domain}` | `cortex_governance`, `cortex_lens`, `cortex_workflow` |
| `cortex_{domain}_{action}` | `cortex_process_request`, `cortex_validate_request`, `cortex_tools_catalog` |

### Registration Rules

1. Every tool **must** inherit from `ConsolidatedTool`
2. Tool name **must** start with `cortex_`
3. Tool name **must** be unique across all modules
4. Tool **must** define `name`, `description`, `category`, `parameters`, `execute`
5. Tool **must** record audit trail entries on execution

---

## Adding New Tools

### Step 1: Create Tool Class

```python
# cortex/mcp/tools/my_new_tool.py
from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolCategory, ToolParameter, ToolResult

class CortexMyNewTool(ConsolidatedTool):
    @property
    def name(self) -> str:
        return "cortex_my_new_tool"
    
    @property
    def description(self) -> str:
        return "Description of what this tool does."
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.UTILITY
    
    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="input",
                type="string",
                description="Input parameter",
                required=True,
            ),
        ]
    
    async def execute(self, args: dict) -> ToolResult:
        # Implementation
        return ToolResult(content="Result")
```

### Step 2: Register in `__init__.py`

```python
# cortex/mcp/tools/__init__.py
from cortex.mcp.tools.my_new_tool import CortexMyNewTool
```

### Step 3: Write Tests First (CORE-008)

```python
# tests/mcp/test_my_new_tool.py
def test_my_new_tool_name():
    tool = CortexMyNewTool()
    assert tool.name == "cortex_my_new_tool"

def test_my_new_tool_execution():
    tool = CortexMyNewTool()
    result = await tool.execute({"input": "test"})
    assert result.content is not None
```

---

## Deprecation Policy

1. **Announce:** Mark tool with `@deprecated` decorator, add warning to description
2. **Grace period:** Tool continues to work for 2 phases (approximately 4 weeks)
3. **Remove:** Delete tool class, update `__init__.py`, remove from catalog
4. **Audit:** Log all deprecated tool calls with migration guidance

---

## Practical Examples

**Product Owner:** "When we add a new capability, it becomes a new MCP tool. The naming convention makes tools discoverable — `cortex_` prefix, domain name, then action."

**Developer:** "Adding a tool follows TDD. I write the test first (CORE-008), create the `ConsolidatedTool` subclass, register it in `__init__.py`, and it's immediately available in Copilot Chat."

---

*Verified against MCP tool base class and registration patterns · 20 February 2026*
