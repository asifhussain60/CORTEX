# MCP Versioning

**Purpose:** Version management for CORTEX MCP tools  
**Audience:** Developers, Operations  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Version Schema](#version-schema)
- [Compatibility](#compatibility)
- [Deprecation](#deprecation)
- [Migration](#migration)
- [Related Documents](#related-documents)

---

## Overview

CORTEX uses semantic versioning for both the MCP protocol and individual tools.

```
┌─────────────────────────────────────────────────────────────────┐
│                   VERSION MANAGEMENT                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Protocol Version                                         │  │
│  │  • MCP specification version                              │  │
│  │  • Format: YYYY-MM-DD (e.g., 2024-11-05)                 │  │
│  │  • Negotiated during initialize                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Server Version                                           │  │
│  │  • CORTEX release version                                 │  │
│  │  • Format: major.minor.patch                              │  │
│  │  • Returned in serverInfo                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tool Versions                                            │  │
│  │  • Individual tool versions                               │  │
│  │  • Format: major.minor.patch                              │  │
│  │  • Independent of server version                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Version Schema

### Semantic Versioning

```
{major}.{minor}.{patch}

major: Breaking changes
minor: New features (backward compatible)
patch: Bug fixes (backward compatible)

Examples:
  1.0.0 → Initial release
  1.1.0 → New parameter added
  1.1.1 → Bug fix
  2.0.0 → Breaking parameter change
```

### Protocol Version

```json
// Initialize request
{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "clientInfo": {
            "name": "my-client",
            "version": "1.0.0"
        }
    },
    "id": 0
}

// Initialize response
{
    "jsonrpc": "2.0",
    "result": {
        "protocolVersion": "2024-11-05",
        "serverInfo": {
            "name": "cortex-mcp",
            "version": "1.5.0"
        }
    },
    "id": 0
}
```

### Tool Versions

```json
// tools/list response
{
    "tools": [
        {
            "name": "cortex_lens_analyze",
            "description": "...",
            "version": "1.2.0",
            "deprecated": false
        },
        {
            "name": "cortex_ast_analyze",
            "description": "...",
            "version": "2.0.0",
            "deprecated": false
        }
    ]
}
```

---

## Compatibility

### Compatibility Matrix

| Client Version | Server 1.x | Server 2.x |
|---------------|------------|------------|
| 1.0.x | ✅ Full | ⚠️ Partial |
| 1.1.x | ✅ Full | ⚠️ Partial |
| 2.0.x | ⚠️ Partial | ✅ Full |

### Checking Compatibility

```python
class VersionChecker:
    """Check version compatibility."""
    
    def is_compatible(
        self,
        client_version: str,
        server_version: str
    ) -> tuple[bool, str]:
        """
        Check if client is compatible with server.
        
        Returns:
            (is_compatible, message)
        """
        client = self._parse(client_version)
        server = self._parse(server_version)
        
        # Same major version = compatible
        if client[0] == server[0]:
            return (True, "Compatible")
        
        # Client newer than server
        if client[0] > server[0]:
            return (
                False,
                f"Client {client_version} requires server {client[0]}.x"
            )
        
        # Client older than server
        return (
            True,
            f"Client {client_version} is older, consider upgrade"
        )
```

### Negotiation

```python
async def negotiate_version(
    client_version: str,
    supported_versions: list[str]
) -> str:
    """Negotiate protocol version."""
    # Parse client version
    client_date = parse_date(client_version)
    
    # Find best match
    for version in sorted(supported_versions, reverse=True):
        server_date = parse_date(version)
        if server_date <= client_date:
            return version
    
    # Fall back to oldest supported
    return supported_versions[-1]
```

---

## Deprecation

### Deprecation Process

```
┌─────────────────────────────────────────────────────────────────┐
│                  DEPRECATION TIMELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  v1.0 ──► v1.1 ──► v1.2 ──► v2.0 ──► v2.1 ──► v2.2 ──► v3.0   │
│                      │                  │                        │
│                      │                  └── Old tool removed     │
│                      │                                           │
│                      └── Tool deprecated, replacement available  │
│                                                                  │
│  Timeline:                                                       │
│  • Deprecation announced at v1.2                                │
│  • Warning emitted at v2.0                                      │
│  • Tool removed at v3.0 (minimum 2 minor versions)              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Deprecation Markers

```json
// Deprecated tool in tools/list
{
    "name": "cortex_old_analyze",
    "description": "Analyze code (DEPRECATED: use cortex_lens_analyze)",
    "version": "1.0.0",
    "deprecated": true,
    "replacement": "cortex_lens_analyze",
    "removalVersion": "3.0.0"
}
```

### Deprecation Warnings

```python
class DeprecationHandler:
    """Handle deprecated tool invocations."""
    
    async def handle_call(
        self,
        tool: Tool,
        arguments: dict
    ) -> ToolResult:
        """Handle call with deprecation warning."""
        metadata = self.registry.get_metadata(tool.name)
        
        if metadata.deprecated:
            # Log warning
            logger.warning(
                f"Tool {tool.name} is deprecated, "
                f"use {metadata.replacement} instead"
            )
            
            # Add warning to result
            result = await tool.execute(arguments)
            result.warnings = result.warnings or []
            result.warnings.append(
                f"DEPRECATED: {tool.name} will be removed in "
                f"v{metadata.removal_version}. "
                f"Use {metadata.replacement} instead."
            )
            
            return result
        
        return await tool.execute(arguments)
```

---

## Migration

### Migration Guides

#### v1.x to v2.x

**Breaking Changes:**

| v1.x | v2.x | Action |
|------|------|--------|
| `cortex_analyze` | `cortex_lens_analyze` | Update tool name |
| `path` parameter | `target` parameter | Rename parameter |
| Sync responses | Async responses | Handle promises |

**Migration Script:**

```python
# Migration helper
def migrate_v1_to_v2(request: dict) -> dict:
    """Migrate v1 request to v2 format."""
    migrated = request.copy()
    
    # Rename tools
    tool_renames = {
        "cortex_analyze": "cortex_lens_analyze",
        "cortex_audit_code": "cortex_audit",
    }
    
    if migrated.get("name") in tool_renames:
        migrated["name"] = tool_renames[migrated["name"]]
    
    # Rename parameters
    args = migrated.get("arguments", {})
    if "path" in args:
        args["target"] = args.pop("path")
    
    return migrated
```

### Version Discovery

```bash
# Check server version
curl http://localhost:8000/health
# {"version": "2.1.0", ...}

# List tools with versions
curl -X POST http://localhost:8000/mcp \
    -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' \
    | jq '.result.tools[] | {name, version, deprecated}'
```

### Upgrade Checklist

- [ ] Review changelog for breaking changes
- [ ] Update client version
- [ ] Test with new server version
- [ ] Update deprecated tool calls
- [ ] Verify parameter changes
- [ ] Update error handling for new codes
- [ ] Run integration tests
- [ ] Deploy updated client

---

## Related Documents

- [MCP Overview](overview.md) — Introduction
- [MCP Protocol](protocol.md) — Protocol details
- [Integration Guide](integration.md) — Client integration

---

*Part of CORTEX Architecture Documentation*
