# CORTEX Component Architecture Specification

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** 2026-01-26  
**Status:** SPECIFICATION  

---

## 1. Overview

The CORTEX Component Architecture enables creation of **lightweight, shareable components** that provide CORTEX capabilities without requiring full infrastructure adoption.

### 1.1 Goals

1. **Shareability:** Components distributable via pip/npm
2. **Standalone Operation:** Work as MCP servers without CORTEX
3. **Progressive Enhancement:** Gain capabilities with full CORTEX
4. **Pattern Preservation:** Maintain CORTEX governance/audit/knowledge
5. **Team Autonomy:** Teams can adopt incrementally

### 1.2 Non-Goals

1. Full orchestrator capabilities in standalone mode
2. Complete CORTEX feature parity in lightweight mode
3. Replacing orchestrator architecture for complex workflows

---

## 2. Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FULL CORTEX MODE                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ MasterOrchestrator                                               │    │
│  │  ├─ DatabaseBackedRegistry (orchestrator wiring)                 │    │
│  │  ├─ Full Governance (35+ CORE rules)                             │    │
│  │  ├─ Full Audit (SHA256 hash chains)                              │    │
│  │  ├─ Full Knowledge (35+ YAML best practices)                     │    │
│  │  └─ StateManager (cross-orchestrator state)                      │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              │ Integration Layer                         │
│                              ▼                                           │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                     CORTEX COMPONENT LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ CORTEXComponent (Base Class)                                     │    │
│  │  ├─ LightweightGovernance (core rules subset)                    │    │
│  │  ├─ LightweightAudit (essential logging)                         │    │
│  │  ├─ ComponentKnowledge (domain-focused)                          │    │
│  │  └─ MCP Tool Exposure (standard interface)                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                              │                                           │
│                              │ Can operate standalone                    │
│                              ▼                                           │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                        STANDALONE MODE                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Component as MCP Server                                          │    │
│  │  ├─ Zero CORTEX dependency                                       │    │
│  │  ├─ Standard MCP protocol                                        │    │
│  │  ├─ Package manager installation (pip/npm)                       │    │
│  │  └─ Team-autonomous operation                                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Base Class

### 3.1 CORTEXComponent

```python
# cortex/components/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from cortex.components.governance import LightweightGovernance
from cortex.components.audit import LightweightAudit
from cortex.components.knowledge import ComponentKnowledge
from cortex.core.result import Result, Ok, Err


@dataclass
class ComponentMetadata:
    """Metadata for CORTEX components"""
    name: str
    version: str
    description: str
    author: str
    domain: str
    dependencies: List[str] = field(default_factory=list)
    mcp_tools: List[str] = field(default_factory=list)
    governance_rules: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CORTEXComponent(ABC):
    """
    Base class for shareable CORTEX components.
    
    Components can operate in two modes:
    1. STANDALONE: As MCP server without full CORTEX
    2. INTEGRATED: Within full CORTEX infrastructure
    
    Both modes get CORTEX patterns (governance, audit, knowledge)
    in appropriate weight for the mode.
    """
    
    # Component metadata (override in subclasses)
    metadata: ComponentMetadata
    
    def __init__(self, integrated_mode: bool = False):
        """
        Initialize CORTEX component.
        
        Args:
            integrated_mode: If True, uses full CORTEX infrastructure.
                           If False, uses lightweight standalone systems.
        """
        self._integrated_mode = integrated_mode
        
        if integrated_mode:
            # Full CORTEX integration
            self._init_integrated_mode()
        else:
            # Standalone lightweight mode
            self._init_standalone_mode()
    
    def _init_standalone_mode(self):
        """Initialize lightweight standalone systems"""
        self.governance = LightweightGovernance(
            rules=self.metadata.governance_rules
        )
        self.audit = LightweightAudit(
            component_name=self.metadata.name
        )
        self.knowledge = ComponentKnowledge(
            domain=self.metadata.domain
        )
    
    def _init_integrated_mode(self):
        """Initialize full CORTEX integration"""
        from cortex.brain.core.governance_registry import GovernanceRegistry
        from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
        from cortex.brain.core.knowledge.knowledge_repository import KnowledgeRepository
        
        self.governance = GovernanceRegistry.instance()
        self.audit = EnhancedAuditLogger.instance()
        self.knowledge = KnowledgeRepository()
    
    @abstractmethod
    async def execute(self, operation: str, params: Dict[str, Any]) -> Result:
        """
        Execute component operation.
        
        Args:
            operation: Operation name
            params: Operation parameters
            
        Returns:
            Result with operation outcome
        """
        pass
    
    @abstractmethod
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Get MCP tool definitions for this component.
        
        Returns:
            List of MCP tool schema definitions
        """
        pass
    
    async def execute_with_governance(
        self, 
        operation: str, 
        params: Dict[str, Any]
    ) -> Result:
        """
        Execute operation with governance and audit.
        
        This wrapper ensures CORTEX patterns are applied
        regardless of operation mode.
        """
        # Governance check
        governance_result = self.governance.validate_operation(
            operation=operation,
            context=params
        )
        if not governance_result.is_ok:
            return Err(f"Governance violation: {governance_result.error}")
        
        # Audit start
        operation_id = self.audit.log_operation_start(
            component=self.metadata.name,
            operation=operation,
            params=params
        )
        
        try:
            # Execute operation
            result = await self.execute(operation, params)
            
            # Audit complete
            self.audit.log_operation_complete(
                operation_id=operation_id,
                success=result.is_ok,
                result=result.value if result.is_ok else None,
                error=result.error if not result.is_ok else None
            )
            
            return result
            
        except Exception as e:
            # Audit failure
            self.audit.log_operation_complete(
                operation_id=operation_id,
                success=False,
                error=str(e)
            )
            return Err(str(e))
    
    def as_mcp_server(self) -> 'ComponentMCPServer':
        """
        Create MCP server from this component.
        
        Enables standalone operation without full CORTEX.
        """
        from cortex.components.mcp_server import ComponentMCPServer
        return ComponentMCPServer(self)
    
    @property
    def is_integrated(self) -> bool:
        """Check if running in integrated CORTEX mode"""
        return self._integrated_mode
```

### 3.2 Component Registration Decorator

```python
# cortex/components/registry.py

from typing import Type, List, Optional
from functools import wraps

# Global component registry
_component_registry: Dict[str, Type[CORTEXComponent]] = {}


def register_component(
    name: str,
    version: str,
    description: str,
    author: str,
    domain: str,
    dependencies: Optional[List[str]] = None,
    governance_rules: Optional[List[str]] = None
):
    """
    Decorator to register a CORTEX component.
    
    Usage:
        @register_component(
            name="test-automation",
            version="1.0.0",
            description="CORTEX-powered test generation",
            author="cortex-team",
            domain="testing"
        )
        class TestAutomationComponent(CORTEXComponent):
            pass
    """
    def decorator(cls: Type[CORTEXComponent]) -> Type[CORTEXComponent]:
        # Create metadata
        cls.metadata = ComponentMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            domain=domain,
            dependencies=dependencies or [],
            governance_rules=governance_rules or ['CORE-027-AUDIT']
        )
        
        # Register in global registry
        _component_registry[name] = cls
        
        return cls
    
    return decorator


def get_component(name: str) -> Optional[Type[CORTEXComponent]]:
    """Get registered component by name"""
    return _component_registry.get(name)


def list_components() -> List[str]:
    """List all registered component names"""
    return list(_component_registry.keys())
```

---

## 4. Integration with MasterOrchestrator

### 4.1 Component Discovery

```python
# cortex/orchestrators/core/component_integration.py

class ComponentIntegration:
    """
    Integrates CORTEX components with MasterOrchestrator.
    
    Enables MasterOrchestrator to:
    1. Discover available components
    2. Route operations to components
    3. Manage component lifecycle
    """
    
    def __init__(self, master_orchestrator: 'MasterOrchestrator'):
        self.master = master_orchestrator
        self._components: Dict[str, CORTEXComponent] = {}
    
    async def discover_components(self):
        """Discover and register all available components"""
        from cortex.components.registry import list_components, get_component
        
        for component_name in list_components():
            component_class = get_component(component_name)
            if component_class:
                # Initialize in integrated mode
                component = component_class(integrated_mode=True)
                self._components[component_name] = component
                
                # Register MCP tools with MasterOrchestrator
                for tool in component.get_mcp_tools():
                    self.master.register_mcp_tool(
                        tool_name=f"{component_name}.{tool['name']}",
                        handler=self._create_handler(component, tool['name'])
                    )
    
    def _create_handler(self, component: CORTEXComponent, operation: str):
        """Create handler function for component operation"""
        async def handler(**params):
            return await component.execute_with_governance(operation, params)
        return handler
    
    async def route_to_component(
        self, 
        component_name: str, 
        operation: str, 
        params: Dict[str, Any]
    ) -> Result:
        """Route operation to specific component"""
        component = self._components.get(component_name)
        if not component:
            return Err(f"Component not found: {component_name}")
        
        return await component.execute_with_governance(operation, params)
```

### 4.2 MasterOrchestrator Updates

```python
# Add to MasterOrchestrator.__init__

# AC-COMPONENT-INTEGRATION-001: Initialize component integration
self._component_integration = ComponentIntegration(self)

# In execute_operation, add component routing:
async def execute_operation(self, operation: str, context: Dict[str, Any]) -> Result:
    # Check if operation targets a component
    if '.' in operation:
        component_name, op_name = operation.split('.', 1)
        if component_name in self._component_integration._components:
            return await self._component_integration.route_to_component(
                component_name, op_name, context
            )
    
    # Continue with standard orchestrator routing
    # ... existing code ...
```

---

## 5. Standalone MCP Server

### 5.1 ComponentMCPServer

```python
# cortex/components/mcp_server.py

from mcp import Server, Tool
from typing import Dict, Any, List
import asyncio


class ComponentMCPServer:
    """
    MCP server wrapper for CORTEX components.
    
    Enables components to run as standalone MCP servers
    without full CORTEX infrastructure.
    """
    
    def __init__(self, component: CORTEXComponent):
        self.component = component
        self.server = Server(
            name=component.metadata.name,
            version=component.metadata.version
        )
        self._register_tools()
    
    def _register_tools(self):
        """Register component tools with MCP server"""
        for tool_def in self.component.get_mcp_tools():
            @self.server.tool(
                name=tool_def['name'],
                description=tool_def['description'],
                input_schema=tool_def['input_schema']
            )
            async def handler(params: Dict[str, Any], tool_name=tool_def['name']):
                result = await self.component.execute_with_governance(
                    tool_name, params
                )
                if result.is_ok:
                    return result.value
                else:
                    raise Exception(result.error)
    
    def run(self, transport: str = 'stdio'):
        """Run MCP server"""
        if transport == 'stdio':
            from mcp.transports import StdioTransport
            asyncio.run(self.server.run(StdioTransport()))
        elif transport == 'http':
            from mcp.transports import HTTPTransport
            asyncio.run(self.server.run(HTTPTransport(port=8080)))
```

### 5.2 CLI Entry Point

```python
# cortex/components/cli.py

import click
import importlib


@click.group()
def cli():
    """CORTEX Component CLI"""
    pass


@cli.command()
@click.argument('component_name')
@click.option('--transport', default='stdio', help='MCP transport (stdio/http)')
def serve(component_name: str, transport: str):
    """Run component as MCP server"""
    from cortex.components.registry import get_component
    
    component_class = get_component(component_name)
    if not component_class:
        click.echo(f"Component not found: {component_name}")
        return
    
    component = component_class(integrated_mode=False)
    server = component.as_mcp_server()
    
    click.echo(f"Starting {component_name} MCP server on {transport}...")
    server.run(transport=transport)


@cli.command()
def list():
    """List available components"""
    from cortex.components.registry import list_components
    
    for name in list_components():
        click.echo(name)


if __name__ == '__main__':
    cli()
```

---

## 6. Mode Comparison

| Capability | Standalone Mode | Integrated Mode |
|------------|-----------------|-----------------|
| **MCP Tools** | ✅ Full | ✅ Full |
| **Governance** | ✅ Lightweight (core rules) | ✅ Full (35+ rules) |
| **Audit** | ✅ Lightweight (JSON logs) | ✅ Full (hash chains) |
| **Knowledge** | ✅ Domain-focused | ✅ Full repository |
| **State Management** | ❌ None | ✅ StateManager |
| **Cross-component coordination** | ❌ None | ✅ MasterOrchestrator |
| **DatabaseBackedRegistry** | ❌ None | ✅ Full |
| **Complex workflows** | ❌ Limited | ✅ Full orchestration |
| **Installation** | `pip install cortex-{name}` | Full CORTEX |
| **Team adoption** | Zero CORTEX knowledge | CORTEX familiarity |

---

## 7. Package Structure

### 7.1 Component Package Layout

```
cortex-test-automation/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── cortex_test_automation/
│       ├── __init__.py
│       ├── component.py          # Main component class
│       ├── tools/                 # Domain-specific tools
│       │   ├── __init__.py
│       │   ├── ado_client.py
│       │   ├── framework_scanner.py
│       │   └── test_generator.py
│       ├── knowledge/             # Domain knowledge
│       │   └── testing.yaml
│       └── governance/            # Domain governance rules
│           └── testing_rules.yaml
├── tests/
│   ├── test_component.py
│   └── test_tools.py
└── examples/
    └── usage.py
```

### 7.2 pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cortex-test-automation"
version = "1.0.0"
description = "CORTEX-powered test automation component"
authors = [{name = "CORTEX Team", email = "cortex@example.com"}]
license = "MIT"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "cortex-components>=1.0.0",
    "mcp>=1.0.0",
    "aiohttp>=3.8.0"
]

[project.optional-dependencies]
cortex = [
    "cortex>=6.0.0"  # For integrated mode
]

[project.scripts]
cortex-test-automation = "cortex_test_automation.cli:main"

[project.entry-points."cortex.components"]
test-automation = "cortex_test_automation:TestAutomationComponent"
```

---

## 8. Progressive Enhancement Path

### 8.1 Team Adoption Journey

```
Stage 1: Discovery
├─ Team discovers component
├─ pip install cortex-test-automation
├─ Runs as standalone MCP server
└─ Zero CORTEX knowledge required

Stage 2: Usage
├─ Team uses component via Copilot/Claude
├─ Experiences CORTEX patterns (governance, audit)
├─ Gains familiarity with CORTEX approach
└─ Sees value in structured development

Stage 3: Exploration
├─ Team wants more components
├─ Explores other cortex-* packages
├─ Understands component ecosystem
└─ Considers full CORTEX adoption

Stage 4: Integration
├─ Team adopts full CORTEX
├─ Components auto-upgrade to integrated mode
├─ Gains full CORTEX capabilities
└─ Contributes new components back
```

### 8.2 Component Upgrade Path

```python
# Standalone installation
pip install cortex-test-automation

# Usage (standalone mode)
from cortex_test_automation import TestAutomationComponent
component = TestAutomationComponent()  # integrated_mode=False by default

# After full CORTEX adoption
pip install cortex

# Usage (integrated mode - automatic detection)
from cortex_test_automation import TestAutomationComponent
component = TestAutomationComponent()  # Detects CORTEX, uses integrated_mode=True

# Explicit mode selection
component = TestAutomationComponent(integrated_mode=True)
```

---

## 9. Security & Governance

### 9.1 Lightweight Governance Rules

Components include a subset of CORE rules appropriate for standalone operation:

```yaml
# Minimal governance for standalone components
lightweight_rules:
  - CORE-013: No bare except clauses
  - CORE-027: Audit trail for operations
  - CORE-011: Type hints required
  - CORE-012: Docstrings required

# Additional rules in integrated mode (full set)
integrated_rules:
  - All 35+ CORE rules
  - DatabaseBackedRegistry enforcement
  - Hash chain audit trails
```

### 9.2 Component Signing

```python
# Future: Component signature verification
@register_component(
    name="test-automation",
    version="1.0.0",
    signature="sha256:abc123...",  # Package signature
    trusted_publisher="cortex-team"  # Verified publisher
)
class TestAutomationComponent(CORTEXComponent):
    pass
```

---

## 10. Next Steps

See:
- [specifications/component-base-spec.md](../specifications/component-base-spec.md) - Detailed base class spec
- [specifications/governance-lightweight-spec.md](../specifications/governance-lightweight-spec.md) - Governance spec
- [examples/test-automation-component.yaml](../examples/test-automation-component.yaml) - Example component
- [implementation/implementation-plan.md](../implementation/implementation-plan.md) - Implementation plan
