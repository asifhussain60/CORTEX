# Dashboard Orchestrator Guide

## Overview

The **DashboardOrchestrator** provides unified dashboard generation and synchronization across all CORTEX repositories. It consolidates 5 legacy dashboard SPAs into a single, unified SPA with orchestrator integration.

**Key Benefits:**
- Single unified SPA (vs 5 legacy dashboards) = 68% size reduction
- JSON-first architecture (Phase 21 aligned)
- MCP-FIRST exposure for all operations
- Cross-orchestrator integration with 7 operational orchestrators
- Full audit trail (AC markers) for governance compliance

---

## MCP Tools

### cortex_generate_dashboard

Generates dashboard JSON for a repository with full metrics.

**Endpoint:** `/tools/cortex_generate_dashboard`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repo_path` | string | Yes | Path to repository (e.g., "cortex", "alist") |
| `output_format` | string | No | Output format: "json" (default) or "html" |
| `force_regenerate` | boolean | No | Bypass cache and regenerate (default: false) |

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "repo_path": {"type": "string"},
    "output_format": {"type": "string", "enum": ["json", "html"]},
    "force_regenerate": {"type": "boolean"}
  },
  "required": ["repo_path"]
}
```

**Output Schema:**
```json
{
  "type": "object",
  "properties": {
    "schema_version": {"type": "string"},
    "generated_at": {"type": "string", "format": "date-time"},
    "repository": {"type": "string"},
    "overview": {"type": "object"},
    "metrics": {"type": "object"},
    "security": {"type": "object"},
    "health": {"type": "object"}
  },
  "required": ["schema_version", "repository", "overview"]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/tools/cortex_generate_dashboard \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "cortex",
    "output_format": "json",
    "force_regenerate": false
  }'
```

**Example Response:**
```json
{
  "schema_version": "1.0",
  "generated_at": "2025-02-08T12:00:00Z",
  "repository": "cortex",
  "type": "core-platform",
  "overview": {
    "description": "Core platform",
    "stats": {
      "files": 7776,
      "size_mb": 67,
      "loc": 45000
    }
  },
  "metrics": {
    "test_coverage": 89,
    "build_status": "passing"
  }
}
```

---

### cortex_sync_dashboard_data

Synchronizes dashboard data with latest repository metrics.

**Endpoint:** `/tools/cortex_sync_dashboard_data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `repo_name` | string | Yes | Repository name |
| `sync_timeout` | integer | No | Sync timeout in seconds (default: 30) |

**Example:**
```bash
curl -X POST http://localhost:8000/tools/cortex_sync_dashboard_data \
  -H "Content-Type: application/json" \
  -d '{
    "repo_name": "cortex",
    "sync_timeout": 30
  }'
```

---

## Integration Points

The DashboardOrchestrator integrates with **7 operational orchestrators**:

### 1. **MasterOrchestrator**
- **Role:** Governance gate for dashboard generation
- **Action:** Routes dashboard requests through security validation
- **Trigger:** Any dashboard generation request
- **Output:** Validated dashboard JSON

### 2. **PlanningOrchestrator**
- **Role:** Artifact registration
- **Action:** Registers generated dashboard as deployment artifact
- **Trigger:** Successful dashboard generation
- **Output:** Dashboard artifact metadata

### 3. **InteractionOrchestrator**
- **Role:** Action discovery
- **Action:** Lists dashboard generation as available action
- **Trigger:** User queries available actions
- **Output:** Action metadata in action list

### 4. **RepositoryOnboardingOrchestrator**
- **Role:** Auto-generation on onboarding
- **Action:** Automatically generates dashboard when repo onboarded
- **Trigger:** Repository onboarding completion
- **Output:** Onboarded repository with dashboard

### 5. **RefactoringOrchestrator**
- **Role:** Post-refactor regeneration
- **Action:** Regenerates dashboard after major refactoring
- **Trigger:** Refactoring completion
- **Output:** Updated dashboard reflecting refactoring changes

### 6. **RecommendationGate**
- **Role:** Metrics evidence source
- **Action:** Uses dashboard metrics as evidence for recommendations
- **Trigger:** Recommendation generation
- **Output:** Evidence-backed recommendations

### 7. **TDDOrchestrator**
- **Role:** Test suite integration
- **Action:** Adds dashboard generation to TDD test suite
- **Trigger:** TDD test execution
- **Output:** Dashboard test coverage metrics

---

## Usage Examples

### Python API

```python
from cortex.orchestrators.domain.dashboard_orchestrator import get_dashboard_orchestrator

# Get singleton instance
orchestrator = get_dashboard_orchestrator()

# Generate dashboard for cortex repository
dashboard_json = orchestrator.generate_dashboard("cortex")

print(f"Generated dashboard for {dashboard_json['repository']}")
print(f"Schema version: {dashboard_json['schema_version']}")

# Access metrics
metrics = dashboard_json.get("metrics", {})
print(f"Test coverage: {metrics.get('test_coverage', 'N/A')}%")

# Sync with latest data
updated_dashboard = orchestrator.sync_dashboard_data("cortex")
print(f"Updated at: {updated_dashboard['generated_at']}")
```

### MCP Tool Integration

```python
from cortex.mcp.gateway import get_mcp_gateway

# Get MCP gateway
gateway = get_mcp_gateway()

# Call MCP tool
result = gateway.call_tool(
    "cortex_generate_dashboard",
    {
        "repo_path": "cortex",
        "output_format": "json"
    }
)

print(result)
```

### Command Line

```bash
# Generate dashboard via CLI
python -m cortex.orchestrators.domain.dashboard_orchestrator cortex

# List available dashboards
python -m cortex.orchestrators.domain.dashboard_orchestrator --list

# Sync all dashboards
python -m cortex.orchestrators.domain.dashboard_orchestrator --sync-all
```

---

## Caching & Performance

### Cache Configuration

- **Default TTL:** 5 minutes (300 seconds)
- **Strategy:** In-memory + file-based
- **Location:** `company/dashboards/data/`

### Cache Management

```python
orchestrator = get_dashboard_orchestrator()

# Check cache status
cache_status = orchestrator.get_cache_status()
print(f"Cached repos: {len(cache_status['cached_repos'])}")
print(f"Cache size: {cache_status['total_size_kb']}KB")

# Clear specific repo cache
orchestrator.clear_cache("cortex")

# Clear all caches
orchestrator.clear_cache()

# Force regeneration (bypass cache)
orchestrator.generate_dashboard("cortex", force=True)
```

---

## Architecture

### Schema Version

**Current:** 1.0

Dashboard JSON follows strict schema with required fields:

```json
{
  "schema_version": "1.0",
  "generated_at": "ISO-8601 timestamp",
  "repository": "repository name",
  "type": "repository type",
  "overview": {
    "description": "string",
    "stats": {}
  },
  "metadata": {
    "migrated_from": "legacy file path",
    "migration_timestamp": "ISO-8601"
  },
  "metrics": {},
  "security": {},
  "health": {},
  "recommendations": {}
}
```

### Supported Repository Types

- `core-platform` - Core CORTEX platform
- `domain-service` - Domain-specific service
- `tool-service` - Tool or utility service
- `file-management-service` - File management
- `web-application` - Web application
- `session-management` - Session/auth service
- `graphics-engine` - Graphics/rendering engine

---

## Troubleshooting

### Dashboard Not Generated

**Symptoms:** Empty response or null dashboard

**Solutions:**
1. Verify repository path exists: `ls -la company/dashboards/data/`
2. Check cache: `orchestrator.get_cache_status()`
3. Force regeneration: `orchestrator.generate_dashboard(repo, force=True)`
4. Check logs: `tail -f logs/dashboard_orchestrator.log`

### Performance Issues

**Symptoms:** Slow dashboard generation (>5 seconds)

**Solutions:**
1. Check cache hits: `orchestrator.get_cache_status()`
2. Enable caching: Ensure `cache_ttl_seconds > 0`
3. Monitor metrics: Check Prometheus metrics `cortex_dashboard_generation_seconds`
4. Profile: Enable debug logging `LOG_LEVEL=DEBUG`

### Schema Validation Errors

**Symptoms:** "Schema validation failed" error

**Solutions:**
1. Check required fields are present
2. Verify data types match schema
3. Validate JSON: `python -m json.tool < dashboard.json`
4. Compare with schema: `cortex/mcp/tools/dashboard_tools_spec.yaml`

### Integration Failures

**Symptoms:** Dashboard not appearing in other orchestrators

**Solutions:**
1. Verify DashboardIntegrationMixin is registered
2. Check orchestrator logs for errors
3. Verify MCP tool registration: `GET /tools/cortex_generate_dashboard`
4. Test MCP tool directly: `curl http://localhost:8000/tools`

---

## Monitoring

### Prometheus Metrics

- `cortex_dashboard_generation_seconds` - Generation time histogram
- `cortex_dashboard_generations_total` - Total generations counter
- `cortex_dashboard_cache_hits_total` - Cache hits counter
- `cortex_dashboard_validation_errors_total` - Validation errors counter

### Health Check

```bash
curl http://localhost:8000/health/dashboard-orchestrator
```

Expected response:
```json
{
  "status": "healthy",
  "orchestrator": "DashboardOrchestrator",
  "mcp_tools": 2,
  "cache_enabled": true,
  "cache_ttl_seconds": 300,
  "integrations": 7
}
```

---

## Audit Trail

All dashboard operations include AC markers for governance compliance:

```python
# AC_START: AC-PHASE53.0-DASHBOARD-GEN-001
dashboard = orchestrator.generate_dashboard("cortex")
# AC_COMPLETE: AC-PHASE53.0-DASHBOARD-GEN-001 ✅
```

---

## Migration Notes

**Migrated From:** 5 legacy dashboard SPAs
- `company/dashboards/repos/alist/index.html`
- `company/dashboards/repos/cortex/index.html`
- `company/dashboards/repos/kashkole/index.html`
- `company/dashboards/repos/ksessions/index.html`
- `company/dashboards/repos/noor-canvas/index.html`

**Migrated To:** Unified SPA
- `company/dashboards/spa/index.html`
- `company/dashboards/spa/app.js`
- `company/dashboards/spa/css/dashboard.css`
- `company/dashboards/data/*.json` (5 repository datasets)

**Benefits:**
- ✅ 68% size reduction
- ✅ Zero SQL dependencies (Phase 21 aligned)
- ✅ Cross-orchestrator integration
- ✅ MCP-FIRST exposure
- ✅ Full governance compliance

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-02-08 | Initial release - Phase 53 completion |

