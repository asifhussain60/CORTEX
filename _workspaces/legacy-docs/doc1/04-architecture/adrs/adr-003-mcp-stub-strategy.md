# ADR-003: MCP Stub Strategy

> Architecture Decision Record

**Status:** Accepted  
**Date:** 2026-01-20  
**Deciders:** CORTEX Architecture Team  
**Technical Story:** Phase B - MCP Centralization

## Context

CORTEX implements 14 MCP tools for AI-native integration. The tools were scaffolded before the core governance and knowledge systems were complete. A decision was needed on whether to implement tools immediately or defer until dependencies are ready.

## Decision

Maintain MCP tools as **stub implementations** until Phase B (MCP Centralization) completes.

### Stub Strategy

```python
# Current stub pattern
async def query_tool(query: str, context: Dict) -> ToolResult:
    """Query governance rules (STUB)."""
    return ToolResult(
        success=True,
        data={"stub": True, "message": "Implementation pending Phase B"},
        metadata={"tool": "query_tool", "status": "stub"}
    )
```

### Implementation Timeline

| Phase | Tools Affected | Status |
|-------|----------------|--------|
| Pre-Phase B | All 14 tools | Stub (mock data) |
| Phase B | Registry, Discovery | Implemented |
| Post-Phase B | All tools | Full implementation |

### Rationale

1. **Dependency order** - Tools depend on registry (Phase B)
2. **Contract stability** - Tool schemas finalized before implementation
3. **Testing enablement** - Stubs allow integration testing
4. **Risk reduction** - Avoid rework when registry changes

## Consequences

### Positive

- Clear separation of concerns (registry vs tool logic)
- Integration tests can proceed with stubs
- Tool contracts are stable and documented
- Implementation can be parallelized post-Phase B

### Negative

- 14 tools non-functional until Phase B
- Risk of stub behavior leaking into production
- Documentation must clearly mark stub status

### Risks

- Phase B delay extends stub period
- Users may expect functional tools from MCP discovery

## Mitigation

1. Clear `status: stub` in all tool metadata
2. Tool results include `stub: true` flag
3. Documentation explicitly notes stub status
4. Phase B prioritized in roadmap

## Alternatives Considered

1. **Implement immediately** - Rejected: Registry dependency missing
2. **No stubs (errors)** - Rejected: Breaks integration testing
3. **Partial implementation** - Rejected: Inconsistent behavior

## Related

- [MCP Tool Governance](../10-mcp-tool-governance.md)
- [MCP Tools Diagram](../_diagrams/mcp-tools.mmd)
- `cortex/mcp/tools/`
