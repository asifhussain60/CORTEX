# API Reference Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-20

---

## Available APIs

CORTEX provides three API interfaces:

### 1. REST API
- **Protocol:** HTTP/HTTPS
- **Format:** JSON
- **Authentication:** API key or OAuth 2.0
- **Docs:** [REST API Guide](rest-api/0-guide.md)

### 2. MCP Protocol
- **Protocol:** Model Context Protocol (JSON-RPC 2.0)
- **Use Case:** AI assistant integration
- **Status:** ⚠️ 14 tools (stub implementations, see [MCP Guide](mcp-protocol/0-specification.md))
- **Docs:** [MCP Protocol Specification](mcp-protocol/0-specification.md)

### 3. CLI
- **Tool:** `cortex-cli`
- **Use Case:** Local development, automation
- **Docs:** [CLI Command Reference](cli/0-guide.md)

---

## Quick Reference

| Operation | REST | MCP | CLI |
|-----------|------|-----|-----|
| Create Orchestrator | POST /orchestrators | N/A | cortex orchestrator create |
| Execute | POST /orchestrators/{id}/execute | Call tool | cortex execute |
| Get Status | GET /status | Call tool | cortex status |
| Query Knowledge | GET /knowledge | Call tool | cortex knowledge query |

---

## Authentication

All APIs require authentication. See individual guides for setup.

---

## Related Documentation

- [REST API Guide](rest-api/0-guide.md)
- [MCP Specification](mcp-protocol/0-specification.md)
- [CLI Reference](cli/0-guide.md)
- [Integration Guides](../04-guides/integration/0-overview.md)

