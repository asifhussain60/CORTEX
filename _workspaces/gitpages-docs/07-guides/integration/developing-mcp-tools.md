# Developing MCP Tools

**Status:** Production Ready | **Last Updated:** 2026-01-21

Create custom MCP tools for CORTEX integration.

## Overview

MCP tools expose CORTEX functionality through the Model Context Protocol JSON-RPC interface.

## Tool Development Guide

```python
from cortex.mcp.tools import Tool

class CustomTool(Tool):
    def __init__(self):
        super().__init__()
        self.name = "custom_tool"
        self.description = "My custom tool"
    
    def execute(self, **params):
        return {"result": "success"}
```

## Related Resources

- [MCP Integration Tutorial](../../06-tutorials/api-integration/2-mcp-integration.md)
- [MCP Protocol Specification](../../03-api-reference/mcp-protocol/0-specification.md)
