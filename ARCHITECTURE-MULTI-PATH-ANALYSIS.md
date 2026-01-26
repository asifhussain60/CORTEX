# CORTEX Comprehensive Multi-Path Architecture Analysis
**Author:** Asif Hussain | **Date:** 2026-01-26 | **Authority:** CORE-035 (Single Canonical Implementation)

---

## 📊 Executive Summary

Comprehensive repository scan identified **285+ CORE-035 violations** categorized into 3 distinct multi-path architecture patterns:

| Pattern | Count | Severity | Status |
|---------|-------|----------|--------|
| **Type 1: Duplicate Classes** | 154 | 🔴 CRITICAL | Identified |
| **Type 2: Duplicate Functions** | 101 | 🟡 HIGH | Identified |
| **Type 3: Duplicate Execution Paths** | 30+ | 🔴 CRITICAL | Identified |

**Impact:** Deployment blocked until duplicates resolved. Auto-cleanup mechanisms remove code unpredictably.

---

## 🏗️ Multi-Path Architecture Problems (Detailed)

### PATTERN 1: Duplicate Execution Paths in Orchestrators

**Root Cause:** Same functionality implemented in multiple `execute_*` methods with conditional routing.

#### Problem 1.1: Master Orchestrator (FIXED - See notes below)
```python
# Location: cortex/orchestrators/core/master_orchestrator.py

# PATH A: execute_operation() [ACTIVE - lines 1086-1310]
def execute_operation(self, operation_name: str, parameters: Dict):
    # Stage 1 & 2 wiring ONLY in execute_operation
    # Scope: ALL operations
    # Status: ✅ ACTIVE (after AC-DRIFT-REMEDIATION-001)

# PATH B: coordinate_operation() [DEAD - rarely called]
def coordinate_operation(self, operation_data: Dict):
    # Previously had duplicate Stage 1 & 2 code
    # Scope: operation_name == "coordinate_operation"
    # Caller: Line 1434, only if operation_name matches
    # Status: ✅ CLEANED (code removed in AC-DRIFT-REMEDIATION-001)
```

**Status:** ✅ **PERMANENTLY FIXED** via AC-DRIFT-REMEDIATION-001
- Consolidated to single canonical path in `execute_operation()`
- Dead code removed from `coordinate_operation()`
- All Stage 1 & 2 orchestrator wiring now in active execution path
- Deployed and verified

---

### PATTERN 2: Multiple Handler/Router/Coordinator Classes

**Root Cause:** Different naming conventions + layered architecture created parallel implementations.

| Problem | Path A | Path B | Path C | Status |
|---------|--------|--------|--------|--------|
| **HandlerCoordinator** | cortex/orchestrators/handlers/handler_implementations.py:282 | cortex/orchestrators/coordinator.py:1 | — | 🟡 Duplicate implementation |
| **IntentClassificationHandler** | cortex/orchestrators/handlers/intent_classification_handler.py | cortex/orchestrators/core/intent_router.py | — | 🟡 Duplicate implementation |
| **ExecutionCoordinator** | cortex/orchestrators/handlers/handler_implementations.py:170 | cortex/orchestrators/coordinator.py | — | 🟡 Parallel implementations |

#### Problem 2.1: HandlerCoordinator vs OrchestrationCoordinator
```python
# CLASS 1: HandlerCoordinator
# Location: cortex/orchestrators/handlers/handler_implementations.py:282
class HandlerCoordinator:
    """Coordinates all handlers for orchestration pipeline."""
    def orchestrate(self, text: str, context: Dict[str, Any]) -> HandlerResult:
        # Implements: Intent → Route → Governance → Knowledge → Execute

# CLASS 2: OrchestrationCoordinator
# Location: cortex/orchestrators/coordinator.py:1
class OrchestrationCoordinator:
    """Coordinates multiple orchestrators with deadlock prevention."""
    def execute(self, ...):
        # Implements: Lock ordering → Registry → Deadlock detection
```

**Problem:** Both coordinate multi-step operations but have NO shared interface. Different approaches:
- `HandlerCoordinator`: Pipeline-style (sequential handlers)
- `OrchestrationCoordinator`: Lock-based (concurrent safety)

**Decision Points for Consolidation:**
- Keep both (specialized purposes) with unified interface
- Or consolidate via composition pattern (preferred)

**Recommended Fix:** Create `UnifiedCoordinator` using composition pattern.

---

#### Problem 2.2: Multiple Intent Routing Implementations
```python
# IMPLEMENTATION A: HandlerCoordinator routing
# cortex/orchestrators/handlers/handler_implementations.py:140
class RoutingHandler:
    def route(self, intent: Intent) -> HandlerResult:
        route_key = f"{intent.intent_type}:{intent.scope}"
        handler_name = self._routes.get(route_key, f"{intent.scope}_orchestrator")
        return HandlerResult(success=True, data=handler_name)

# IMPLEMENTATION B: IntentRouter routing
# cortex/orchestrators/core/intent_router.py:890
def execute_operation(self, operation_name: str, parameters: Dict):
    if operation_name == "route_operation":
        decision = self.route(parameters)
        return Ok(decision)

# IMPLEMENTATION C: Documentation orchestrator routing
# cortex/orchestrators/domain/enhanced_documentation_orchestrator.py:671
def execute_operation(self, operation_name: str, parameters: Dict[str, Any]):
    if operation_name == 'extract_api':
        python_file = parameters.get('file', '')
        return self.extract_api_docs(python_file)
```

**Problem:** Different routing logic in 3+ places with NO shared interface.

---

### PATTERN 3: Duplicate Enum/Model Classes

**Count:** 154 classes with 2-8 duplicate implementations each

**Top Offenders:**
| Class | Instances | Locations |
|-------|-----------|-----------|
| `ComplexityLevel` | 8 | cortex/core/, cortex/orchestrators/, cortex/brain/ |
| `SeverityLevel` | 5 | cortex/core/, cortex/orchestrators/, cortex/brain/ |
| `ValidationSeverity` | 5 | cortex/core/, cortex/domain_orchestrators/, cortex/brain/ |
| `AlertSeverity` | 4 | cortex/brain/core/, cortex/infrastructure/, cortex_brain/tier2/ |
| `ViolationType` | 4 | cortex/orchestrators/, cortex/testing/, cortex_brain/ |
| `ToolCategory` | 5 | cortex/mcp/, cortex/orchestrators/ |

**Example - ComplexityLevel (8 implementations):**
```python
# 1. cortex/core/orchestrator/complexity_assessment.py:14
class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# 2. cortex/orchestrators/core/tool_discovery_orchestrator_enhanced.py:50
class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# 3-8: Similar in other files...
# (All identical implementations with NO shared reference)
```

**Problem:** Auto-cleanup or refactoring deletes "duplicate" imports causing import errors.

---

### PATTERN 4: Decorator Function Duplicates

**Functions with 2-3 implementations:**

| Function | Count | Paths |
|----------|-------|-------|
| `orchestrator()` decorator | 3 | cortex/core/decorators/, cortex/brain/core/decorators/, cortex/brain/core/ |
| `mcp_tool()` decorator | 3 | cortex/mcp/decorator.py, cortex/mcp/decorators.py, cortex/brain/mcp/ |
| `get_registered_tools()` | 3 | cortex/mcp/, cortex/brain/mcp/ |
| `clear_orchestrator_registry()` | 2 | cortex/core/decorators/, cortex/brain/core/decorators/ |
| `get_registered_orchestrators()` | 2 | cortex/core/decorators/, cortex/brain/core/decorators/ |

**Problem:** Registry state inconsistency when decorators in different modules register same orchestrator/tool.

---

### PATTERN 5: Dashboard Extensibility Duplicates

**Issue:** 100% code duplication across two modules:

```python
# SET A: cortex/observability/dashboard_extensibility.py (100+ functions)
def get_business_context(self, ...):
def get_cache_status(self, ...):
def is_domain_available(self, ...):
def enrich_dashboard_context(self, ...):
def enrich_batch_context(self, ...):
# ... 10+ more

# SET B: cortex/brain/observability/dashboard_extensibility.py
# IDENTICAL IMPLEMENTATION of all functions above
```

**Status:** 🟡 **Complete duplication** - both modules exist with no clear purpose differentiation.

---

### PATTERN 6: Documentation Orchestrator Multiple Paths

**Issue:** 3 different execute/operation methods in same file:

```python
# cortex/orchestrators/domain/enhanced_documentation_orchestrator.py

# PATH 1: execute(self, request: Dict[str, Any]) -> Result
def execute(self, request: Dict[str, Any]) -> Result:
    if operation == 'validate':
        return self.validate_links(doc_file)
    elif operation == 'cleanup':
        return self.generate_cleanup_tasks()
    # ...

# PATH 2: execute_operation(self, operation_name: str, parameters: Dict) -> Result
def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result:
    if operation_name == 'extract_api':
        python_file = parameters.get('file', '')
        return self.extract_api_docs(python_file)
    # ...

# PATH 3: execute_on_domain(self, operation: str) -> Result
def execute_on_domain(self, operation: str) -> Result:
    if operation == 'validate_links':
        # Different implementation than execute()
    # ...
```

**Problem:** Same operation types scattered across 3 methods with inconsistent naming and signatures.

---

### PATTERN 7: MCP Tools Registry Duplication

**Issue:** Tools registered in multiple places:

```python
# REGISTRY A: cortex/mcp/registry.py:21
class ToolCategory(Enum):
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"

# REGISTRY B: cortex/orchestrators/mcp_tools_registry.py:21
class ToolCategory(Enum):
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"

# REGISTRY C: cortex/mcp/tool_governance.py:16
class ToolCategory(Enum):
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"

# REGISTRY D: cortex/mcp/unified_tool_discovery.py:27
class ToolCategory(Enum):
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"

# REGISTRY E: cortex/orchestrators/core/tool_discovery_orchestrator_enhanced.py:58
class ToolCategory(Enum):
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
```

**Problem:** Changes to tool categories require updates in 5+ places.

---

## 📋 Complete Multi-Path Violations Table

### Type 1: Duplicate Orchestrator/Coordinator Classes (HIGH PRIORITY)

| Problem | Path A | Path B | Path C | Impact | Fix |
|---------|--------|--------|--------|--------|-----|
| **HandlerCoordinator** | handlers/handler_implementations.py:282 | orchestrators/coordinator.py:1 | — | Parallel execution pipelines | Consolidate with composition |
| **ExecutionCoordinator** | handlers/handler_implementations.py:170 | coordinator.py | — | Duplicate operation execution | Use canonical path |
| **IntentRouter** | core/intent_router.py | handlers/intent_classification_handler.py | — | Duplicate intent classification | Merge into single router |
| **DocumentationOrch** | documentation/orchestrator.py | domain/enhanced_documentation_orchestrator.py | — | Duplicate doc operations | Use factory pattern |
| **RefactoringOrch** | domain/refactoring_orchestrator.py | domain/enhanced_refactoring_orchestrator.py | — | Duplicate refactoring logic | Single base implementation |
| **PlanningOrch** | domain/planning_orchestrator.py | domain/enhanced_planning_orchestrator.py | — | Duplicate planning operations | Merge with strategy pattern |

### Type 2: Duplicate Dashboard Extensibility

| Problem | Path A | Path B | Impact | Fix |
|---------|--------|--------|--------|-----|
| **Dashboard Context** | observability/dashboard_extensibility.py:92 | brain/observability/dashboard_extensibility.py:92 | **100% code duplication** | Keep one, delete other |
| **Enrich Dashboard** | observability/dashboard_extensibility.py:139 | brain/observability/dashboard_extensibility.py:139 | Inconsistent enrichment | Consolidate |
| **Business Context** | observability/dashboard_extensibility.py:196 | brain/observability/dashboard_extensibility.py:196 | State divergence | Canonical implementation |

### Type 3: Duplicate Enum Definitions (MEDIUM PRIORITY)

| Enum | Instances | Typical Locations | Fix |
|------|-----------|-------------------|-----|
| `ComplexityLevel` | 8 | core/,orchestrators/,brain/, | Create cortex_brain/tier3/enums.py |
| `SeverityLevel` | 5 | core/, orchestrators/, brain/ | Move to shared module |
| `ToolCategory` | 5 | mcp/, orchestrators/ | Create MCP canonical enums |
| `AlertSeverity` | 4 | brain/, infrastructure/ | Consolidate to infrastructure |
| `ViolationType` | 4 | orchestrators/, brain/, testing/ | Create governance enums |

### Type 4: Duplicate Decorator Functions (LOW-MEDIUM PRIORITY)

| Function | Instances | Paths | Fix |
|----------|-----------|-------|-----|
| `orchestrator()` | 3 | core/decorators/, brain/core/decorators/, brain/core/ | Use core/decorators as canonical |
| `mcp_tool()` | 3 | mcp/decorator.py, mcp/decorators.py, brain/mcp/decorator.py | Consolidate to mcp/decorator.py |
| `get_registered_orchestrators()` | 2 | core/decorators/, brain/core/decorators/ | Single registry |
| `clear_orchestrator_registry()` | 2 | core/decorators/, brain/core/decorators/ | Unified registry clearer |

### Type 5: Duplicate MCP Tools Registry

| Function | Instances | Paths | Fix |
|----------|-----------|-------|-----|
| `search_knowledge_base()` | 2 | mcp/tools/knowledge/, brain/mcp/tools/knowledge_tools.py | Consolidate |
| `analyze_knowledge_gap()` | 2 | mcp/tools/knowledge/, brain/mcp/tools/ | Merge implementations |
| `get_operation_status()` | 2 | mcp/tools/orchestration/, brain/mcp/tools/ | Single source |
| `monitor_orchestrator_health()` | 2 | mcp/tools/orchestration/, brain/mcp/tools/ | Canonical health monitor |

### Type 6: Duplicate Handlers & Validators

| Handler | Instances | Paths | Fix |
|---------|-----------|-------|-----|
| `AnalysisHandler` | 2 | domain_orchestrators/, brain/domain_orchestrators/ | Single handler base |
| `CreateHandler` | 2 | domain_orchestrators/, brain/domain_orchestrators/ | Consolidate |
| `validate_llm_output()` | 2 | core/hallucination_prevention/, core/safety/ | Safety module canonical |
| `validate_schema()` | 2 | mcp/domain_operations.py, common/validators.py | Common validators canonical |

---

## 🎯 Consolidation Strategy (CORE-035 Compliance)

### Phase 1: High-Impact Consolidations (CRITICAL)
**Priority:** Fix execution path duplicates first (prevent auto-cleanup)

| Target | Pattern | Approach | Timeline |
|--------|---------|----------|----------|
| `HandlerCoordinator` / `OrchestrationCoordinator` | Parallel implementation | Composition pattern with unified interface | Day 1-2 |
| Dashboard extensibility | 100% duplication | Delete brain/ version, keep cortex/ | Day 1 |
| `DocumentationOrchestrator` | Multiple execute methods | Consolidate 3 paths into 1 canonical | Day 2 |

### Phase 2: Enum Consolidation (HIGH)
**Priority:** Prevent import errors from deleted duplicates

**Solution:** Create canonical enum modules in `cortex_brain/tier3/`

```python
# NEW FILE: cortex_brain/tier3/common_enums.py
"""Canonical enum definitions (CORE-035 compliance).

This is the single source of truth for all shared enums.
All modules import from here, never define locally.
"""

from enum import Enum

class ComplexityLevel(Enum):
    """Shared complexity level definition."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SeverityLevel(Enum):
    """Shared severity level definition."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AlertSeverity(Enum):
    """Alert severity levels (superset of SeverityLevel)."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ToolCategory(Enum):
    """MCP tool categories."""
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE = "knowledge"
    TESTING = "testing"
    UTILITY = "utility"

class ViolationType(Enum):
    """Governance violation types."""
    CORE_RULE = "core_rule"
    TIER1_RULE = "tier1_rule"
    PATTERN_VIOLATION = "pattern_violation"
    SECURITY = "security"
```

Then in all modules:
```python
# ❌ BEFORE (scattered definitions)
class ComplexityLevel(Enum):
    LOW = "low"

# ✅ AFTER (canonical import)
from cortex_brain.tier3.common_enums import ComplexityLevel
```

### Phase 3: Decorator & Registry Consolidation (MEDIUM)
**Priority:** Ensure single decorator registration point

```python
# Canonical location: cortex/core/decorators/orchestrator_decorator.py

# Delete from: cortex/brain/core/decorators/orchestrator_decorator.py
# Delete from: cortex/brain/core/decorators/orchestrator.py

# Update imports everywhere to point to canonical location
```

### Phase 4: Handler Consolidation (MEDIUM-LOW)
**Priority:** Reduce complexity in handler implementations

```python
# Option A: Consolidation Pattern (Recommended - CONS-003-009 pattern)
class UnifiedHandlerCoordinator:
    """Single canonical coordinator (CORE-035)."""
    
    def __init__(self):
        self._pipeline_coordinator = HandlerCoordinator()  # For sequential
        self._lock_coordinator = OrchestrationCoordinator()  # For concurrent
    
    def execute(self, operation, context, concurrent=False):
        """Route to appropriate coordinator."""
        if concurrent:
            return self._lock_coordinator.execute(operation)
        return self._pipeline_coordinator.orchestrate(operation['text'], context)
```

---

## 🛠️ Implementation Plan

### IMMEDIATE ACTION ITEMS (Today)

#### 1. Create Canonical Enum Module
```bash
# File: cortex_brain/tier3/common_enums.py
# Lines: ~200
# Time: 1 hour
# Risk: LOW (additive, no changes to existing)
```

#### 2. Fix Dashboard Extensibility (Delete Duplicate)
```bash
# Delete: cortex/brain/observability/dashboard_extensibility.py
# Update imports: grep -r "from cortex.brain.observability" → "from cortex.observability"
# Risk: LOW (simple file deletion + import updates)
# Time: 30 minutes
```

#### 3. Consolidate HandlerCoordinator
```bash
# Create: cortex/orchestrators/handlers/unified_handler_coordinator.py
# Keep: Both old implementations for backward compatibility
# Add: Unified facade routing to appropriate implementation
# Risk: LOW (composition pattern, backward compatible)
# Time: 2 hours
```

### SHORT-TERM (This Week)

#### 4. Consolidate Documentation Orchestrator Paths
- Merge `execute()`, `execute_operation()`, `execute_on_domain()` into single method
- Use dispatch table pattern
- Add tests for all operation types

#### 5. Consolidate RefactoringOrchestrator Duplicates
- Enhanced → Base consolidation
- Verify all tests pass
- Update wiring registry

#### 6. Consolidate PlanningOrchestrator Duplicates
- Similar to RefactoringOrchestrator
- Merge enhanced version into base
- Maintain backward compatibility

### MEDIUM-TERM (Next 2 Weeks)

#### 7. Migrate All Enum Imports
- Run codemod to replace all local enum definitions
- Update 50+ files to import from `cortex_brain.tier3.common_enums`
- Verify import chains

#### 8. Consolidate Decorator Functions
- Move all decorators to canonical locations
- Delete duplicates from brain/ module
- Run import validation

#### 9. MCP Tools Registry Consolidation
- Single registry for tool registration
- Consolidate duplicate tool definitions
- Update all MCP tool modules

---

## 📊 Compliance Metrics

### Current State (VIOLATING CORE-035)
```
✅ Unique Classes: 495
✅ Unique Functions: 384
❌ Duplicate Classes: 154 (30.9% of classes)
❌ Duplicate Functions: 101 (26.3% of functions)
❌ Multi-Path Orchestrators: 6+ (HIGH RISK)
❌ Compliance Status: NON-COMPLIANT (285 violations)
```

### Target State (CORE-035 COMPLIANT)
```
✅ Unique Classes: 495 (zero duplicates)
✅ Unique Functions: 384 (zero duplicates)
✅ Multi-Path Orchestrators: 0 (single canonical paths)
✅ Compliance Status: COMPLIANT (0 violations)
✅ Deployment: UNBLOCKED
```

### Progress Tracking
```yaml
Target: 100% CORE-035 compliance
Current: 0% (just started comprehensive analysis)
Immediate fixes: 3 items (25%)
Short-term fixes: 6 items (50%)
Medium-term fixes: 3 items (75%)
Validation: All tests passing (100%)
```

---

## 🔒 Prevention Strategies (CORE-030: Implementation Truth)

### 1. Pre-Implementation Audit
```bash
# Before creating ANY new class/function:
python3 scripts/duplication_audit.py | grep "YOUR_CLASS_NAME"

# If found: DON'T create new → use consolidation pattern instead
```

### 2. Import from Canonical Locations ONLY
```python
# ✅ CORRECT
from cortex_brain.tier3.common_enums import ComplexityLevel

# ❌ WRONG
class ComplexityLevel(Enum):
    LOW = "low"  # Duplicate!
```

### 3. Pre-Commit Hook (Enforce CORE-035)
```bash
# ~/.git/hooks/pre-commit
python3 scripts/duplication_audit.py > /tmp/audit.txt
if grep -q "NEW VIOLATIONS" /tmp/audit.txt; then
    echo "❌ CORE-035 violation detected"
    echo "Run: python3 scripts/duplication_audit.py for details"
    exit 1
fi
```

### 4. Documentation Requirement
```
When creating new class/function:
- Add comment: "Canonical location: [LOCATION]"
- Add comment: "Replaces: [OLD DUPLICATES IF ANY]"
- Reference CORE-035 in commit message
```

---

## 📋 Detailed Consolidation Cases (Ready to Fix)

### CASE 1: HandlerCoordinator & OrchestrationCoordinator

**Current State:**
```python
# Two separate coordinators with different concerns
class HandlerCoordinator:  # Sequential handler pipeline
class OrchestrationCoordinator:  # Concurrent with locks
```

**Recommended Solution:**
```python
# cortex/orchestrators/handlers/unified_handler_coordinator.py (NEW)
class UnifiedHandlerCoordinator:
    """Single canonical coordinator (CORE-035).
    
    Routes to specialized coordinators based on context:
    - Sequential operations → HandlerCoordinator
    - Concurrent operations → OrchestrationCoordinator
    """
    
    def __init__(self):
        self._handler_coordinator = HandlerCoordinator()
        self._orchestration_coordinator = OrchestrationCoordinator()
    
    def orchestrate(
        self, 
        text: str,
        context: Dict[str, Any],
        concurrent: bool = False
    ) -> HandlerResult:
        """Execute orchestration (sequential or concurrent)."""
        if concurrent and context.get("requires_lock_safety"):
            return self._orchestration_coordinator.execute(
                operation_type=context.get("operation_type"),
                parameters=context.get("parameters", {})
            )
        
        return self._handler_coordinator.orchestrate(text, context)
```

**Backward Compatibility:**
- Keep both old classes functional
- New unified coordinator wraps them
- Existing code continues to work
- Gradual migration to canonical coordinator

---

### CASE 2: ComplexityLevel Enum (8 duplicates)

**Current Problem:**
```python
# Location 1: cortex/core/orchestrator/complexity_assessment.py
class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Location 2-8: Same definition repeated
```

**Fix:**
```python
# Step 1: Create canonical location
# File: cortex_brain/tier3/common_enums.py
class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Step 2: Replace all imports with codemod
from cortex_brain.tier3.common_enums import ComplexityLevel

# Step 3: Delete local definitions
# Delete from: cortex/core/orchestrator/complexity_assessment.py (and 7 others)

# Step 4: Verify
grep -r "class ComplexityLevel" cortex/
# Should return: only cortex_brain/tier3/common_enums.py
```

---

## 🚀 Execution Checklist

### PHASE 1: Foundation (Complete in 1 day)
- [ ] Create cortex_brain/tier3/common_enums.py with all canonical enums
- [ ] Delete cortex/brain/observability/dashboard_extensibility.py  
- [ ] Update all imports for deleted file
- [ ] Run tests to verify no breakage
- [ ] Create git commit: "CORE-035-001: Canonical enums and dashboard consolidation"

### PHASE 2: Coordinators (Complete in 2 days)
- [ ] Create UnifiedHandlerCoordinator
- [ ] Run tests for both sequential and concurrent paths
- [ ] Update orchestration entry points to use unified coordinator
- [ ] Run integration tests
- [ ] Create git commit: "CORE-035-002: Unified handler coordinator"

### PHASE 3: Orchestrators (Complete in 3 days)
- [ ] Consolidate DocumentationOrchestrator paths
- [ ] Consolidate RefactoringOrchestrator duplicates
- [ ] Consolidate PlanningOrchestrator duplicates
- [ ] Full test suite passing
- [ ] Create git commit: "CORE-035-003: Orchestrator consolidation"

### PHASE 4: Global Migration (Complete in 1 week)
- [ ] Codemod all enum imports
- [ ] Consolidate all decorator functions
- [ ] Consolidate all MCP tool registries
- [ ] Run full test suite
- [ ] Run duplication audit script
- [ ] Create git commit: "CORE-035-004: Complete enum and registry consolidation"

### PHASE 5: Validation
- [ ] All 285+ violations resolved
- [ ] Duplication audit shows 0 violations
- [ ] All 6,847+ tests passing
- [ ] Deployment unblocked
- [ ] Documentation updated

---

## 📈 Expected Outcomes

### After Consolidation
```
Metrics Before          Metrics After       Improvement
────────────────      ───────────────      ────────────
154 duplicate classes  0 duplicate classes  100% ↓
101 duplicate funcs    0 duplicate funcs    100% ↓
6+ multi-path orchs    Single canonical     100% ↓
285 violations         0 violations         100% ↓
Deployment blocked     Unblocked            ✅
Auto-cleanup risk      Eliminated           ✅
Import errors          Prevented            ✅
Maintenance cost       Reduced 40%+         ✅
Test coverage          Improved 15%+        ✅
```

### Code Quality Improvements
- **Maintainability:** Single source of truth for each component
- **Reliability:** No auto-cleanup confusion
- **Testability:** Easier to test canonical implementations
- **Performance:** Reduced module loading (fewer duplicates)
- **Governance:** Full CORE-035 compliance

---

## 📚 References

- **CORE-035:** Single Canonical Implementation
- **CORE-030:** Implementation Truth (verify code, not docs)
- **CONS-003-009:** Consolidation Pattern (composition vs inheritance)
- **AC-DRIFT-REMEDIATION-001:** Master Orchestrator fix (reference)
- **Duplication Audit:** `cortex/scripts/duplication_audit.py`

---

## ✅ Validation Criteria (GATE)

Before considering consolidation complete:

```yaml
✅ Compliance:
  - duplication_audit.py shows 0 violations
  - All CORE-035 checks pass
  - No new imports of duplicate classes

✅ Testing:
  - All 6,847+ tests passing
  - New consolidation tests added
  - Integration tests validated
  - E2E scenarios tested

✅ Performance:
  - No performance regression
  - Module load time ≤ baseline
  - Memory usage within bounds

✅ Documentation:
  - All canonical locations documented
  - Migration guide provided
  - CORE-035 principles explained

✅ Deployment:
  - Zero-downtime compatible
  - Backward compatibility verified
  - Rollback plan documented
```

---

**Status:** 📋 Ready for implementation  
**Next Action:** Execute Phase 1 consolidations  
**Estimated Timeline:** 10-12 business days (complete phases 1-5)  
**Owner:** GitHub Copilot / CORTEX MasterOrchestrator  
**Authority:** CORE-035 Single Canonical Implementation Rule

