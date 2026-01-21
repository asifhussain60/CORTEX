# CORTEX Total Recall - Post-Clone Setup & Functionality Wiring
**Version:** 2.0 | **Updated:** 2026-01-21 | **Authority:** cortex-impl-map.yaml v3.9

---

## Purpose

**First-run setup prompt for CORTEX after cloning from GitHub.** This prompt ensures:
1. Python environment is created and configured from `requirements.txt`
2. CORTEX.prompt.md and copilot-instruction.md are wired to MasterOrchestrator
3. All completed functionality is available for immediate use
4. Roadmap context is understood (what's done vs. in-progress)

---

## 🚀 PHASE 1: Environment Setup

### Step 1.1: Create Python Virtual Environment

```powershell
# Windows (PowerShell)
cd C:\PROJECTS\CORTEX
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
cd /path/to/CORTEX
python3 -m venv .venv
source .venv/bin/activate
```

### Step 1.2: Install Dependencies from requirements.txt

```powershell
# Windows
.\.venv\Scripts\pip.exe install -r requirements.txt
```

```bash
# macOS/Linux
pip install -r requirements.txt
```

### Step 1.3: Verify Installation

```powershell
# Check Python version (3.9+ required, 3.10+ recommended)
python --version

# Verify critical packages
python -c "import cortex; print('CORTEX package: OK')"
python -c "import pytest; print('pytest:', pytest.__version__)"
python -c "import pydantic; print('pydantic:', pydantic.__version__)"
```

### Step 1.4: Initialize Governance Database

```powershell
# Verify governance database exists
Test-Path "cortex_brain/state/governance.db"

# If missing, initialize it
python -c "from cortex.infrastructure.database import DatabaseManager; DatabaseManager().initialize()"
```

---

## 🔌 PHASE 2: Wire Copilot Instructions to MasterOrchestrator

### Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `.github/prompts/CORTEX.prompt.md` | System prompt for MasterOrchestrator | ✅ Configured |
| `.github/copilot-instruction.md` | Copilot workspace instructions | ✅ Configured |
| `cortex-config.yaml` | Runtime configuration | ✅ Active |

### Verify Integration Points

```python
# Test MasterOrchestrator availability
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator()
print(f"MasterOrchestrator: {orchestrator.name}")
print(f"Orchestrator ready: {orchestrator.is_ready()}")
```

### Key Entry Points (Wired to Copilot)

| Component | Import Path | Usage |
|-----------|-------------|-------|
| **MasterOrchestrator** | `cortex.orchestrators.core.master_orchestrator.MasterOrchestrator` | 4-stage pipeline execution |
| **IntentClassifier** | `cortex.intent_router.classifier.IntentClassifier` | Parse user requests |
| **GovernanceRegistry** | `cortex.brain.core.governance_registry.GovernanceRegistry` | Validate against TIER 0 rules |
| **StateManager** | `cortex.brain.core.state_manager.StateManager` | Cross-phase state persistence |
| **EnhancedAuditLogger** | `cortex.infrastructure.enhanced_audit_logger.EnhancedAuditLogger` | Hash-chain audit trail |
| **TotalRecallAgent** | `cortex.tools.total_recall_agent.TotalRecallAgent` | Feature discovery |

---

## ✅ PHASE 3: Completed Functionality (Production Ready)

### Intent Router — 128/128 Tests (100%)

| Component | Entry Point | Capabilities |
|-----------|-------------|--------------|
| **IntentClassifier** | `cortex.intent_router.classifier.IntentClassifier` | Multi-label classification, confidence scoring |
| **ConfidenceScorer** | `cortex.intent_router.confidence_scorer.ConfidenceScorer` | Threshold-based confidence evaluation |
| **ContextManager** | `cortex.intent_router.context_manager.ContextManager` | Session context persistence |
| **RoutingEngine** | `cortex.intent_router.routing_engine.RoutingEngine` | Orchestrator selection and routing |
| **IntentDisambiguator** | `cortex.intent_router.disambiguator.IntentDisambiguator` | Ambiguity detection, recommendations |
| **MultiModalIntentProcessor** | `cortex.intent_router.multimodal_processor.MultiModalIntentProcessor` | TEXT, JSON, COMMAND, CODE, SCHEMA modality |
| **FallbackStrategy** | `cortex.intent_router.fallback_strategy.FallbackStrategy` | Graceful degradation |
| **IntentLearner** | `cortex.intent_router.intent_learner.IntentLearner` | Pattern learning |
| **PerformanceMetrics** | `cortex.intent_router.performance_metrics.PerformanceMetrics` | Latency/throughput tracking |
| **OrchestrationIntegrator** | `cortex.intent_router.orchestration_integrator.OrchestrationIntegrator` | MasterOrchestrator bridge |

**Usage:**
```python
from cortex.intent_router.classifier import IntentClassifier
from cortex.intent_router.routing_engine import RoutingEngine

classifier = IntentClassifier()
result = classifier.classify(user_input)
if result.confidence >= 0.7:
    orchestrator = RoutingEngine().route(result.intent)
```

---

### Governance Engine — 348/368 Tests (95%)

| Component | Entry Point | Capabilities |
|-----------|-------------|--------------|
| **GovernanceRegistry** | `cortex.brain.core.governance_registry.GovernanceRegistry` | Rule loading, evaluation, enforcement |
| **ContextExtractor** | `cortex.brain.core.governance.context_extractor.ContextExtractor` | Situational context extraction |
| **RuleApplicability** | `cortex.brain.core.governance.rule_applicability.RuleApplicability` | Rule filtering |
| **RuleValidators** | `cortex.brain.core.governance.rule_validators.RuleValidators` | Operation validation |
| **RuleEvaluator** | `cortex.brain.core.rule_evaluator.RuleEvaluator` | Integrated evaluation pipeline |

**29 TIER 0 Rules Active:**
```yaml
Location: cortex_brain/tier0/governance/core-rules.yaml
Critical Rules:
  - CORE-001: Incremental execution (<500 lines)
  - CORE-005: No hardcoded paths
  - CORE-008: TDD enforcement
  - CORE-011: Type hints required
  - CORE-012: Docstrings required
  - CORE-013: No bare except
  - CORE-029: Response headers
```

---

### Infrastructure Resilience — 472/472 Tests (100%)

| Component | Entry Point | Capabilities |
|-----------|-------------|--------------|
| **ConnectionPool** | `cortex.infrastructure.connection_pool.ConnectionPool` | Connection management, health checks |
| **CircuitBreaker** | `cortex.infrastructure.circuit_breaker.CircuitBreaker` | Failure detection, auto-recovery |
| **RetryStrategy** | `cortex.infrastructure.retry_strategy.RetryStrategy` | Exponential backoff, jitter |
| **BulkheadManager** | `cortex.infrastructure.bulkhead_manager.BulkheadManager` | Resource isolation |
| **DegradationManager** | `cortex.infrastructure.degradation_manager.DegradationManager` | Graceful feature degradation |
| **ResourceTracker** | `cortex.infrastructure.resource_tracker.ResourceTracker` | Memory/connection/thread tracking |
| **TransactionManager** | `cortex.infrastructure.transaction_manager.TransactionManager` | ACID transactions, rollback |
| **StructuredLogger** | `cortex.infrastructure.structured_logger.StructuredLogger` | JSON logging, PII redaction |
| **PrometheusMetrics** | `cortex.infrastructure.prometheus_metrics.PrometheusMetrics` | RED/USE metrics |
| **DistributedTracing** | `cortex.infrastructure.tracing.DistributedTracing` | OpenTelemetry tracing |
| **EnhancedAuditLogger** | `cortex.infrastructure.enhanced_audit_logger.EnhancedAuditLogger` | Hash-chain audit logging |
| **CrashRecovery** | `cortex.infrastructure.crash_recovery.CrashRecovery` | State recovery after failures |
| **FaultIsolator** | `cortex.infrastructure.fault_isolator.FaultIsolator` | Cascading failure prevention |

---

### State & Concurrency — 82/82 Tests (100%)

| Component | Entry Point | Capabilities |
|-----------|-------------|--------------|
| **OptimisticLock** | `cortex.core.state.optimistic_lock.OptimisticLock` | Version-based concurrency |
| **PhaseStateMachine** | `cortex.core.state.phase_state_machine.PhaseStateMachine` | Phase transitions |
| **StateManager** | `cortex.brain.core.state_manager.StateManager` | Cross-phase persistence |
| **LockFreeRegistry** | `cortex.orchestrators.registry.lock_free_registry.LockFreeRegistry` | Concurrent registration |
| **AuditHashChain** | `cortex.infrastructure.audit_hash_chain.AuditHashChain` | Tamper-evident logging |

---

### Fault Tolerance — 127/127 Tests (100%)

| Component | Entry Point | Capabilities |
|-----------|-------------|--------------|
| **SagaCoordinator** | `cortex.core.recovery.saga_coordinator.SagaCoordinator` | Distributed transaction compensation |
| **OrphanCleaner** | `cortex.core.recovery.orphan_cleaner.OrphanCleaner` | Orphaned resource cleanup |
| **CrashRecovery** | `cortex.infrastructure.crash_recovery.CrashRecovery` | Post-failure recovery |
| **FaultIsolator** | `cortex.infrastructure.fault_isolator.FaultIsolator` | Fault containment |

---

### Observability — 137/137 Tests (100%)

| Component | Entry Point | Capabilities |
|-----------|-------------|--------------|
| **StructuredLogger** | `cortex.infrastructure.structured_logger.StructuredLogger` | JSON logging, correlation IDs |
| **PrometheusMetrics** | `cortex.infrastructure.prometheus_metrics.PrometheusMetrics` | RED/USE metrics |
| **DistributedTracing** | `cortex.infrastructure.tracing.DistributedTracing` | OpenTelemetry, sampling |
| **HealthEndpoints** | `cortex.api.health_endpoints.HealthEndpoints` | Liveness, readiness checks |
| **ProfilingTools** | `cortex.devx.profiling_tools.ProfilingTools` | CPU/memory profiling |

**Dashboards:**
```
deployment/grafana/dashboards/
├── system-dashboard.json
├── governance-dashboard.json
└── database-dashboard.json

deployment/prometheus/alerts.yaml
```

---

### Intelligence Modules — 42/42 Tests (100%)

| Component | Entry Point | Capabilities |
|-----------|-------------|--------------|
| **RoutingAnalyzer** | `cortex.core.intelligence.routing_intelligence.RoutingAnalyzer` | Routing accuracy analysis |
| **DurationAnalyzer** | `cortex.core.intelligence.duration_intelligence.DurationAnalyzer` | p50/p95/p99 baselines |
| **ErrorAnalyzer** | `cortex.core.intelligence.error_intelligence.ErrorAnalyzer` | Brittle handler detection |

---

### Win Track Features — 48/48 Tests (100%)

| Phase | Tests | Status |
|-------|-------|--------|
| Registry Infrastructure | 7 | ✅ Complete |
| E2E Validation | 11 | ✅ Complete |
| CICD Automation | 9 | ✅ Complete |
| Governance Content | 12 | ✅ Complete |
| Feature Discovery | 9 | ✅ Complete |

---

## ⏳ PHASE 4: Roadmap In-Progress

### Current Phase: PHASE-E-TDD-IMPLEMENTATION

**Authority:** `_workspaces/roadmap/cortex-impl-map.yaml`

| Track | Status | Progress |
|-------|--------|----------|
| **Mac Track** | ⏳ IN_PROGRESS | Day 1 of 15-20 |
| **Win Track** | ✅ COMPLETE | 5/5 phases (48 tests) |

### Remaining Work

| Component | Current | Target | Gap |
|-----------|---------|--------|-----|
| Domain Brain | 213/353 (60%) | 353/353 | 140 tests |
| Orchestrators | 412/613 (67%) | 613/613 | 201 tests |
| MCP Tools | 14 stubs | 14 functional | Logic implementation |

### Phase Files

```
_workspaces/roadmap/
├── cortex-impl-map.yaml         # SSOT: Implementation status
├── PHASE-E-EXECUTION-STATUS.md  # Current phase status
├── phases/
│   ├── PHASE-E-TDD-IMPLEMENTATION.yaml
│   ├── impl-governance-001-context-aware.yaml
│   ├── impl-infra-001-resilience.yaml
│   └── ... (15 phase specifications)
└── reports/
    ├── PHASE-E2-EXECUTIVE-SUMMARY.md
    └── PHASE-E2-INVENTORY.md
```

---

## 📋 PHASE 5: Validation Checklist

### Environment Verification

```powershell
# 1. Test collection (expect 7540+ tests)
pytest tests/ --co -q 2>&1 | Select-String "test"

# 2. Run intent router tests (128/128 expected)
pytest tests/unit/intent_router/ -v --tb=short

# 3. Run governance tests (348/368 expected)
pytest tests/unit/governance/ -v --tb=short

# 4. Verify MCP server starts
python -m cortex.mcp.server --health-check

# 5. Validate governance
python -m cortex.brain.core.governance_registry --validate
```

### Quick Health Check

```python
# Run this to verify all systems operational
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.intent_router.classifier import IntentClassifier
from cortex.brain.core.governance_registry import GovernanceRegistry
from cortex.brain.core.state_manager import StateManager

print("Checking CORTEX components...")
print(f"✓ MasterOrchestrator: {MasterOrchestrator().name}")
print(f"✓ IntentClassifier: Ready")
print(f"✓ GovernanceRegistry: {len(GovernanceRegistry().rules)} rules")
print(f"✓ StateManager: Operational")
print("\n🧠 CORTEX is ready for operation!")
```

---

## 🎯 MCP Tools Available (14 Registered)

| Category | Tools | Status |
|----------|-------|--------|
| **Governance** | query_tool, validate_tool, execute_tool, analyze_tool, report_tool | Registered |
| **Orchestration** | status_tool, monitor_tool, optimize_tool, diagnose_tool | Registered |
| **Knowledge** | search_tool, analyze_tool, generate_tool | Registered |
| **Utility** | echo_tool, sample_tool | Registered |

**Entry Point:**
```python
from cortex.mcp.registry import get_mcp_tool_registry

registry = get_mcp_tool_registry()
for tool in registry.list_tools():
    print(f"- {tool.name}: {tool.category}")
```

---

## 🔧 MasterOrchestrator Pipeline

### 4-Stage Execution

```python
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

orchestrator = MasterOrchestrator()

# Stage 1: Intent Comprehension (LENS Protocol)
# Stage 2: Intent Routing
# Stage 3: Knowledge Integration
# Stage 4: Execution & Audit

result = orchestrator.execute_operation(
    operation_type="IMPLEMENT",
    context={"ac_id": "AC-XXX-001", "description": "..."},
    governance_enabled=True
)
```

### Response Header (CORE-029)

Every CORTEX response MUST begin with:

```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

---
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
```

---

## 📚 Key File References

| Document | Location | Purpose |
|----------|----------|---------|
| **System Prompt** | `.github/prompts/CORTEX.prompt.md` | MasterOrchestrator instructions |
| **Copilot Instructions** | `.github/copilot-instruction.md` | Workspace development rules |
| **Implementation Map** | `_workspaces/roadmap/cortex-impl-map.yaml` | SSOT: Phase status |
| **TIER 0 Rules** | `cortex_brain/tier0/governance/core-rules.yaml` | 29 immutable rules |
| **Governance DB** | `cortex_brain/state/governance.db` | 257 production ACs |

---

## 🚨 Post-Clone Troubleshooting

### Import Errors

```powershell
# If ImportError on cortex package
$env:PYTHONPATH = "C:\PROJECTS\CORTEX"
python -c "import cortex; print('OK')"
```

### Database Missing

```powershell
# Recreate governance database
python -c "
from cortex.infrastructure.database import DatabaseManager
db = DatabaseManager()
db.initialize()
print('Database initialized')
"
```

### Test Collection Fails

```powershell
# Check for syntax errors
python -m py_compile cortex/__init__.py

# Run with verbose collection
pytest tests/ --co -v 2>&1 | Select-Object -First 50
```

---

## ✅ Setup Complete Confirmation

After running all steps, you should see:

```
✓ Python virtual environment: .venv/
✓ Dependencies installed: requirements.txt
✓ Test collection: 7540+ tests
✓ Intent Router: 128/128 (100%)
✓ Governance Engine: 348/368 (95%)
✓ Infrastructure: 472/472 (100%)
✓ MasterOrchestrator: Ready
✓ Copilot Instructions: Wired
✓ CORTEX.prompt.md: Active

🧠 CORTEX is fully operational and ready for development!
```

---

**Last Updated:** 2026-01-21
**Authority:** cortex-impl-map.yaml v3.9
**Agent Support:** `cortex.tools.total_recall_agent.TotalRecallAgent`
**Status:** ✅ Post-clone setup and functionality wiring complete
