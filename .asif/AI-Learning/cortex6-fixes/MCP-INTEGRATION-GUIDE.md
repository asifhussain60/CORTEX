# 🔌 MCP Integration Guide - Remediation Tools

**Date:** 2026-01-08  
**Purpose:** Expose CORTEX Remediation Tools as MCP capabilities for cross-repo usage

---

## ✅ Yes! These Tools Are MCP-Ready

The remediation tools created in Phase P0 are **designed to integrate with the CORTEX MCP server**, enabling them to be used across **all repositories** where CORTEX is available.

---

## 🏗️ Current Architecture

### Local Tools (Current State)

```
src/tools/
├── yaml_validator.py        # Standalone CLI tool
├── gap_detector.py          # Standalone CLI tool
├── md_to_yaml_converter.py  # Standalone CLI tool
├── dashboard_generator.py   # Standalone CLI tool
├── checkpoint_manager.py    # Standalone CLI tool
├── requirements_auditor.py  # Standalone CLI tool
└── remediation_executor.py  # Standalone CLI tool
```

**Usage:** Direct Python invocation
```bash
python3 -m src.tools.yaml_validator file.yaml
python3 -m src.tools.gap_detector
python3 -m src.tools.dashboard_generator
```

### MCP-Exposed Tools (Target State)

```
MCP Client (VS Code, Claude Desktop, etc.)
    ↓
MCP Protocol (tools/list, tools/call)
    ↓
CORTEX MCP Server (src/mcp/mcp_server.py)
    ↓
Capability Registry (src/mcp/capability_registry.py)
    ↓
Tool Wrappers → src/tools/*.py
```

**Usage:** Through any MCP client
```json
{
  "method": "tools/call",
  "params": {
    "name": "cortex_validate_yaml",
    "arguments": {
      "file_path": "feature.yaml",
      "schema_type": "feature"
    }
  }
}
```

---

## 🔧 Integration Steps

### Step 1: Create MCP Tool Wrappers

Each tool needs an MCP-compatible wrapper in the capability registry:

```python
# src/mcp/tools/remediation_tools.py

from src.mcp.capability_registry import Capability, ParameterSchema
from src.tools.yaml_validator import YAMLValidator
from src.tools.gap_detector import GapDetector
from src.tools.dashboard_generator import DashboardGenerator
from src.tools.checkpoint_manager import CheckpointManager

def register_remediation_tools(registry):
    """Register all remediation tools as MCP capabilities."""
    
    # 1. YAML Validator Tool
    registry.register(Capability(
        name="cortex_validate_yaml",
        description="Validate YAML files against CORTEX schemas",
        category="validation",
        orchestrator_id="yaml_validator",
        parameters={
            "file_path": ParameterSchema(
                type="string",
                description="Path to YAML file to validate",
                required=True
            ),
            "schema_type": ParameterSchema(
                type="string",
                description="Schema type: 'feature' or 'requirements'",
                required=False,
                enum=["feature", "requirements"]
            )
        },
        handler=lambda args: _validate_yaml_handler(args)
    ))
    
    # 2. Gap Detector Tool
    registry.register(Capability(
        name="cortex_detect_gaps",
        description="Analyze implementation gaps between requirements and code",
        category="analysis",
        orchestrator_id="gap_detector",
        parameters={
            "workspace_root": ParameterSchema(
                type="string",
                description="Root directory of project to analyze",
                required=True
            ),
            "output_format": ParameterSchema(
                type="string",
                description="Output format: 'yaml', 'json', or 'markdown'",
                required=False,
                enum=["yaml", "json", "markdown"],
                default="yaml"
            )
        },
        handler=lambda args: _detect_gaps_handler(args)
    ))
    
    # 3. Dashboard Generator Tool
    registry.register(Capability(
        name="cortex_generate_dashboard",
        description="Generate progress dashboard for remediation plan",
        category="reporting",
        orchestrator_id="dashboard_generator",
        parameters={
            "plan_dir": ParameterSchema(
                type="string",
                description="Directory containing plan YAML files",
                required=False
            ),
            "format": ParameterSchema(
                type="string",
                description="Output format: 'ascii', 'yaml', 'html', 'json'",
                required=False,
                enum=["ascii", "yaml", "html", "json"],
                default="ascii"
            )
        },
        handler=lambda args: _generate_dashboard_handler(args)
    ))
    
    # 4. Checkpoint Manager Tool
    registry.register(Capability(
        name="cortex_checkpoint",
        description="Create, list, or restore git checkpoints",
        category="version_control",
        orchestrator_id="checkpoint_manager",
        parameters={
            "action": ParameterSchema(
                type="string",
                description="Action: 'create', 'list', 'restore', 'validate'",
                required=True,
                enum=["create", "list", "restore", "validate"]
            ),
            "checkpoint_id": ParameterSchema(
                type="string",
                description="Checkpoint ID (required for create/restore/validate)",
                required=False
            ),
            "name": ParameterSchema(
                type="string",
                description="Checkpoint name (required for create)",
                required=False
            ),
            "description": ParameterSchema(
                type="string",
                description="Checkpoint description (optional for create)",
                required=False
            )
        },
        handler=lambda args: _checkpoint_handler(args)
    ))
    
    # 5. MD to YAML Converter Tool
    registry.register(Capability(
        name="cortex_convert_md_to_yaml",
        description="Convert markdown requirements to YAML format",
        category="conversion",
        orchestrator_id="md_to_yaml_converter",
        parameters={
            "input_path": ParameterSchema(
                type="string",
                description="Path to markdown file or directory",
                required=True
            ),
            "output_path": ParameterSchema(
                type="string",
                description="Path for output YAML file or directory",
                required=True
            ),
            "validate": ParameterSchema(
                type="boolean",
                description="Validate output against schema",
                required=False,
                default=True
            )
        },
        handler=lambda args: _convert_md_to_yaml_handler(args)
    ))
    
    # 6. Requirements Auditor Tool
    registry.register(Capability(
        name="cortex_audit_requirements",
        description="Audit all requirements files in a project",
        category="analysis",
        orchestrator_id="requirements_auditor",
        parameters={
            "project_root": ParameterSchema(
                type="string",
                description="Root directory of project to audit",
                required=True
            ),
            "output_format": ParameterSchema(
                type="string",
                description="Output format: 'yaml', 'json', 'markdown'",
                required=False,
                enum=["yaml", "json", "markdown"],
                default="yaml"
            )
        },
        handler=lambda args: _audit_requirements_handler(args)
    ))


# Handler implementations
def _validate_yaml_handler(args):
    """Handle YAML validation requests."""
    validator = YAMLValidator()
    result = validator.validate_file(args['file_path'], args.get('schema_type'))
    return {
        "is_valid": result.is_valid,
        "errors": [str(e) for e in result.errors],
        "summary": result.format_errors()
    }

def _detect_gaps_handler(args):
    """Handle gap detection requests."""
    detector = GapDetector(args['workspace_root'])
    report = detector.analyze()
    return {
        "total_gaps": len(report['gaps']),
        "critical": sum(1 for g in report['gaps'] if g['severity'] == 'CRITICAL'),
        "high": sum(1 for g in report['gaps'] if g['severity'] == 'HIGH'),
        "summary": report['summary']
    }

def _generate_dashboard_handler(args):
    """Handle dashboard generation requests."""
    generator = DashboardGenerator(args.get('plan_dir'))
    format = args.get('format', 'ascii')
    
    if format == 'ascii':
        return {"dashboard": generator.generate_ascii_progress_bars()}
    elif format == 'yaml':
        return generator.generate_yaml_dashboard()
    elif format == 'html':
        return {"html": generator.generate_html_dashboard()}
    else:
        return generator.generate_yaml_dashboard()

def _checkpoint_handler(args):
    """Handle checkpoint management requests."""
    manager = CheckpointManager()
    action = args['action']
    
    if action == 'create':
        cp = manager.create_checkpoint(
            args['checkpoint_id'],
            args['name'],
            args.get('description', '')
        )
        return {"checkpoint_id": cp.id, "commit": cp.git_commit}
    elif action == 'list':
        checkpoints = manager.list_checkpoints()
        return {"checkpoints": [cp.to_dict() for cp in checkpoints]}
    elif action == 'restore':
        manager.restore_checkpoint(args['checkpoint_id'])
        return {"status": "restored", "checkpoint_id": args['checkpoint_id']}
    elif action == 'validate':
        is_valid = manager.validate_checkpoint(args['checkpoint_id'])
        return {"is_valid": is_valid, "checkpoint_id": args['checkpoint_id']}
```

### Step 2: Register at Startup

Update `src/mcp/mcp_server.py` to auto-register remediation tools:

```python
# In src/mcp/mcp_server.py

from src.mcp.tools.remediation_tools import register_remediation_tools

class MCPServer:
    def __init__(self, ...):
        # ... existing initialization ...
        
        # Auto-register remediation tools
        register_remediation_tools(self.capability_registry)
        
        logger.info("MCPServer initialized with remediation tools")
```

### Step 3: Add to MCP Server Configuration

Update `cortex-brain/config/mcp-server.yaml`:

```yaml
server:
  name: "CORTEX MCP Server"
  version: "6.0.0"
  description: "Model Context Protocol server for CORTEX orchestrators and tools"
  
capabilities:
  # ... existing capabilities ...
  
  # Remediation Tools (Phase P0)
  - name: cortex_validate_yaml
    enabled: true
    category: validation
    
  - name: cortex_detect_gaps
    enabled: true
    category: analysis
    
  - name: cortex_generate_dashboard
    enabled: true
    category: reporting
    
  - name: cortex_checkpoint
    enabled: true
    category: version_control
    
  - name: cortex_convert_md_to_yaml
    enabled: true
    category: conversion
    
  - name: cortex_audit_requirements
    enabled: true
    category: analysis
```

---

## 🌍 Cross-Repository Usage

Once integrated into MCP, these tools become **universally available**:

### Scenario 1: User Working in ANY Repository

**Context:** User is in their own project, not CORTEX

**MCP Client (VS Code/Claude):**
```
User: "Analyze my project for implementation gaps"

Claude: [Uses cortex_detect_gaps tool]
{
  "name": "cortex_detect_gaps",
  "arguments": {
    "workspace_root": "/path/to/user/project"
  }
}

Response: {
  "total_gaps": 15,
  "critical": 3,
  "high": 8,
  "summary": "Found 15 gaps in implementation..."
}
```

### Scenario 2: Requirements Conversion Across Projects

**Any repo with markdown requirements:**
```
User: "Convert my markdown requirements to YAML"

Claude: [Uses cortex_convert_md_to_yaml tool]
{
  "name": "cortex_convert_md_to_yaml",
  "arguments": {
    "input_path": "docs/requirements.md",
    "output_path": "requirements/feature.yaml"
  }
}
```

### Scenario 3: Project Health Monitoring

**Any repo with YAML plan files:**
```
User: "Show my project's progress dashboard"

Claude: [Uses cortex_generate_dashboard tool]
{
  "name": "cortex_generate_dashboard",
  "arguments": {
    "plan_dir": ".project/plans",
    "format": "ascii"
  }
}
```

---

## 🎯 Benefits of MCP Integration

### 1. **Universal Availability**
- Tools available in **any repository** via MCP client
- No need to copy/install tools per-project

### 2. **Consistent Interface**
- Standardized MCP protocol
- Works with VS Code, Claude Desktop, CLI tools

### 3. **Centralized Updates**
- Update tools in CORTEX repo → instantly available everywhere
- No version fragmentation

### 4. **Intelligent Invocation**
- LLM-based intent detection
- Natural language → tool calls
- Context-aware parameter inference

### 5. **Composability**
- Chain multiple tools together
- Example: `audit_requirements` → `detect_gaps` → `generate_dashboard`

---

## 📊 Tool Availability Matrix

| Tool | Local CLI | MCP Exposed | Cross-Repo | Status |
|------|-----------|-------------|------------|--------|
| YAML Validator | ✅ | ⏳ P1-T10 | ⏳ | Ready to integrate |
| Gap Detector | ✅ | ⏳ P1-T10 | ⏳ | Ready to integrate |
| MD→YAML Converter | ✅ | ⏳ P1-T10 | ⏳ | Ready to integrate |
| Dashboard Generator | ✅ | ⏳ P1-T10 | ⏳ | Ready to integrate |
| Checkpoint Manager | ✅ | ⏳ P1-T10 | ⏳ | Ready to integrate |
| Requirements Auditor | ✅ | ⏳ P1-T10 | ⏳ | Ready to integrate |
| Remediation Executor | ✅ | ⏳ P1-T11 | ⏳ | Ready to integrate |

---

## 🚀 Implementation Timeline

**Phase P1-T10: MCP Tool Registration (2 hours)**
- Create `src/mcp/tools/remediation_tools.py`
- Implement handlers for all 7 tools
- Register in capability registry
- Test via MCP protocol

**Phase P1-T11: Cross-Repo Validation (1 hour)**
- Test in external repository
- Validate parameter schemas
- Document usage patterns
- Create examples

**Total Effort:** 3 hours (included in P1 phase)

---

## 🛡️ Security & Governance

**Tool Execution Policies:**
- Tools respect workspace boundaries
- Git operations require confirmation
- File modifications are logged
- Audit trail maintained

**MCP Security:**
- Parameter validation enforced
- Schema compliance required
- Resource limits applied
- Error handling standardized

---

## 📝 Next Steps

1. **Complete P1 (Requirements Conversion)** first
2. **Add P1-T10/T11 tasks** to register tools in MCP
3. **Test in external repo** to validate cross-repo usage
4. **Document in CORTEX docs** for user adoption

---

**Status:** ✅ Tools are MCP-ready, integration pending P1-T10/T11  
**Timeline:** 3 hours of integration work (part of P1 phase)  
**Impact:** Universal tool availability across all repositories
