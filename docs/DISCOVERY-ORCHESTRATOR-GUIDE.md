# Discovery Orchestrator - Quick Start Guide

**Version:** 1.0  
**Status:** Production-Ready ✅  
**Phase:** 9 - Discovery Orchestrator  
**Authority:** PHASE-9-IMPLEMENTATION-TRUTH.md

---

## 🎯 What is Discovery Orchestrator?

DiscoveryOrchestrator provides **automated infrastructure topology discovery** for CORTEX projects, analyzing:

- 🔧 **Configuration Files** - web.config, appsettings.json, docker-compose, etc.
- 🗄️ **Database Connections** - ORMs, connection strings, migrations, schemas
- 🌐 **API Endpoints** - Swagger/OpenAPI, REST, GraphQL, gRPC
- 🏗️ **Microservices** - Service mesh, API gateways, message brokers
- 🧪 **Testing Frameworks** - pytest, Jest, coverage configs
- 🔒 **Security/Monitoring** - Auth, logging, APM

---

## 🚀 Quick Start

### Python API

```python
from pathlib import Path
from cortex.orchestrators.support.discovery_orchestrator import (
    DiscoveryOrchestrator,
    DiscoveryType,
    get_discovery_orchestrator,
)

# Initialize orchestrator
repo_path = Path("/path/to/your/project")
orchestrator = DiscoveryOrchestrator(
    repo_path=repo_path,
    enable_cache=True,        # Enable result caching
    parallel_execution=True,  # Run parsers in parallel
    max_workers=4,            # Parallel worker threads
)

# Discover complete topology (all registered plugins)
topology = orchestrator.discover_topology()

# Access discoveries
print(f"Databases: {topology.databases}")
print(f"APIs: {topology.apis}")
print(f"Config: {topology.config}")
print(f"Microservices: {topology.microservices}")

# Discover specific type only
db_config = orchestrator.discover_by_type(DiscoveryType.DATABASE)
print(f"Database connections: {db_config}")

# Cache management
orchestrator.invalidate_cache()  # Force re-discovery
cache_stats = orchestrator.get_cache_stats()
print(f"Cache stats: {cache_stats}")
```

### Factory Function

```python
from cortex.orchestrators.support.discovery_orchestrator import get_discovery_orchestrator

# Simplified creation
orchestrator = get_discovery_orchestrator(
    repo_path=Path("/my/repo"),
    enable_cache=False,  # Disable caching
)

topology = orchestrator.discover_topology()
```

---

## 🔌 Plugin Architecture

### Available Discovery Types

```python
class DiscoveryType(Enum):
    CONFIG = "config"              # Configuration files
    DATABASE = "database"          # Database connections
    API = "api"                    # API endpoints
    MICROSERVICES = "microservices"  # Microservices topology
    TESTING = "testing"            # Testing frameworks
    SECURITY = "security"          # Security/monitoring
    LENS = "lens"                  # LENS code analysis
```

### Registering Custom Plugins

```python
from cortex.brain.discovery import DiscoveryPlugin

class CustomDiscoveryPlugin(DiscoveryPlugin):
    """Custom discovery plugin example."""
    
    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """Implement your discovery logic."""
        # Your parsing logic here
        return {
            "entities": [],
            "metadata": {},
        }

# Register plugin
orchestrator.register_plugin(DiscoveryType.CONFIG, CustomDiscoveryPlugin())
```

---

## 📊 Topology Map Structure

```python
@dataclass
class TopologyMap:
    """Unified infrastructure topology map."""
    
    config: Dict[str, Any] = field(default_factory=dict)
    databases: Dict[str, Any] = field(default_factory=dict)
    apis: Dict[str, Any] = field(default_factory=dict)
    microservices: Dict[str, Any] = field(default_factory=dict)
    testing: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

Example output:

```python
{
    "config": {
        "files_found": ["appsettings.json", "web.config"],
        "database_connections": 3,
        "api_endpoints": 15,
    },
    "databases": {
        "connections": [
            {
                "type": "PostgreSQL",
                "connection_string": "Host=localhost;Database=cortex;",
                "orm": "Entity Framework",
            }
        ],
    },
    "apis": {
        "endpoints": [
            {"path": "/api/users", "method": "GET", "auth": "JWT"},
            {"path": "/api/users", "method": "POST", "auth": "JWT"},
        ],
        "swagger": "/swagger/v1/swagger.json",
    },
    "metadata": {
        "discovery_time_ms": 150.5,
        "cache_hit": false,
        "plugins_run": 7,
        "repo_path": "/path/to/repo",
    },
}
```

---

## ⚡ Performance Features

### Caching

```python
# Enable memory caching (default)
orchestrator = DiscoveryOrchestrator(
    repo_path=repo_path,
    enable_cache=True,
)

# First call - discovers everything
topology1 = orchestrator.discover_topology()  # ~150ms

# Second call - returns cached result
topology2 = orchestrator.discover_topology()  # ~1ms (cache hit)

# Invalidate cache when configs change
orchestrator.invalidate_cache(file_patterns=["*.json", "*.yaml"])
```

### Parallel Execution

```python
# Enable parallel plugin execution (default)
orchestrator = DiscoveryOrchestrator(
    repo_path=repo_path,
    parallel_execution=True,  # Run plugins concurrently
    max_workers=4,            # Up to 4 threads
)

# Plugins run in parallel - faster discovery
topology = orchestrator.discover_topology()
```

### Selective Discovery

```python
# Discover only specific types (faster)
db_only = orchestrator.discover_by_type(DiscoveryType.DATABASE)
api_only = orchestrator.discover_by_type(DiscoveryType.API)

# No need to run all plugins if you only need one type
```

---

## 🧪 Testing

### Unit Tests

```python
# Location: tests/unit/orchestrators/support/test_discovery_orchestrator.py
# 15 tests, 100% passing

# Run Phase 9 tests
pytest tests/unit/orchestrators/support/test_discovery_orchestrator.py -v
```

### Integration Tests

```python
# Location: tests/integration/brain/discovery/test_discovery_integration.py
# 8 tests, 100% passing

# Run integration tests
pytest tests/integration/brain/discovery/ -v
```

### Test Coverage

```bash
# Run with coverage
pytest tests/unit/orchestrators/support/test_discovery_orchestrator.py --cov=cortex.orchestrators.support.discovery_orchestrator --cov-report=html
```

---

## 🔍 LENS Integration

The Discovery Orchestrator integrates with LENS (Phase 7.1) for verification:

```python
from cortex.brain.discovery.lens_integration import LENSDiscoveryIntegration

# LENS-powered verification
lens_discovery = LENSDiscoveryIntegration(repo_path=Path("/my/repo"))
verified_topology = lens_discovery.discover_and_verify()

# Combines discovery results with LENS code analysis:
# - Git history patterns
# - AST complexity analysis  
# - Comment hints (TODO/FIXME)
# - Validates implementation truth (CORE-030)
```

---

## 📖 Advanced Usage

### Error Handling

```python
# Plugins are isolated - failures don't crash others
try:
    topology = orchestrator.discover_topology()
except Exception as e:
    # Handle errors
    logger.error(f"Discovery failed: {e}")

# Check individual plugin results
for discovery_type, result in topology.metadata.get("plugin_results", {}).items():
    if not result.success:
        logger.warning(f"{discovery_type} failed: {result.error}")
```

### Audit Logging

```python
# Automatic audit trail (CORE-027)
# AC_START logged at discovery start
# AC_COMPLETE logged at discovery end

# Check audit logs
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

audit_logger = EnhancedAuditLogger()
logs = audit_logger.get_logs(ac_id="DISC-001")
```

### Cache Statistics

```python
# Monitor cache performance
stats = orchestrator.get_cache_stats()

print(f"Cache enabled: {stats['cache_enabled']}")
print(f"Cache size: {stats['cache_size']}")
print(f"Cached repos: {stats['cached_repos']}")
```

---

## 🎓 Extension Guide

### Creating a Custom Parser

```python
from pathlib import Path
from typing import Dict, Any
from cortex.brain.discovery import DiscoveryPlugin

class CustomConfigParser(DiscoveryPlugin):
    """
    Custom parser for proprietary config files.
    
    Example: Parse .env files
    """
    
    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """
        Discover .env files and extract configuration.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with discovered config data
        """
        env_files = list(repo_path.rglob(".env*"))
        
        config_data = {
            "env_files_found": len(env_files),
            "variables": [],
        }
        
        for env_file in env_files:
            with open(env_file) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        config_data["variables"].append({
                            "key": key,
                            "file": str(env_file),
                        })
        
        return config_data


# Register and use
orchestrator = get_discovery_orchestrator(repo_path=Path("/my/repo"))
orchestrator.register_plugin(DiscoveryType.CONFIG, CustomConfigParser())

topology = orchestrator.discover_topology()
print(topology.config)  # Includes your custom .env parsing
```

---

## 📚 Available Parsers

All parsers located in `cortex/brain/discovery/`:

| Parser | File | Description |
|--------|------|-------------|
| **ConfigDiscovery** | `config_discovery.py` | Web.config, appsettings.json, docker-compose |
| **DatabaseDiscovery** | `database_discovery.py` | Connection strings, ORMs, migrations |
| **APIDiscovery** | `api_discovery.py` | Swagger, REST, GraphQL, gRPC |
| **MicroservicesDiscovery** | `microservices_discovery.py` | Service mesh, API gateways |
| **TestingDiscovery** | `testing_discovery.py` | pytest, Jest, coverage configs |
| **SecurityDiscovery** | `security_discovery.py` | Auth, logging, APM |
| **LENSIntegration** | `lens_integration.py` | LENS-powered verification |

---

## 🚦 Production Deployment

### Docker Integration

```python
# In your Docker container
from cortex.orchestrators.support.discovery_orchestrator import get_discovery_orchestrator

orchestrator = get_discovery_orchestrator(
    repo_path=Path("/app"),  # Mounted volume
    enable_cache=True,
    parallel_execution=True,
)

# Discover on container startup
topology = orchestrator.discover_topology()

# Expose via API
@app.get("/topology")
def get_topology():
    return topology
```

### Health Checks

```python
# Verify discovery system health
def health_check():
    try:
        orchestrator = get_discovery_orchestrator(repo_path=Path("."))
        topology = orchestrator.discover_topology()
        return {
            "status": "healthy",
            "plugins": len(orchestrator.plugins),
            "cache_enabled": orchestrator.cache_enabled,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
```

---

## 📊 Metrics & Monitoring

```python
# Track discovery performance
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

audit_logger = EnhancedAuditLogger()

# Discovery timing
topology = orchestrator.discover_topology()
discovery_time = topology.metadata["discovery_time_ms"]

# Log to monitoring
audit_logger.log_metric(
    metric_name="discovery_time_ms",
    value=discovery_time,
    tags={"repo": str(repo_path), "cache_hit": topology.metadata["cache_hit"]},
)
```

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Verify imports work
python3 -c "from cortex.orchestrators.support.discovery_orchestrator import DiscoveryOrchestrator; print('✅ Imports OK')"
```

### Plugin Not Running

```python
# Check plugin registration
print(orchestrator.plugins.keys())  # Should show registered types

# Verify plugin implements DiscoveryPlugin
from cortex.brain.discovery import DiscoveryPlugin
isinstance(my_plugin, DiscoveryPlugin)  # Should be True
```

### Cache Issues

```python
# Clear cache if stale
orchestrator.invalidate_cache()

# Disable cache for debugging
orchestrator = DiscoveryOrchestrator(
    repo_path=repo_path,
    enable_cache=False,  # Always re-discover
)
```

---

## 📖 References

- **Implementation:** `cortex/orchestrators/support/discovery_orchestrator.py` (441 lines)
- **Parsers:** `cortex/brain/discovery/*.py` (10 files, 3,750 lines)
- **Tests:** `tests/unit/orchestrators/support/test_discovery_orchestrator.py` (15 tests)
- **Integration Tests:** `tests/integration/brain/discovery/test_discovery_integration.py` (8 tests)
- **Phase Spec:** `_workspaces/docker-plan/PHASE-9-DISCOVERY-ORCHESTRATOR.yaml`
- **Truth Report:** `_workspaces/docker-plan/PHASE-9-IMPLEMENTATION-TRUTH.md`

---

**Status:** ✅ Production-Ready  
**Version:** 1.0  
**Authority:** PHASE-9-IMPLEMENTATION-TRUTH.md  
**Compliance:** CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings), CORE-030 (Implementation Truth)
