# Extensibility Capabilities

**Purpose:** Documentation of CORTEX extension mechanisms and customization  
**Audience:** Developers, Architects  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Custom Tool Development](#custom-tool-development)
- [Domain Orchestrator Extensions](#domain-orchestrator-extensions)
- [Knowledge Base Integration](#knowledge-base-integration)
- [Plugin Architecture](#plugin-architecture)
- [Extension Lifecycle](#extension-lifecycle)
- [Related Documents](#related-documents)

---

## Overview

CORTEX provides multiple extension points that allow organizations to customize and extend the platform without modifying core code:

1. **Custom Tools** — Add new MCP tools
2. **Domain Orchestrators** — Add domain-specific orchestrators
3. **Knowledge Integration** — Add organizational knowledge
4. **Plugins** — Extend analyzer capabilities

---

## Custom Tool Development

### Tool Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      TOOL ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                     Tool Base Class                        │ │
│  │  • Abstract execute() method                              │ │
│  │  • ToolDefinition property                                │ │
│  │  • Parameter validation                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                     Custom Tool                            │ │
│  │  • Implement execute()                                    │ │
│  │  • Define parameters                                       │ │
│  │  • Return structured result                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Tool Registry                           │ │
│  │  • Register tool                                          │ │
│  │  • Expose via MCP                                         │ │
│  │  • Apply governance                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Creating a Custom Tool

```python
from cortex.mcp.server import Tool, ToolDefinition, ToolParameter
from typing import Dict, Any

class MyCustomTool(Tool):
    """Custom tool for specific organization needs."""
    
    @property
    def definition(self) -> ToolDefinition:
        """Define tool metadata and parameters."""
        return ToolDefinition(
            name="my_custom_tool",
            description="Performs organization-specific operation",
            parameters=[
                ToolParameter(
                    name="input_data",
                    type="string",
                    required=True,
                    description="Input data to process"
                ),
                ToolParameter(
                    name="options",
                    type="object",
                    required=False,
                    description="Optional processing options"
                )
            ],
            metadata={
                "category": "custom",
                "version": "1.0.0",
                "author": "Organization Name"
            }
        )
    
    def execute(
        self,
        input_data: str,
        options: Dict[str, Any] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute the custom operation."""
        try:
            # Implement custom logic
            result = self._process_data(input_data, options or {})
            
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _process_data(
        self,
        data: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Internal processing logic."""
        # Custom implementation
        return {"processed": data}
```

### Registering Custom Tools

```python
from cortex.mcp.tool_registry import get_mcp_tool_registry

# Get registry instance
registry = get_mcp_tool_registry()

# Create and register tool
tool = MyCustomTool()
registry.register(tool.definition)

# Tool is now available via MCP
# Endpoint: POST /mcp/execute
# Body: {"name": "my_custom_tool", "arguments": {...}}
```

### Tool Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **GOVERNANCE** | Rule enforcement | Compliance checkers |
| **ORCHESTRATION** | Workflow management | Custom workflows |
| **KNOWLEDGE** | Information retrieval | Domain queries |
| **UTILITY** | General helpers | Data transformation |

---

## Domain Orchestrator Extensions

### Creating Domain Orchestrators

```python
from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err
from typing import Dict, Any

class CustomDomainOrchestrator(IOrchestrator):
    """Custom orchestrator for specific domain logic."""
    
    def __init__(self):
        self.name = "CustomDomainOrchestrator"
        self.category = "domain"
        self.priority = 150  # After standard domain orchestrators
        self.capabilities = ["custom_domain_operation"]
    
    def can_handle(self, operation: str) -> bool:
        """Check if this orchestrator can handle the operation."""
        return operation in self.capabilities
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
        mode: OperationMode = OperationMode.STANDARD
    ) -> Result[Dict[str, Any], str]:
        """Execute the domain operation."""
        try:
            # Validate parameters
            if not self._validate_parameters(parameters):
                return Err("Invalid parameters")
            
            # Execute domain logic
            result = self._execute_domain_logic(
                operation_name,
                parameters
            )
            
            return Ok(result)
            
        except Exception as e:
            return Err(f"Operation failed: {str(e)}")
    
    def _validate_parameters(
        self,
        parameters: Dict[str, Any]
    ) -> bool:
        """Validate operation parameters."""
        required = ["target", "action"]
        return all(key in parameters for key in required)
    
    def _execute_domain_logic(
        self,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific domain logic."""
        # Custom implementation
        return {"status": "completed"}
```

### Registering in Wiring Contract

```yaml
# Add to cortex/__wiring_contract__.yaml
orchestrators:
  - name: "CustomDomainOrchestrator"
    module: "company.orchestrators.custom_domain_orchestrator"
    class_name: "CustomDomainOrchestrator"
    category: "domain"
    priority: 150
    capabilities: ["custom_domain_operation"]
    dependencies: []
    is_optional: true
    version: "1.0.0"
```

### Orchestrator Integration Points

| Integration Point | Purpose | Example |
|-------------------|---------|---------|
| **IntentRouter** | Route requests | Add intent keywords |
| **MasterOrchestrator** | Coordinate execution | Register capabilities |
| **LENS** | Provide context | Add analyzers |
| **Governance** | Apply rules | Register policies |

---

## Knowledge Base Integration

### Knowledge Structure

```
company/
├── domains/
│   ├── authentication/
│   │   ├── best-practices.yaml
│   │   └── patterns.yaml
│   ├── payments/
│   │   ├── compliance.yaml
│   │   └── integrations.yaml
│   └── inventory/
│       ├── rules.yaml
│       └── workflows.yaml
└── standards/
    ├── coding-standards.yaml
    ├── security-policy.yaml
    └── review-checklist.yaml
```

### Knowledge YAML Format

```yaml
# company/domains/authentication/best-practices.yaml
domain: authentication
version: "1.0.0"
last_updated: "2026-02-10"

practices:
  - id: AUTH-001
    name: "Password Hashing"
    description: "Always use bcrypt with cost factor ≥ 12"
    severity: critical
    example: |
      from passlib.hash import bcrypt
      hashed = bcrypt.using(rounds=12).hash(password)
    
  - id: AUTH-002
    name: "Session Management"
    description: "Use secure, HttpOnly cookies with SameSite=Strict"
    severity: high
    
  - id: AUTH-003
    name: "Rate Limiting"
    description: "Limit login attempts to 5 per minute per IP"
    severity: high

patterns:
  - name: "JWT Authentication"
    when: "API authentication required"
    implementation: |
      # Standard JWT pattern for organization
      
  - name: "OAuth2 Integration"
    when: "Third-party authentication required"
    implementation: |
      # OAuth2 pattern for organization
```

### Loading Custom Knowledge

```python
from cortex.brain.knowledge import KnowledgeRepository

repo = KnowledgeRepository()

# Load organization knowledge
repo.load_directory("company/domains/")
repo.load_directory("company/standards/")

# Query with organization knowledge
context = repo.synthesize_for_operation(
    operation="implement",
    domain="authentication",
    include_organization=True  # Include company knowledge
)
```

### Knowledge Precedence

| Tier | Source | Precedence | Example |
|------|--------|------------|---------|
| **0** | CORTEX Core | Lowest | Core rules |
| **1** | Best Practices | Low | Industry patterns |
| **2** | Organization | High | Company standards |
| **3** | Domain-Specific | Highest | Team rules |

---

## Plugin Architecture

### Plugin Types

| Plugin Type | Extends | Use Case |
|------------|---------|----------|
| **Analyzer Plugin** | LENS | Add new analyzers |
| **Governance Plugin** | Enforcement | Add custom rules |
| **Integration Plugin** | MCP | Add external integrations |
| **Reporting Plugin** | Observability | Add custom reports |

### Creating an Analyzer Plugin

```python
from cortex.lens.core import BaseAnalyzer
from typing import Dict, Any
from pathlib import Path

class CustomAnalyzer(BaseAnalyzer):
    """Custom analyzer for organization-specific patterns."""
    
    name = "custom_analyzer"
    supported_extensions = [".py", ".ts", ".js"]
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file for organization-specific patterns."""
        content = file_path.read_text()
        
        results = {
            "custom_patterns": [],
            "violations": [],
            "recommendations": []
        }
        
        # Check for organization patterns
        results["custom_patterns"] = self._detect_patterns(content)
        
        # Check for violations
        results["violations"] = self._detect_violations(content)
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(
            results["custom_patterns"],
            results["violations"]
        )
        
        return results
    
    def _detect_patterns(self, content: str) -> list:
        """Detect organization-specific patterns."""
        # Custom pattern detection
        return []
    
    def _detect_violations(self, content: str) -> list:
        """Detect organization-specific violations."""
        # Custom violation detection
        return []
    
    def _generate_recommendations(
        self,
        patterns: list,
        violations: list
    ) -> list:
        """Generate improvement recommendations."""
        # Custom recommendation generation
        return []
```

### Plugin Registration

```python
from cortex.plugins import PluginRegistry

registry = PluginRegistry()

# Register analyzer plugin
registry.register_analyzer(CustomAnalyzer())

# Plugin is now used in LENS analysis
```

---

## Extension Lifecycle

### Development Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                   EXTENSION LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. DESIGN                                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Define extension purpose                               │ │
│  │  • Choose extension type                                   │ │
│  │  • Design interface                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  2. IMPLEMENT                                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Follow TDD (tests first)                               │ │
│  │  • Implement extension                                     │ │
│  │  • Add documentation                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  3. REGISTER                                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Add to registry                                        │ │
│  │  • Update wiring (if orchestrator)                        │ │
│  │  • Configure routing (if needed)                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  4. VALIDATE                                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Run integration tests                                  │ │
│  │  • Validate governance                                     │ │
│  │  • Performance testing                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  5. DEPLOY                                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Deploy to environment                                  │ │
│  │  • Monitor metrics                                         │ │
│  │  • Gather feedback                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Versioning

Extensions follow semantic versioning:

| Version Part | When to Increment |
|--------------|-------------------|
| **Major** | Breaking changes |
| **Minor** | New features (backward compatible) |
| **Patch** | Bug fixes |

### Deprecation Policy

| Phase | Duration | Action |
|-------|----------|--------|
| **Deprecated** | 2 releases | Add deprecation warnings |
| **Removed** | Next major | Remove from codebase |

---

## Related Documents

- [Tool Registry](../toolkit/tool-registry.md) — Tool management
- [Developer Guide](../toolkit/developer-guide.md) — Building tools
- [Domain Orchestrators](../orchestration/domain-orchestrators.md) — Orchestrator patterns

---

*Part of CORTEX Architecture Documentation*
