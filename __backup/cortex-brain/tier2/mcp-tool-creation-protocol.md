# MCP Tool Creation Protocol

**Version:** 1.0.0 | **Created:** 2026-01-10 | **SKULL Rule:** CORE-024  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

This protocol ensures **100% MCP exposure** for all CORTEX tools through decorator-based auto-registration. It prevents registration drift where tools exist but aren't discoverable via Model Context Protocol.

---

## 🛡️ Enforcement: CORE-024 SKULL Rule

**Rule:** All functions in `src/mcp/*_tools.py` MUST use `@mcp_tool` decorator.

**Enforcement:**
- ✅ **Pre-commit hook** - Blocks commits with undecorated tools
- ✅ **AST static analysis** - Scans code before merge
- ✅ **Runtime validation** - Capability registry checks on startup
- ✅ **Audit trail** - Logs decorator metadata for compliance

**Bypass:** Emergency only (`git commit --no-verify`) - Creates audit alert

---

## 📋 4-Step Tool Creation Process

### **Step 1: Choose Tool Category**

Create tool file in appropriate category:

```
src/mcp/
  ├── audit_tools.py        # Audit logging, query, export
  ├── governance_tools.py   # Governance validation, rule checks
  ├── planning_tools.py     # Plan creation, execution, validation
  ├── tdd_tools.py          # TDD execution, phase management
  ├── todo_tools.py         # Task management, DAG operations
  ├── traceability_tools.py # AC-ID tracking, coverage, gaps
  └── housekeeping_tools.py # Cleanup, vacuum, health checks
```

**New category?** Create `{category}_tools.py` and add to `capability_registry.py` import list.

---

### **Step 2: Import Decorator**

```python
from src.mcp.mcp_decorator import mcp_tool
```

---

### **Step 3: Decorate Function**

```python
@mcp_tool(
    name="cortex_your_tool_name",           # Required: Unique tool name
    description="Clear description",         # Required: What tool does
    category="audit",                        # Required: Category for grouping
    orchestrator_id="audit_orchestrator",   # Optional: Associated orchestrator
    parameters={                             # Required: Input parameters
        "param1": {
            "type": "string",                # string|integer|boolean|object|array
            "required": True,
            "description": "Parameter description"
        },
        "param2": {
            "type": "integer",
            "required": False,
            "description": "Optional parameter"
        }
    },
    returns={                                # Required: Output schema
        "type": "object",
        "description": "Return value description"
    },
    metadata={                               # Optional: Additional metadata
        "tags": ["audit", "logging"],
        "version": "1.0",
        "priority": "P0"
    }
)
def your_tool_function(param1: str, param2: int = 0):
    """
    Docstring - will be used if description not in decorator.
    """
    # Implementation
    return {"success": True, "data": ...}
```

---

### **Step 4: Verify Registration**

```bash
# Check decorator validation passes
python3 -m src.tools.validators.mcp_decorator_validator

# Verify tool exposed via MCP
python3 -c "
from src.mcp.capability_registry import get_capability_registry
registry = get_capability_registry()
tool = registry.get('cortex_your_tool_name')
print(f'Tool registered: {tool is not None}')
"
```

---

## 📖 Complete Example: Audit Query Tool

```python
"""
CORTEX 6.0 - Audit Tools
"""

from pathlib import Path
from typing import Dict, Any, Optional
from src.mcp.mcp_decorator import mcp_tool
from src.infrastructure.enhanced_audit_logger import AuditStorage


@mcp_tool(
    name="cortex_audit_query",
    description="Query CORTEX audit logs with filters (ac_id, component, level, category, time range)",
    category="audit",
    orchestrator_id="audit_orchestrator",
    parameters={
        "db_path": {
            "type": "string",
            "required": True,
            "description": "Path to audit database (governance.db)"
        },
        "filters": {
            "type": "object",
            "required": False,
            "description": "Query filters: ac_id, component, level (INFO/WARNING/ERROR), category, start_time, end_time"
        }
    },
    returns={
        "type": "object",
        "description": "Query result with success, entries list, and count"
    },
    metadata={
        "tags": ["audit", "logging", "debugging", "traceability"],
        "version": "1.0",
        "priority": "P0"
    }
)
def audit_query(db_path: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Query audit logs via MCP with filters.
    
    Args:
        db_path: Path to audit database
        filters: Query filters (ac_id, component, level, etc.)
    
    Returns:
        Query result with success status and entries
    """
    try:
        storage = AuditStorage(Path(db_path))
        filters = filters or {}
        
        entries = storage.query(**filters)
        
        return {
            "success": True,
            "entries": entries,
            "count": len(entries)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "entries": []
        }
```

---

## 🚫 Common Mistakes (BLOCKED by CORE-024)

### ❌ **Wrong: Manual Registration**
```python
def my_tool():
    pass

# Manual registry call - FORBIDDEN
registry.register(Capability(name="my_tool", ...))
```

**Why blocked:** Registration drift risk - easy to forget manual call.

---

### ❌ **Wrong: Missing Decorator**
```python
def my_tool():
    pass  # Will NOT be exposed via MCP
```

**Why blocked:** Tool exists but not discoverable - silent failure.

---

### ❌ **Wrong: Incomplete Metadata**
```python
@mcp_tool(name="my_tool")  # Missing: description, parameters, returns
def my_tool():
    pass
```

**Why blocked:** Insufficient metadata for MCP clients to use tool correctly.

---

## 🎯 Parameter Type Reference

| JSON Schema Type | Python Type | Example | Description |
|-----------------|-------------|---------|-------------|
| `string` | `str` | `"path/to/file"` | Text values |
| `integer` | `int` | `42` | Whole numbers |
| `number` | `float` | `3.14` | Decimals |
| `boolean` | `bool` | `true` | True/False |
| `object` | `dict` | `{"key": "value"}` | Nested structures |
| `array` | `list` | `["a", "b", "c"]` | Lists |

---

## 🔄 Multi-Layer Defense Strategy

| Layer | Mechanism | Prevention | Detection | Scope |
|-------|-----------|------------|-----------|-------|
| **1. SKULL Rule** | Pre-commit hook | ✅ Commit-time | ✅ Static | CORTEX repo |
| **2. Scaffolder** | Template generator | ✅ Build-time | N/A | CORTEX repo |
| **3. Plugin** | Portable package | ✅ Import-time | ✅ Runtime | User repos |
| **4. Docs** | Developer guidance | ⚠️ Awareness | ❌ None | All repos |

---

## 🔌 Cross-Repo Support (Phase 3 Roadmap)

**Coming:** `cortex-mcp-protocol` PyPI package for user repos.

**User repo usage:**
```python
# Install protocol package
pip install cortex-mcp-protocol

# Use same decorator
from cortex_mcp_protocol import mcp_tool

@mcp_tool(name="my_custom_tool", ...)
def my_tool():
    pass
```

**CORTEX discovery:**
- Scans `sys.modules` for `cortex_mcp_protocol` presence
- Imports user's decorated tools via `get_decorated_tools()`
- Merges into CORTEX capability registry seamlessly

---

## 🧪 Testing Your Tool

```python
# Test decorator metadata
from src.mcp.mcp_decorator import get_decorated_tools

tools = get_decorated_tools()
tool = next((t for t in tools if t['name'] == 'cortex_your_tool_name'), None)

assert tool is not None, "Tool not registered"
assert 'description' in tool, "Missing description"
assert 'parameters' in tool, "Missing parameters"
```

---

## 📊 Benefits vs. Manual Registration

| Aspect | Manual Registration | @mcp_tool Decorator |
|--------|-------------------|---------------------|
| **Registration** | Call registry.register() | Automatic at import |
| **Drift Risk** | High (easy to forget) | Zero (enforced by CORE-024) |
| **Consistency** | Varies by developer | Template-enforced |
| **Validation** | Runtime only | Commit-time + Runtime |
| **Cross-Repo** | Not portable | Plugin-based (Phase 3) |
| **Audit Trail** | Manual logging | Automatic metadata |

---

## 🚀 Tool Scaffolder (Phase 2 - AC-MCP-PROTOCOL-002)

**Coming:** Auto-generate decorated tool stubs.

```bash
python3 -m src.tools.create_mcp_tool \
  --name my_tool \
  --category audit \
  --description "Query something" \
  --parameters '{"param1": {"type": "string", "required": true}}'
```

**Generates:**
```python
# Auto-generated by CORTEX Tool Scaffolder
# DO NOT REMOVE @mcp_tool DECORATOR

from src.mcp.mcp_decorator import mcp_tool

@mcp_tool(
    name="cortex_my_tool",
    description="Query something",
    category="audit",
    parameters={"param1": {"type": "string", "required": True}},
    returns={"type": "object", "description": "Result"}
)
def my_tool(param1: str):
    # TODO: Implement
    pass
```

---

## ⚠️ Emergency Bypass (Use Sparingly)

If you MUST commit without decorator (emergency fix):

```bash
git commit --no-verify -m "EMERGENCY: Bypass CORE-024 - Reason: [explain]"
```

**Consequences:**
- ⚠️ Creates audit alert
- ⚠️ Flagged in governance reports
- ⚠️ Requires remediation within 24 hours
- ⚠️ Tool NOT exposed via MCP until decorated

---

## 📚 Related Documentation

- **SKULL Rule:** `cortex-brain/tier0/governance/core-rules.yaml` (CORE-024)
- **Decorator Implementation:** `src/mcp/mcp_decorator.py`
- **Validator:** `src/tools/validators/mcp_decorator_validator.py`
- **Pre-commit Hook:** `scripts/pre-commit` (MCP section)
- **Capability Registry:** `src/mcp/capability_registry.py`

---

## 🎯 Quick Reference Checklist

Before committing new MCP tool:

- [ ] Tool file in `src/mcp/*_tools.py`
- [ ] Imported `@mcp_tool` decorator
- [ ] Decorated function with full metadata
- [ ] Parameter types defined (JSON Schema)
- [ ] Returns schema specified
- [ ] Validator passes (`python3 -m src.tools.validators.mcp_decorator_validator`)
- [ ] Tool listed in capability registry
- [ ] Pre-commit hook passes

---

**Version History:**
- 1.0.0 (2026-01-10): Initial protocol documentation (CORE-024 enforcement)
