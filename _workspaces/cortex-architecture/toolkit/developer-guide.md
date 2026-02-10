# Tool Developer Guide

**Purpose:** Guide for creating new CORTEX tools  
**Audience:** Developers, Contributors  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Tool Structure](#tool-structure)
- [Implementation Steps](#implementation-steps)
- [Testing Tools](#testing-tools)
- [Best Practices](#best-practices)
- [Related Documents](#related-documents)

---

## Overview

This guide walks through creating a new CORTEX MCP tool from scratch.

### Prerequisites

- Understanding of MCP protocol
- Python 3.9+
- Familiarity with async/await

---

## Tool Structure

### Base Class

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from cortex.mcp.models import ToolResult, ToolParameter

class Tool(ABC):
    """Base class for all CORTEX tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name (cortex_*)."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for documentation."""
        pass
    
    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """Define tool parameters."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        arguments: Dict[str, Any]
    ) -> ToolResult:
        """Execute the tool with given arguments."""
        pass
    
    def get_required_parameters(self) -> List[str]:
        """Get list of required parameter names."""
        return [
            p.name for p in self.get_parameters()
            if p.required
        ]
```

### ToolParameter

```python
@dataclass
class ToolParameter:
    """Parameter definition."""
    
    name: str
    type: str  # string, number, boolean, object, array
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
```

### ToolResult

```python
@dataclass
class ToolResult:
    """Tool execution result."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
```

---

## Implementation Steps

### Step 1: Create Tool Class

```python
# cortex/mcp/tools/my_custom_tool.py

from cortex.mcp.base import Tool, ToolParameter, ToolResult

class MyCustomTool(Tool):
    """
    A custom tool for CORTEX.
    
    This tool does something useful.
    """
    
    @property
    def name(self) -> str:
        return "cortex_my_custom"
    
    @property
    def description(self) -> str:
        return "Perform a custom operation"
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="target",
                type="string",
                description="Target file or directory",
                required=True
            ),
            ToolParameter(
                name="options",
                type="object",
                description="Additional options",
                required=False,
                default={}
            )
        ]
    
    async def execute(
        self,
        arguments: Dict[str, Any]
    ) -> ToolResult:
        # Validate arguments
        target = arguments.get("target")
        if not target:
            return ToolResult(
                success=False,
                error="Target is required"
            )
        
        # Perform operation
        try:
            result = await self._do_operation(target)
            
            return ToolResult(
                success=True,
                data={"result": result}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    async def _do_operation(self, target: str) -> Dict:
        """Internal operation logic."""
        # Your logic here
        return {"processed": target}
```

### Step 2: Add Metadata

```python
# cortex/mcp/tools/my_custom_tool.py (continued)

from cortex.mcp.registry import ToolMetadata, ToolCategory

TOOL_METADATA = ToolMetadata(
    name="cortex_my_custom",
    category=ToolCategory.CORE,
    description="Perform a custom operation",
    version="1.0.0",
    parameters=[
        ToolParameter(
            name="target",
            type="string",
            description="Target file or directory",
            required=True
        ),
        ToolParameter(
            name="options",
            type="object",
            description="Additional options",
            required=False,
            default={}
        )
    ],
    required_parameters=["target"],
    examples=[
        {
            "description": "Basic usage",
            "arguments": {"target": "src/app.py"},
            "result": {"success": True}
        }
    ],
    related_tools=["cortex_lens_analyze"]
)
```

### Step 3: Register Tool

```python
# cortex/mcp/tools/__init__.py

from cortex.mcp.registry import ToolRegistry
from cortex.mcp.tools.my_custom_tool import MyCustomTool, TOOL_METADATA

def register_tools():
    """Register all tools with the registry."""
    registry = ToolRegistry.instance()
    
    # Register custom tool
    registry.register(MyCustomTool(), TOOL_METADATA)
    
    # ... other registrations
```

### Step 4: Expose via MCP

The MCP server automatically exposes registered tools:

```python
# cortex/mcp/server.py

@app.route("/mcp/tools/list", methods=["GET"])
async def list_tools():
    """List all available tools."""
    registry = ToolRegistry.instance()
    return jsonify([
        metadata.to_dict()
        for metadata in registry.list_all()
    ])

@app.route("/mcp/tools/call", methods=["POST"])
async def call_tool():
    """Call a tool by name."""
    request = await request.json()
    
    tool_name = request["name"]
    arguments = request.get("arguments", {})
    
    registry = ToolRegistry.instance()
    tool = registry.get(tool_name)
    
    if not tool:
        return jsonify({"error": f"Tool not found: {tool_name}"})
    
    result = await tool.execute(arguments)
    return jsonify(result.to_dict())
```

---

## Testing Tools

### Unit Tests

```python
# tests/mcp/tools/test_my_custom_tool.py

import pytest
from cortex.mcp.tools.my_custom_tool import MyCustomTool

class TestMyCustomTool:
    
    @pytest.fixture
    def tool(self):
        return MyCustomTool()
    
    def test_name(self, tool):
        assert tool.name == "cortex_my_custom"
    
    def test_parameters(self, tool):
        params = tool.get_parameters()
        assert len(params) == 2
        assert params[0].name == "target"
        assert params[0].required is True
    
    @pytest.mark.asyncio
    async def test_execute_success(self, tool):
        result = await tool.execute({"target": "test.py"})
        
        assert result.success is True
        assert "result" in result.data
    
    @pytest.mark.asyncio
    async def test_execute_missing_target(self, tool):
        result = await tool.execute({})
        
        assert result.success is False
        assert "required" in result.error.lower()
```

### Integration Tests

```python
# tests/integration/test_mcp_tools.py

import pytest
import httpx

class TestMCPToolIntegration:
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.mark.asyncio
    async def test_call_my_custom_tool(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "cortex_my_custom",
                        "arguments": {"target": "test.py"}
                    },
                    "id": 1
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["success"] is True
```

---

## Best Practices

### Naming Conventions

```python
# ✅ Good
"cortex_lens_analyze"
"cortex_git_history"
"cortex_plan_sync"

# ❌ Bad
"analyze"           # No prefix
"cortex-analyze"    # Hyphen instead of underscore
"CortexAnalyze"     # CamelCase
```

### Error Handling

```python
async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
    # Validate early
    if not self._validate_arguments(arguments):
        return ToolResult(
            success=False,
            error="Invalid arguments"
        )
    
    try:
        # Main logic
        result = await self._process(arguments)
        return ToolResult(success=True, data=result)
        
    except FileNotFoundError as e:
        return ToolResult(
            success=False,
            error=f"File not found: {e}"
        )
    except PermissionError as e:
        return ToolResult(
            success=False,
            error=f"Permission denied: {e}"
        )
    except Exception as e:
        # Log unexpected errors
        logger.exception("Unexpected error in tool")
        return ToolResult(
            success=False,
            error=f"Internal error: {type(e).__name__}"
        )
```

### Documentation

```python
class WellDocumentedTool(Tool):
    """
    A well-documented tool.
    
    This tool performs X operation by doing Y.
    
    Example:
        result = await tool.execute({
            "target": "path/to/file",
            "options": {"verbose": True}
        })
    
    Notes:
        - Requires file read permissions
        - Caches results for 1 hour
    """
    
    @property
    def description(self) -> str:
        return (
            "Perform X operation on target files. "
            "Supports Python, TypeScript, and Java."
        )
```

### Performance

```python
class PerformantTool(Tool):
    
    def __init__(self):
        # Initialize expensive resources once
        self._cache = {}
        self._analyzer = ExpensiveAnalyzer()
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        target = arguments["target"]
        
        # Check cache first
        cache_key = self._build_cache_key(target)
        if cache_key in self._cache:
            return ToolResult(
                success=True,
                data=self._cache[cache_key]
            )
        
        # Use timeout for external operations
        try:
            result = await asyncio.wait_for(
                self._analyze(target),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                error="Operation timed out"
            )
        
        # Cache result
        self._cache[cache_key] = result
        
        return ToolResult(success=True, data=result)
```

---

## Related Documents

- [Toolkit Overview](overview.md) — Introduction
- [Tool Registry](tool-registry.md) — Registration
- [Security Model](security-model.md) — Security

---

*Part of CORTEX Architecture Documentation*
