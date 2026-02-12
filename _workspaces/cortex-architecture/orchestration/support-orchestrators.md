# Support Orchestrators

**Purpose:** Documentation of support and infrastructure orchestrators  
**Audience:** Developers, Operations  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [OnboardingOrchestrator](#onboardingorchestrator)
- [ToolDiscoveryOrchestrator](#tooldiscoveryorchestrator)
- [UpgradeOrchestrator](#upgradeorchestrator)
- [RollbackOrchestrator](#rollbackorchestrator)
- [DiagnosticsOrchestrator](#diagnosticsorchestrator)
- [CacheOrchestrator](#cacheorchestrator)
- [HealthOrchestrator](#healthorchestrator)
- [Related Documents](#related-documents)

---

## Overview

Support orchestrators provide auxiliary functions that enable smooth CORTEX operations. They handle infrastructure, maintenance, and operational concerns.

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| OnboardingOrchestrator | 110 | Repository setup |
| ToolDiscoveryOrchestrator | 120 | Tool catalog |
| UpgradeOrchestrator | 130 | Version upgrades |
| RollbackOrchestrator | 140 | Version rollbacks |
| DiagnosticsOrchestrator | 150 | System diagnostics |
| CacheOrchestrator | 160 | Cache management |
| HealthOrchestrator | 170 | Health monitoring |

---

## OnboardingOrchestrator

### Purpose

Handles repository onboarding, including project analysis, security scanning, and initial configuration.

### Capabilities

- **Project Analysis** — Detect project type, frameworks
- **Security Scan** — Initial vulnerability assessment
- **Configuration** — Generate CORTEX config
- **Knowledge Extraction** — Extract domain knowledge

### Onboarding Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  ONBOARDING WORKFLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. SCAN: Project structure analysis                            │
│     ├── Language detection                                      │
│     ├── Framework identification                                │
│     └── Dependency analysis                                     │
│                                                                  │
│  2. SECURITY: Vulnerability assessment                          │
│     ├── Dependency vulnerabilities                              │
│     ├── Secrets detection                                       │
│     └── OWASP compliance check                                  │
│                                                                  │
│  3. CONFIGURE: CORTEX setup                                     │
│     ├── Generate .cortex config                                 │
│     ├── Setup MCP integration                                   │
│     └── Configure git hooks                                     │
│                                                                  │
│  4. EXTRACT: Knowledge extraction                               │
│     ├── API patterns                                            │
│     ├── Domain terminology                                      │
│     └── Coding conventions                                      │
│                                                                  │
│  5. REPORT: Onboarding summary                                  │
│     ├── Health score                                            │
│     ├── Security findings                                       │
│     └── Recommendations                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### MCP Tool

```python
# cortex_onboard_repository
{
    "name": "cortex_onboard_repository",
    "description": "Onboard a new repository to CORTEX",
    "parameters": {
        "path": "Repository path",
        "scan_security": "Run security scan (default: true)",
        "extract_knowledge": "Extract domain knowledge (default: true)"
    }
}
```

---

## ToolDiscoveryOrchestrator

### Purpose

Manages the MCP tool catalog, enabling discovery and documentation of available tools.

### Capabilities

- **Catalog Management** — Maintain tool registry
- **Search** — Find tools by capability
- **Documentation** — Tool usage guides
- **Versioning** — Track tool versions

### Tool Catalog Structure

```python
@dataclass
class ToolCatalogEntry:
    """Entry in the tool catalog."""
    
    name: str
    category: ToolCategory
    description: str
    parameters: List[ToolParameter]
    examples: List[ToolExample]
    version: str
    deprecated: bool = False
    replacement: Optional[str] = None
```

### Discovery API

```python
async def discover_tools(
    self,
    category: Optional[ToolCategory] = None,
    capability: Optional[str] = None
) -> List[ToolCatalogEntry]:
    """
    Discover tools matching criteria.
    
    Args:
        category: Filter by category
        capability: Filter by capability keyword
    
    Returns:
        Matching tool entries
    """
    tools = self.catalog.list_all()
    
    if category:
        tools = [t for t in tools if t.category == category]
    
    if capability:
        tools = [
            t for t in tools
            if capability.lower() in t.description.lower()
        ]
    
    return tools
```

---

## UpgradeOrchestrator

### Purpose

Manages CORTEX version upgrades, including migration and compatibility checks.

### Capabilities

- **Version Check** — Detect available upgrades
- **Compatibility** — Assess upgrade impact
- **Migration** — Execute upgrade steps
- **Validation** — Verify upgrade success

### Upgrade Process

```python
async def execute_upgrade(
    self,
    target_version: str
) -> UpgradeResult:
    """
    Execute CORTEX upgrade.
    """
    current = self.get_current_version()
    
    # Check compatibility
    compatibility = await self.check_compatibility(
        current,
        target_version
    )
    
    if not compatibility.compatible:
        return UpgradeResult(
            success=False,
            error=f"Incompatible upgrade: {compatibility.reason}"
        )
    
    # Create backup
    backup = await self.create_backup()
    
    try:
        # Execute migration steps
        for step in compatibility.migration_steps:
            await self.execute_step(step)
        
        # Validate upgrade
        validation = await self.validate_upgrade(target_version)
        
        if not validation.success:
            await self.restore_backup(backup)
            return UpgradeResult(
                success=False,
                error=validation.error
            )
        
        return UpgradeResult(
            success=True,
            from_version=current,
            to_version=target_version,
            steps_executed=len(compatibility.migration_steps)
        )
        
    except Exception as e:
        await self.restore_backup(backup)
        raise
```

---

## RollbackOrchestrator

### Purpose

Handles version rollbacks when upgrades fail or issues are discovered.

### Capabilities

- **Backup Management** — Track rollback points
- **Safe Rollback** — Execute rollback safely
- **Data Preservation** — Protect user data
- **Validation** — Verify rollback success

### Rollback Strategy

```python
class RollbackStrategy(Enum):
    """Rollback strategies."""
    
    FULL = "full"           # Complete rollback to previous version
    PARTIAL = "partial"     # Rollback specific components
    CONFIG_ONLY = "config"  # Rollback configuration only
    DATA_PRESERVE = "data"  # Rollback code, preserve data
```

---

## DiagnosticsOrchestrator

### Purpose

Provides system diagnostics and debugging capabilities.

### Capabilities

- **Health Check** — System health assessment
- **Log Analysis** — Parse and analyze logs
- **Performance Profiling** — Identify bottlenecks
- **Debug Injection** — Insert debug markers

### Diagnostic Commands

```python
# Debug injection for troubleshooting
DIAGNOSTIC_COMMANDS = {
    "/debug {path}": "Full debug cycle",
    "/debug-cleanup": "Remove debug markers",
    "/diagnose": "System health check",
    "/profile": "Performance profiling",
    "/logs": "Recent log analysis",
}
```

### Debug Marker Injection

```python
async def inject_debug_markers(
    self,
    target_file: str
) -> InjectionResult:
    """
    Inject CORTEX_DEBUG markers for troubleshooting.
    """
    content = await self.read_file(target_file)
    
    # Identify injection points
    points = self.identify_injection_points(content)
    
    # Inject markers
    for point in points:
        content = self.inject_at_point(content, point, "CORTEX_DEBUG")
    
    await self.write_file(target_file, content)
    
    return InjectionResult(
        file=target_file,
        markers_injected=len(points)
    )
```

---

## CacheOrchestrator

### Purpose

Manages CORTEX caching layers for performance optimization.

### Capabilities

- **LENS Cache** — Cache LENS analysis results
- **Knowledge Cache** — Cache knowledge queries
- **Invalidation** — Smart cache invalidation
- **Warming** — Proactive cache warming

### Cache Layers

| Layer | TTL | Purpose |
|-------|-----|---------|
| **L1: Request** | 1min | Same-request deduplication |
| **L2: Session** | 1hr | Session-scoped caching |
| **L3: Workspace** | 24hr | Workspace-scoped caching |
| **L4: Global** | 7d | Cross-workspace caching |

### Cache Operations

```python
async def manage_cache(
    self,
    operation: CacheOperation,
    layer: Optional[CacheLayer] = None,
    key: Optional[str] = None
) -> CacheResult:
    """
    Manage cache operations.
    """
    if operation == CacheOperation.CLEAR:
        if layer:
            return await self._clear_layer(layer)
        return await self._clear_all()
    
    if operation == CacheOperation.WARM:
        return await self._warm_cache(layer or CacheLayer.WORKSPACE)
    
    if operation == CacheOperation.STATS:
        return await self._get_stats()
    
    if operation == CacheOperation.INVALIDATE:
        return await self._invalidate_key(key)
```

---

## HealthOrchestrator

### Purpose

Monitors CORTEX system health and provides health endpoints.

### Capabilities

- **Liveness** — System alive check
- **Readiness** — System ready for requests
- **Dependency Health** — External service status
- **Metrics** — Health metrics collection

### Health Endpoints

```python
# Health endpoint responses
HEALTH_ENDPOINTS = {
    "/health": "Basic liveness check",
    "/health/ready": "Readiness probe",
    "/health/wiring": "Wiring contract status",
    "/health/orchestrators": "Orchestrator status",
    "/health/dependencies": "External dependencies",
}
```

### Health Check Implementation

```python
async def check_health(self) -> HealthStatus:
    """
    Comprehensive health check.
    """
    checks = {}
    
    # Core components
    checks["mcp_server"] = await self._check_mcp()
    checks["wiring_contract"] = await self._check_wiring()
    checks["orchestrators"] = await self._check_orchestrators()
    
    # External dependencies
    checks["database"] = await self._check_database()
    checks["cache"] = await self._check_cache()
    
    # Calculate overall status
    all_healthy = all(c.healthy for c in checks.values())
    
    return HealthStatus(
        healthy=all_healthy,
        checks=checks,
        timestamp=datetime.utcnow()
    )
```

### Health Metrics

| Metric | Type | Labels |
|--------|------|--------|
| `cortex_health_check_total` | Counter | component, status |
| `cortex_health_check_duration` | Histogram | component |
| `cortex_component_up` | Gauge | component |

---

## Orchestrator Coordination

### Support Orchestrator Triggers

| Trigger | Orchestrator | Automatic |
|---------|--------------|-----------|
| New repository | OnboardingOrchestrator | Yes |
| Version mismatch | UpgradeOrchestrator | Prompt |
| Health failure | DiagnosticsOrchestrator | Yes |
| Cache miss rate > 50% | CacheOrchestrator | Yes |
| Tool query | ToolDiscoveryOrchestrator | Yes |

### Priority Resolution

```python
def resolve_support_priority(
    orchestrators: List[SupportOrchestrator],
    context: OperationContext
) -> List[SupportOrchestrator]:
    """
    Order support orchestrators by priority.
    
    Lower priority number = higher precedence.
    """
    return sorted(
        orchestrators,
        key=lambda o: o.priority
    )
```

---

## Related Documents

- [Orchestration Overview](overview.md) — Architecture
- [Domain Orchestrators](domain-orchestrators.md) — Domain functions
- [Infrastructure Overview](../infrastructure/overview.md) — Infrastructure

---

*Part of CORTEX Architecture Documentation*
