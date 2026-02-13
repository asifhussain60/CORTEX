# Known Issues & Workarounds

Track known issues and recommended workarounds.

## Critical Limitations (2026-01-20)

### ⚠️ MCP Tools Return Mock Data (STUB IMPLEMENTATIONS)

**Issue**: All 14 MCP tools registered but return stub/mock data  
**Severity**: HIGH for production MCP integrations  
**Status**: STUB_ONLY - Requires implementation in Phase 26+  
**Affected Tools**:
- `sample_tool`, `echo_tool`, `status_tool`, `query_tool`
- `validate_tool`, `transform_tool`, `analyze_tool`, `generate_tool`
- `execute_tool`, `monitor_tool`, `alert_tool`, `report_tool`
- `optimize_tool`, `diagnose_tool`

**Impact**: 
- ✅ MCP tool discovery and schema validation works
- ❌ Tool execution returns mock/example data only
- ❌ Integration with external MCP clients receives stub responses
- ⏳ Production use requires tool functional implementation

**Workaround**: 
- Use REST API endpoints directly (fully implemented)
- Use orchestrator @mcp_tool decorated methods (functional)
- Refer to [MCP Protocol Status](../03-api-reference/mcp-protocol/0-specification.md) for tool-by-tool status

**Resolution**: See governance tools section below for exceptions.

---

### ⚠️ Governance Rules Engine - Partial Implementation

**Issue**: Tier 0 core governance rules incomplete  
**Severity**: MEDIUM for complex governance scenarios  
**Status**: PARTIAL - `core-rules.yaml` missing  
**Details**:
- Tier 0: 2 YAML files (prompt-versions.yaml, repo-registry.yaml) ✅
- Tier 1: Empty (architecture rules not populated)
- Tier 2: Empty (standards templates not populated)
- core-rules.yaml: Missing (blocks full enforcement)

**Impact**:
- ✅ Phase locking works (AC-AR-008-01)
- ✅ AC-ID validation works (AC-AR-009-01)
- ⚠️ Complex governance scenarios fail (requires core-rules.yaml)
- ⚠️ Tier 1 & 2 rules enforcement unavailable

**Workaround**: 
- Use Tier 0 only for current operations
- Create custom governance rules via API
- Reference governance.db directly for state queries

**Resolution**: Implement consolidation-001-src-cleanup and governance rules loading.

---

### ⚠️ Source Code Consolidation Pending

**Issue**: Dual package structure (cortex/ canonical, src/ deprecated)  
**Severity**: LOW - doesn't affect runtime but creates confusion  
**Status**: PENDING - Not started (Phase: consolidation-001-src-cleanup)  
**Details**:
- cortex/ package: 413 files (canonical, active)
- src/ package: 30+ files (deprecated, being consolidated)
- Import paths: Mix of cortex.* and src.* across codebase

**Impact**:
- Documentation may reference src.* imports (outdated)
- Tests reference both cortex.* and src.* (redundant)
- Future imports should use cortex.* only

**Workaround**: Always import from cortex.*, not src.*

**Resolution**: Consolidation-001 phase will migrate all src.* to cortex.* and delete src/.

---

## Performance

### Issue: Knowledge queries are slow
**Symptom**: `Domain Brain query timeout` in logs  
**Root Cause**: Large knowledge base without proper indexing  
**Workaround**:
```bash
# Reindex knowledge repository
cortex admin reindex-knowledge --parallel 4
```
**Fix**: Upgrade to next version with query optimization

---

### Issue: High memory usage in production
**Symptom**: CORTEX process uses >4GB RAM  
**Root Cause**: Unbounded in-memory cache  
**Workaround**:
```yaml
# In cortex-config.yaml
cache:
  max_size: 1000
  ttl: 3600
```

---

## Operational

### Issue: Audit trail database locked
**Symptom**: `governance.db is locked` error  
**Root Cause**: Multiple CORTEX instances writing simultaneously  
**Workaround**: Ensure only one writer instance  
**Fix**: Use PostgreSQL backend for multi-instance setup

---

### Issue: Orchestrator timeout during knowledge retrieval
**Symptom**: Orchestrator fails with timeout after 30s  
**Root Cause**: Knowledge Brain is slow  
**Workaround**:
```yaml
# Increase timeout in orchestrator context
timeout: 60  # seconds
```

---

## Integration

### Issue: REST API returns 401 even with valid token
**Symptom**: `Unauthorized` from valid JWT token  
**Root Cause**: Token clock skew  
**Workaround**: Sync system clocks across infrastructure

---

## Documentation

For detailed troubleshooting, see [Troubleshooting Guide](../04-guides/operations/4-troubleshooting.md).
