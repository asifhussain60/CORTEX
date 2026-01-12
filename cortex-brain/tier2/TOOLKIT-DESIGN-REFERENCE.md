# CORTEX Toolkit Design Reference (Quick Start)

**Purpose:** Quick reference for toolkit organization, naming, and MCP exposure standards  
**Scope:** All Python tools in `src/tools/` and `src/mcp/`  
**Governance:** CORE-022 (file naming), CORE-024 (@mcp_tool enforcement)  
**Last Updated:** 2026-01-12

---

## 🏗️ Toolkit Architecture

```
CORTEX Toolkit
├── src/tools/                      [Core utility tools]
│   ├── audit-query.py              (MCP-exposed utility)
│   ├── state-manager.py            (MCP-exposed utility)
│   ├── evidence-generator.py       (MCP-exposed utility)
│   └── ... (all kebab-case, ≤25 chars)
│
├── src/mcp/                        [MCP-exposed tools + core]
│   ├── audit-tools.py              (Contains @mcp_tool decorated functions)
│   ├── governance-tools.py         (Contains @mcp_tool decorated functions)
│   ├── planning-tools.py           (Contains @mcp_tool decorated functions)
│   ├── tdd-tools.py                (Contains @mcp_tool decorated functions)
│   ├── todo-tools.py               (Contains @mcp_tool decorated functions)
│   ├── capability-registry.py      (Core: discovers all tools)
│   ├── mcp-decorator.py            (Core: @mcp_tool implementation)
│   └── mcp-server.py               (Core: JSON-RPC server)
│
└── scripts/                        [Operational scripts - refactoring candidates]
    ├── audit-based-validator.py    (Should become MCP tool)
    ├── sync-plan-viewer.py         (Should become MCP tool)
    └── ... (evaluate for toolkit integration)
```

---

## ✅ Naming Standards (CORE-022)

### Requirements

| Aspect | Rule | Example |
|--------|------|---------|
| **Case** | kebab-case (hyphens, lowercase) | `audit-query.py` ✅ |
| **Length** | ≤ 25 characters (excluding `.py`) | `evidence-generator.py` ✅ |
| **Adjectives** | FORBIDDEN - no new/old/enhanced/legacy/temp | ❌ `new-audit-query.py` |
| **Clarity** | Capability-focused, not implementation-focused | `state-manager.py` ✅ |
| **Consistency** | All Python tool files follow same pattern | All tools consistent |

### Valid Examples
```
✅ audit-query.py                   (11 chars, kebab-case, no adjectives)
✅ evidence-generator.py             (19 chars, capability-focused)
✅ state-manager.py                  (13 chars, clear purpose)
✅ governance-merger.py              (16 chars, action-based)
✅ capability-registry.py            (20 chars, design pattern)
```

### Invalid Examples
```
❌ new-audit-query.py               (Adjective "new")
❌ AuditQuery.py                    (PascalCase, not kebab-case)
❌ audit_query.py                   (snake_case, not kebab-case)
❌ enhanced-audit-query.py          (Adjective "enhanced")
❌ temporary-evidence-validator.py  (26+ chars + adjective)
❌ legacy_state_manager.py          (Adjectives + snake_case)
```

---

## 📡 MCP Exposure Standards (CORE-024)

### Requirement
**ALL public-facing tools MUST be decorated with `@mcp_tool`**

### Decorator Pattern
```python
from src.mcp.mcp_decorator import mcp_tool

@mcp_tool(
    name="cortex_audit_query",
    description="Query audit logs with filters",
    category="audit",
    parameters={
        "db_path": {
            "type": "string",
            "required": True,
            "description": "Path to audit database"
        },
        "filters": {
            "type": "object",
            "required": False,
            "description": "Query filters (optional)"
        }
    },
    returns={
        "type": "object",
        "description": "Query results with matching entries"
    },
    metadata={
        "tags": ["audit", "query", "logging"],
        "version": "1.0",
        "autonomous": True,
        "ac_standard": "AC-AUDIT-001"  # Link to governance AC-ID
    }
)
def audit_query(db_path: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Query audit logs with optional filters.
    
    Args:
        db_path: Path to the audit database file
        filters: Optional dict with keys: ac_id, start_date, end_date, level
        
    Returns:
        Dict with keys: status, data (list of log entries), error
        
    Example:
        result = audit_query(
            "/path/to/audit.db",
            filters={"ac_id": "AC-AUDIT-001", "level": "ERROR"}
        )
    """
    # Implementation here
    pass
```

### Metadata Fields (Required)
| Field | Type | Purpose |
|-------|------|---------|
| `tags` | list | Search/filter categories |
| `version` | string | Tool version |
| `autonomous` | bool | Can run without user input |
| `ac_standard` | string | Link to governance AC-ID (if applicable) |

### Tool Categories
- `audit` - Audit logging and querying
- `governance` - Governance rules and merging
- `planning` - Plan creation and management
- `development` - Development workflows (TDD, etc.)
- `testing` - Test execution and validation
- `maintenance` - Cleanup, vacuum, optimization
- `integration` - External integrations (ADO, etc.)
- `general` - Uncategorized utilities

---

## 🔍 Tool Discovery & Registry

### How Tools Are Discovered

1. **Manual import in capability_registry.py:**
   ```python
   tool_modules = [
       'src.mcp.audit_tools',
       'src.mcp.governance_tools',
       'src.mcp.planning_tools',
       # ... etc
   ]
   ```

2. **Decorator auto-registration:**
   - When module is imported, @mcp_tool decorator registers tool
   - Tools collected in global `_DECORATED_TOOLS` list

3. **Registry construction:**
   - CapabilityRegistry discovers all decorated tools
   - Converts to Capability objects
   - Stored in `_global_registry` (singleton)

### MasterOrchestrator Access
```python
from src.mcp.capability_registry import get_capability_registry

registry = get_capability_registry()
audit_tool = registry.get("cortex_audit_query")  # MasterOrchestrator can find it
```

---

## 🧪 Testing Requirements

### Test File Naming
- Tool file: `src/mcp/audit-tools.py`
- Test file: `tests/mcp/test-audit-tools.py`

### Test Coverage Areas
1. **Happy path** - Normal operation with valid inputs
2. **Error handling** - Invalid inputs, missing parameters
3. **Parameter validation** - Type checking, required fields
4. **MCP exposure** - Verify decorator metadata
5. **Integration** - Tool works with capability_registry

### Example Test Structure
```python
# tests/mcp/test-audit-tools.py
import pytest
from src.mcp.audit_tools import audit_query
from src.mcp.capability_registry import get_capability_registry

def test_audit_query_happy_path():
    """Test normal audit query operation."""
    result = audit_query("/path/to/audit.db", filters={"level": "ERROR"})
    assert result["status"] == "success"
    assert isinstance(result["data"], list)

def test_audit_query_invalid_db():
    """Test error handling for invalid database path."""
    result = audit_query("/nonexistent/db.db")
    assert result["status"] == "error"
    assert "not found" in result["error"].lower()

def test_mcp_decorator_applied():
    """Verify @mcp_tool decorator is properly applied."""
    registry = get_capability_registry()
    cap = registry.get("cortex_audit_query")
    assert cap is not None
    assert cap.metadata["category"] == "audit"
    assert cap.metadata["ac_standard"] == "AC-AUDIT-001"
```

---

## 🔧 Tool Consolidation Guidelines

### When to Consolidate
- Multiple tools with overlapping functionality
- Related tools that serve the same domain (e.g., all audit tools)
- Tools with <20% usage in codebase
- Tools that share 70%+ of implementation

### Consolidation Process
1. **Preserve all unique capabilities** - No feature loss
2. **Merge into domain module** - `audit-query.py` + `audit-logger.py` → `audit-tools.py`
3. **Update imports** - All references point to new location
4. **Update @mcp_tool decorators** - Ensure all functions still exposed
5. **Verify tests** - All test scenarios still passing
6. **Update registry** - Re-run capability discovery

### Consolidation Example
```yaml
# CONSOLIDATION PLAN
Before:
  - src/tools/audit-query.py               (single function tool)
  - src/tools/audit-history.py             (overlapping functionality)
  - src/tools/audit-logger.py              (domain-related)

After:
  - src/mcp/audit-tools.py                 (unified module)
    ├── @mcp_tool: audit_query()
    ├── @mcp_tool: audit_history()
    ├── @mcp_tool: audit_logger()
    └── Internal: _validate_filters()

Benefits:
  ✅ Single source of truth for audit tools
  ✅ Reduced import complexity
  ✅ Easier testing and maintenance
  ✅ Clearer MPC discovery (one module vs three)
```

---

## 📊 Toolkit Health Scorecard

### Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Tool inventory complete | ~50% | 100% | 🔴 In Progress |
| MCP exposure (@mcp_tool) | ~40% | 100% | 🔴 In Progress |
| Naming compliance (kebab-case, ≤25 chars) | 50% | 100% | 🟡 Partial |
| Naming: No adjectives | 60% | 100% | 🟡 Partial |
| Test coverage (tests for all tools) | 60% | 90% | 🟡 Partial |
| Tool consolidation complete | 0% | 100% | 🔴 Not Started |
| Registry discovery blind spots | 10% | 0% | 🟡 Minor |
| Documentation complete | 70% | 100% | 🟡 Partial |

### Health Score Formula
```
Health = (MCP_Coverage + Naming_Compliance + Test_Coverage + Consolidation_Complete) / 4

Target: ≥ 90% health score
Current: ~50% health score (estimated)
```

---

## 🚀 Implementation Roadmap

### Phase 1: Audit (1-2 days)
- [ ] Inventory all tools in src/tools/ and src/mcp/
- [ ] Classify: MCP-exposed, internal, consolidation, removal
- [ ] Identify naming violations
- [ ] Generate toolkit health report

### Phase 2: Consolidation & Naming (3-5 days)
- [ ] Merge duplicate tools (preserve capabilities)
- [ ] Rename files to kebab-case (≤25 chars, no adjectives)
- [ ] Update all imports/references
- [ ] Add @mcp_tool decorators to public tools
- [ ] Verify capability_registry re-discovers all tools

### Phase 3: Organization (2-3 days)
- [ ] Reorganize by responsibility
- [ ] Split oversized tools (>500 lines)
- [ ] Define consistent tool categories
- [ ] Update module docstrings

### Phase 4: Testing & Validation (3-5 days)
- [ ] Add/update test files for all MCP tools
- [ ] Validate input parameter checking
- [ ] Implement consistent error handling
- [ ] Verify CORE-024 compliance
- [ ] Create tool catalog document

**Total Effort:** 10-15 days  
**Risk:** Low-Medium (no architectural changes)  
**Impact:** High (complete toolkit coherence)

---

## 📖 Reference Documents

| Document | Purpose |
|----------|---------|
| `cortex-brittleness-review.prompt.md` | Full brittleness + toolkit review |
| `TOOLKIT-ALIGNMENT-ENHANCEMENT.md` | Enhancement details (this repo) |
| `core-rules.yaml` | CORE-022 and CORE-024 rules |
| `capability_registry.py` | Tool discovery implementation |
| `mcp_decorator.py` | @mcp_tool decorator code |
| `AC-INDEX.yaml` | Governance AC-IDs for toolkit work |

---

## ❓ FAQ

**Q: Can internal utilities skip the @mcp_tool decorator?**  
A: Yes, but they must be clearly marked as internal in module docstring. They should not be called directly by MasterOrchestrator.

**Q: What if a tool name is >25 chars and we can't shorten it?**  
A: Consolidate with related tools or split functionality. Example: `validate-prompt-integrity-checks.py` → `prompt-validator.py` (consolidate) or `validate-prompts.py` + `validate-integrity.py` (split).

**Q: Should all tools be in src/mcp/ or some in src/tools/?**  
A: Tools in src/mcp/ should be @mcp_tool decorated (MCP-exposed). Tools in src/tools/ can be utilities or candidates for consolidation into MCP modules.

**Q: How does consolidation affect existing orchestrators that use these tools?**  
A: Consolidation updates tool function names and locations. MasterOrchestrator accesses tools via capability_registry (name-based lookup), not direct imports, so it's resilient to consolidation.

**Q: What's the difference between "tool" and "orchestrator"?**  
A: **Tools** are focused, single-capability functions exposed via @mcp_tool. **Orchestrators** are workflow managers that coordinate multiple tools to achieve complex outcomes.

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-12  
**Maintenance Owner:** CORTEX Governance Team
