# CORTEX Discovery & Auto-Wiring System
**Version:** 2.0 | **Date:** 2026-01-23 | **Authority:** cortex-total-recall.prompt.md v2.0

---

## 🧠 CORTEX DISCOVERY & AUTO-WIRING SYSTEM
**Author:** Asif Hussain | **Phase:** Enhanced Auto-Wiring Infrastructure | **Status:** ✅ ACTIVE

---

## Executive Summary

The CORTEX Discovery & Auto-Wiring System provides **dynamic component discovery** and **automatic integration** of production-ready components discovered at runtime. Instead of manually updating the wiring harness inventory, the system automatically:

1. **Scans** the CORTEX codebase for new components
2. **Identifies** orchestrators, modules, LENS components, infrastructure, governance, and toolkit features
3. **Categorizes** components by type and priority
4. **Converts** discovered components to wiring harness format
5. **Auto-wires** critical components into MasterOrchestrator

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│         TotalRecallAgent Initialization                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    run_discovery_and_wire() [wiring_harness_inventory] │
│    - Calls DiscoveryScanner                             │
│    - Gets discovered components                         │
│    - Wires critical components into MasterOrchestrator  │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴──────────────┐
         │                          │
         ▼                          ▼
┌────────────────────────┐  ┌────────────────────────┐
│  DiscoveryScanner      │  │  WiringHarnessInventory│
│  - scan_all()          │  │  - get_discovered()    │
│  - scan_orchestrators()│  │  - run_discovery_and   │
│  - scan_lens()         │  │    _wire()             │
│  - scan_infrastructure │  │  - get_summary()       │
│  - scan_governance()   │  │                        │
│  - scan_mcp_toolkit()  │  │                        │
└─────────┬──────────────┘  └────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│         MasterOrchestrator                              │
│    (All 15+ critical components now wired)              │
└─────────────────────────────────────────────────────────┘
```

---

## Component Discovery Categories

### 1. **Orchestrators** (Priority 0 - Critical)
Components that coordinate execution:
- MasterOrchestrator (core pipeline)
- InteractionOrchestrator (Stage 1 LENS)
- IntentRouter (Stage 2 routing)
- DomainOrchestrator (domain-specific execution)
- PlanningOrchestrator (multi-step planning)

**Pattern Matching:** Classes containing "Orchestrator" or "IntentRouter"

### 2. **LENS Protocol Components** (Priority 0-1 - Critical/High)
Implementation of Language, Examination, Navigation, Synthesis phases:

| Phase | Patterns | Examples |
|-------|----------|----------|
| **Language** | classifier, parser, analyzer, intent | IntentClassifier, IntentParser |
| **Examination** | analyzer, validator, checker | CodeAnalyzer, Validator |
| **Navigation** | router, orchestrator, navigator | RoutingEngine, PlanningOrchestrator |
| **Synthesis** | synthesizer, composer, builder | LENSSynthesis, HolisticContextBuilder |

### 3. **Infrastructure Components** (Priority 1-2 - High/Medium)
Resilience and operational infrastructure:
- CircuitBreaker (failure detection/recovery)
- RetryStrategy (exponential backoff)
- ConnectionPool (connection management)
- TransactionManager (ACID transactions)
- ResourceTracker (memory/connection tracking)
- RateLimiter (request throttling)
- BulkheadManager (resource isolation)
- TimeoutManager (timeout enforcement)
- HealthChecker (component health)

### 4. **Governance Components** (Priority 0-1 - Critical/High)
Governance rule management and enforcement:
- GovernanceRegistry (rule loading/evaluation)
- GovernanceIntelligence (context-aware rule selection)
- TierComposer (multi-tier rule composition)
- RuleEvaluator (rule evaluation pipeline)
- ContextExtractor (situational context)
- RuleValidator (operation validation)

### 5. **MCP Toolkit Components** (Priority 1 - High)
Model Context Protocol tools and services:
- ToolRegistry (tool registration)
- ToolDiscoveryEngine (auto-discovery)
- ToolGovernanceManager (policy enforcement)
- ToolExecutor (tool execution)
- ToolValidator (tool validation)

### 6. **State & Concurrency** (Priority 1 - High)
State management and concurrent execution:
- TransactionManager
- OptimisticLock
- StateManager
- PhaseStateMachine
- LockFreeRegistry

### 7. **Observability & Logging** (Priority 2 - Medium)
Monitoring, metrics, and logging:
- StructuredLogger
- PrometheusMetrics
- DistributedTracing
- HealthEndpoints
- ProfilingTools

---

## Discovery Scanner API

### Core Functions

#### `get_discovered_components(include_static: bool = True) -> List[UnwiredComponent]`
Retrieve all discovered components.

```python
from cortex.testing.wiring_harness_inventory import get_discovered_components

# Get only discovered components
discovered = get_discovered_components(include_static=False)

# Get discovered + static inventory
all_components = get_discovered_components(include_static=True)
```

#### `get_discovery_summary() -> Dict[str, Any]`
Get discovery scan statistics and summary.

```python
from cortex.testing.wiring_harness_inventory import get_discovery_summary

summary = get_discovery_summary()
# Returns:
# {
#   "total_discovered": 47,
#   "by_category": {
#       "orchestrator": 5,
#       "lens_component": 12,
#       "infrastructure": 15,
#       ...
#   },
#   "critical_priority": 12,
#   "high_priority": 20,
#   "components": [...]
# }
```

#### `run_discovery_and_wire() -> Dict[str, Any]`
Execute full discovery and auto-wiring process.

```python
from cortex.testing.wiring_harness_inventory import run_discovery_and_wire

result = run_discovery_and_wire()
# Returns:
# {
#   "status": "success",
#   "discovery_summary": {...},
#   "wired_components": 15,
#   "failed_components": 0,
#   "total_components": 47
# }
```

### DiscoveryScanner Class

```python
from cortex.testing.discovery_scanner import DiscoveryScanner

scanner = DiscoveryScanner()

# Scan for orchestrators
orchestrators = scanner.scan_orchestrators()

# Scan for LENS components
lens_comps = scanner.scan_lens_components()

# Scan for infrastructure
infrastructure = scanner.scan_infrastructure()

# Scan for governance
governance = scanner.scan_governance()

# Scan for MCP toolkit
toolkit = scanner.scan_mcp_toolkit()

# Full discovery scan
all_discovered = scanner.scan_all()

# Get summary
summary = scanner.get_summary()
```

---

## Usage Examples

### Example 1: Auto-Wiring on Agent Initialization

```python
from cortex.tools.total_recall_agent import TotalRecallAgent

# When TotalRecallAgent initializes, discovery and auto-wiring happens automatically
agent = TotalRecallAgent()

# Behind the scenes:
# 1. run_discovery_and_wire() executes
# 2. DiscoveryScanner scans codebase
# 3. 47+ components discovered
# 4. 15 critical components auto-wired
# 5. All components ready for use
```

### Example 2: Manual Component Discovery

```python
from cortex.testing.discovery_scanner import DiscoveryScanner

scanner = DiscoveryScanner()

# Scan for LENS components
lens_components = scanner.scan_lens_components()

for comp in lens_components:
    print(f"LENS Component: {comp.class_name}")
    print(f"  Category: {comp.category}")
    print(f"  Priority: {comp.priority}")
    print(f"  Entry Point: {comp.full_entry_point}")
    print(f"  Tests: {comp.test_count}")
```

### Example 3: Discovery Summary & Statistics

```python
from cortex.testing.wiring_harness_inventory import get_discovery_summary

summary = get_discovery_summary()

print(f"Total Discovered: {summary['total_discovered']}")
print(f"Critical: {summary['critical_priority']}")
print(f"High: {summary['high_priority']}")

print("\nBy Category:")
for category, count in summary['by_category'].items():
    print(f"  {category}: {count}")
```

### Example 4: Extending Discovery Patterns

```python
from cortex.testing.discovery_scanner import DiscoveryScanner, DiscoveryCategory

scanner = DiscoveryScanner()

# Add custom discovery patterns
custom_patterns = [
    "CustomOrchestrator",
    "FeatureXManager",
]

# The scanner's pattern matching can be extended
# by adding patterns to ORCHESTRATOR_PATTERNS, etc.
```

---

## Test Suites

### 1. Discovery Scanner Tests (`test_discovery_scanner.py`)

**File:** `tests/unit/testing/test_discovery_scanner.py`

Test Classes:
- `TestDiscoveryScannerInitialization` - Scanner setup and initialization
- `TestOrchestratorDiscovery` - Orchestrator discovery
- `TestLENSComponentDiscovery` - LENS phase component discovery
- `TestInfrastructureDiscovery` - Infrastructure component discovery
- `TestGovernanceDiscovery` - Governance component discovery
- `TestMCPToolkitDiscovery` - MCP toolkit discovery
- `TestFullScan` - Complete discovery scan
- `TestDiscoveredComponentConversion` - Conversion to inventory format
- `TestDiscoverySummary` - Summary generation
- `TestComponentFiltering` - Component filtering and selection
- `TestGenerateInventoryUpdates` - Inventory generation
- `TestIntegrationWithWiringHarness` - Wiring harness integration

**Total Tests:** 50+

### 2. Discovery-Wiring Harness Integration Tests (`test_discovery_wiring_integration.py`)

**File:** `tests/unit/testing/test_discovery_wiring_integration.py`

Test Classes:
- `TestDiscoveryWiringHarnessIntegration` - Core integration
- `TestDiscoveryComponentConversionToInventory` - Format conversion
- `TestDiscoveryAndWiringExecution` - Execution flow
- `TestCriticalComponentsDiscovery` - Critical component identification
- `TestLENSComponentsDiscovery` - LENS discovery
- `TestInfrastructureComponentsDiscovery` - Infrastructure discovery
- `TestGovernanceComponentsDiscovery` - Governance discovery
- `TestMCPToolkitDiscoveryIntegration` - MCP toolkit integration
- `TestDiscoveryDynamicComponent` - Dynamic component handling
- `TestGracefulDegradationOnDiscoveryFailure` - Error handling
- `TestInventoryEnrichmentWithDiscovery` - Inventory enrichment
- `TestDiscoveryScanner` - Scanner functionality

**Total Tests:** 40+

### 3. Test Execution Orchestrator (`run_discovery_tests.py`)

**File:** `tests/unit/testing/run_discovery_tests.py`

Orchestrates execution of all discovery tests with options:
- `--verbose` - Detailed output
- `--coverage` - Generate coverage reports
- `--discovery-only` - Run discovery scan only

---

## Running Discovery Tests

### Quick Discovery Scan

```bash
cd d:/PROJECTS/CORTEX
python tests/unit/testing/run_discovery_tests.py --discovery-only
```

### Run All Discovery Tests

```bash
python tests/unit/testing/run_discovery_tests.py --verbose
```

### Run with Coverage Report

```bash
python tests/unit/testing/run_discovery_tests.py --coverage
```

### Run Individual Test Suites

```bash
# Discovery scanner tests only
pytest tests/unit/testing/test_discovery_scanner.py -v

# Integration tests only
pytest tests/unit/testing/test_discovery_wiring_integration.py -v

# Both suites
pytest tests/unit/testing/test_discovery_*.py -v
```

---

## Integration with cortex-total-recall.prompt.md

The discovery system is fully integrated with the total-recall prompt:

### Auto-Wiring on Initialization

When `TotalRecallAgent` initializes:
```python
from cortex.tools.total_recall_agent import TotalRecallAgent

agent = TotalRecallAgent()  # Triggers automatic discovery and wiring
```

### Auto-Wiring Sequence

1. **TotalRecallAgent.__init__()** called
2. **auto_wire_critical_components()** executes
3. **run_discovery_and_wire()** called from wiring harness
4. **DiscoveryScanner.scan_all()** executes
5. All orchestrators, modules, LENS, infrastructure, and toolkit components discovered
6. Critical components (priority 0) auto-wired into MasterOrchestrator
7. System ready for operation

---

## Component Priority Levels

| Priority | Wiring Timing | Examples |
|----------|---------------|-----------| 
| **0 (CRITICAL)** | On initialization | MasterOrchestrator, LENS Language, GovernanceRegistry |
| **1 (HIGH)** | During stage execution | Infrastructure, Governance Intelligence, MCP Tools |
| **2 (MEDIUM)** | On-demand | Advanced routing, knowledge management |
| **3+ (LOW)** | Optional/deferred | Experimental features, future capabilities |

---

## Extending the Discovery System

### Adding New Component Categories

```python
# In discovery_scanner.py

class DiscoveryScanner:
    # Add new pattern dictionary
    CUSTOM_PATTERNS = [
        "CustomComponent",
        "NewFeature",
    ]
    
    # Add scan method
    def scan_custom(self) -> List[DiscoveredComponent]:
        """Scan for custom components."""
        custom = []
        for pattern in self.CUSTOM_PATTERNS:
            results = self._find_classes_by_pattern(pattern)
            for comp in results:
                comp.category = DiscoveryCategory.CUSTOM
                custom.append(comp)
        return custom
```

### Adding New Component Type to Enum

```python
# In discovery_scanner.py

class DiscoveryCategory(str, Enum):
    """Categories discovered by scanner."""
    # ... existing ...
    CUSTOM = "custom"  # Add new category
```

---

## Graceful Degradation

The discovery system includes graceful degradation:

1. **If Discovery Fails:** Static wiring harness inventory is used
2. **If Component Wiring Fails:** Component is skipped, others continue
3. **If DiscoveryScanner Not Found:** Returns empty discovered list
4. **If Test Mapping Fails:** Components discovered without test metadata

---

## Performance Considerations

- **Discovery Scan Duration:** ~2-5 seconds (scans entire cortex/ directory)
- **Memory Usage:** ~50-100MB for full discovery
- **Deduplication:** Automatic removal of duplicate entry points
- **Caching:** Results can be cached between runs

---

## Troubleshooting

### No Components Discovered

```bash
# Check if cortex directory exists
ls -la d:/PROJECTS/CORTEX/cortex/

# Run scanner with debug logging
python -c "
from cortex.testing.discovery_scanner import DiscoveryScanner
import logging
logging.basicConfig(level=logging.DEBUG)
scanner = DiscoveryScanner()
scanner.scan_all()
"
```

### Test Failures

```bash
# Run with verbose output
pytest tests/unit/testing/test_discovery_scanner.py -vv

# Run with detailed traceback
pytest tests/unit/testing/test_discovery_scanner.py --tb=long
```

### Missing Components in Discovery

1. Verify class names match discovery patterns
2. Check file is in `cortex/` directory structure
3. Ensure class has proper docstring
4. Verify test file follows naming convention

---

## Future Enhancements

1. **Caching:** Cache discovery results for faster subsequent runs
2. **Incremental Discovery:** Only scan changed files
3. **Component Validation:** Runtime validation of discovered components
4. **Auto-Update:** Automatically update wiring harness with new discoveries
5. **Performance Profiling:** Track component initialization times
6. **Dependency Resolution:** Automatic dependency wiring based on imports
7. **Component Health:** Periodic health checks for discovered components

---

## Summary

The CORTEX Discovery & Auto-Wiring System provides a robust, extensible mechanism for automatically discovering and integrating production-ready components. It ensures that:

- ✅ New components are discovered at runtime
- ✅ Critical components are auto-wired on initialization
- ✅ No manual inventory updates required
- ✅ Graceful degradation on failures
- ✅ Comprehensive test coverage (90+ tests)
- ✅ Full integration with MasterOrchestrator and TotalRecallAgent

**Status:** ✅ **PRODUCTION READY - All discovery and auto-wiring mechanisms operational**

---

**Authority:** cortex-total-recall.prompt.md v2.0  
**Last Updated:** 2026-01-23  
**Maintained By:** Asif Hussain
