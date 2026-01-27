# Phase 8: CORE-035 Consolidation Plan (UPDATED)
**Date:** 2026-01-27  
**Authority:** CORE-030 (Implementation Truth), CORE-035 (Single Canonical)  
**Status:** READY FOR EXECUTION

---

## 📊 Canonical Location Determination

**Criteria for Canonical Selection:**
1. **Largest file** (most complete implementation)
2. **Most functions/classes** (most features)
3. **CORE-038 compliance** (proper location per File Placement Policy)
4. **Most imports** (most dependencies = likely production code)

---

## 🎯 Consolidation Matrix

| File | Canonical (KEEP) | Remove | Decision Rationale |
|------|-----------------|--------|-------------------|
| **tier_resolver.py** | `cortex/brain/core/tier_resolver.py` (123 lines, 4 imports) | `cortex/core/` (10 lines), `cortex/mcp/tools/governance/` (92 lines) | Brain/core is proper location per CORE-038 |
| **routing_engine.py** | `cortex/orchestrators/adaptive/routing_engine.py` (336 lines, 2 classes) | `cortex/intent_router/` (89 lines), `cortex/brain/intent_router/` (20 lines) | Largest, most complete implementation |
| **registry.py** | `cortex/brain/tier1/orchestrators/cleaners/registry.py` (262 lines, 3 classes) | `cortex/mcp/` (245 lines), `cortex/brain/mcp/` (101 lines) | Most complete, proper tier1 location |
| **performance_profiler.py** | `cortex/brain/core/observability/performance_profiler.py` (579 lines, 8 classes) | `cortex/orchestrators/adaptive/` (272 lines), `cortex/brain/observability/` (431 lines) | Largest, most features, proper location |
| **performance_metrics.py** | `cortex/execution/performance_metrics.py` (95 lines, 2 classes) | `cortex/intent_router/` (62 lines), `cortex/brain/intent_router/` (28 lines) | Most complete, proper execution domain |
| **orchestrator.py** | `cortex/orchestrators/documentation/orchestrator.py` (938 lines, 15 classes) | `cortex/orchestrators/onboarding/` (286 lines), `cortex/brain/core/decorators/` (190 lines) | Largest, domain-specific orchestrators stay separate |
| **observability.py** | `cortex/intent_router/observability.py` (227 lines, 4 classes) | `cortex/core/` (1 line stub), `cortex/brain/intent_router/` (110 lines) | Most complete implementation |
| **domain_orchestrator.py** | `cortex/domain_orchestrators/domain_orchestrator.py` (301 lines, 9 classes) | `cortex/orchestrators/` (88 lines), `cortex/brain/domain_orchestrators/` (139 lines) | Canonical domain_orchestrators location |
| **documentation.py** | `cortex/cli/commands/documentation.py` (360 lines, 13 classes) | `cortex/intent_router/` (124 lines), `cortex/brain/intent_router/` (47 lines) | CLI commands is proper location |
| **batch_audit_logger.py** | `cortex/brain/intent_router/batch_audit_logger.py` (86 lines) | `cortex/brain/governance_tools/` (42 lines), `cortex/brain/domain_orchestrators/` (43 lines) | Most complete implementation |

---

## ⚠️ SPECIAL CASE: orchestrator.py

**Finding:** `orchestrator.py` has 3 copies but they serve DIFFERENT purposes:

1. `cortex/orchestrators/documentation/orchestrator.py` (938 lines) - **DocumentationOrchestrator**
2. `cortex/orchestrators/onboarding/orchestrator.py` (286 lines) - **OnboardingOrchestrator**  
3. `cortex/brain/core/decorators/orchestrator.py` (190 lines) - **@orchestrator decorator**

**Decision:** These are NOT duplicates - they are different implementations with same filename.

**Action:** RENAME for clarity:
- `cortex/orchestrators/documentation/orchestrator.py` → `documentation_orchestrator.py`
- `cortex/orchestrators/onboarding/orchestrator.py` → `onboarding_orchestrator.py`
- `cortex/brain/core/decorators/orchestrator.py` → `orchestrator_decorator.py`

**Rationale:** CORE-035 allows same filename if implementations are genuinely different. Better solution: unique names to prevent confusion.

---

## 📋 Consolidation Tasks

### Task 1: Tier Resolver (P1 - Critical)
**Canonical:** `cortex/brain/core/tier_resolver.py`  
**Remove:**
- `cortex/core/tier_resolver.py` (10 lines - stub)
- `cortex/mcp/tools/governance/tier_resolver.py` (92 lines)

**Import Fix Pattern:**
```python
# OLD (2 variants)
from cortex.core.tier_resolver import TierResolver
from cortex.mcp.tools.governance.tier_resolver import TierResolver

# NEW (canonical)
from cortex.brain.core.tier_resolver import TierResolver
```

**Import Search:**
```bash
grep -r "from cortex.core.tier_resolver\|from cortex.mcp.tools.governance.tier_resolver" \
  --include="*.py" ./cortex ./tests
```

---

### Task 2: Routing Engine (P1 - Critical)
**Canonical:** `cortex/orchestrators/adaptive/routing_engine.py`  
**Remove:**
- `cortex/intent_router/routing_engine.py` (89 lines)
- `cortex/brain/intent_router/routing_engine.py` (20 lines - stub)

**Import Fix Pattern:**
```python
# OLD (2 variants)
from cortex.intent_router.routing_engine import RoutingEngine
from cortex.brain.intent_router.routing_engine import RoutingEngine

# NEW (canonical)
from cortex.orchestrators.adaptive.routing_engine import RoutingEngine
```

---

### Task 3: Registry (P1 - Critical)
**Canonical:** `cortex/brain/tier1/orchestrators/cleaners/registry.py`  
**Remove:**
- `cortex/mcp/registry.py` (245 lines)
- `cortex/brain/mcp/registry.py` (101 lines)

**Import Fix Pattern:**
```python
# OLD (2 variants)
from cortex.mcp.registry import MCPRegistry
from cortex.brain.mcp.registry import MCPRegistry

# NEW (canonical)
from cortex.brain.tier1.orchestrators.cleaners.registry import MCPRegistry
```

---

### Task 4: Performance Profiler (P2 - High)
**Canonical:** `cortex/brain/core/observability/performance_profiler.py`  
**Remove:**
- `cortex/orchestrators/adaptive/performance_profiler.py` (272 lines)
- `cortex/brain/observability/performance_profiler.py` (431 lines)

---

### Task 5: Performance Metrics (P2 - High)
**Canonical:** `cortex/execution/performance_metrics.py`  
**Remove:**
- `cortex/intent_router/performance_metrics.py` (62 lines)
- `cortex/brain/intent_router/performance_metrics.py` (28 lines)

---

### Task 6: Observability (P2 - High)
**Canonical:** `cortex/intent_router/observability.py`  
**Remove:**
- `cortex/core/observability.py` (1 line - stub)
- `cortex/brain/intent_router/observability.py` (110 lines)

---

### Task 7: Domain Orchestrator (P2 - High)
**Canonical:** `cortex/domain_orchestrators/domain_orchestrator.py`  
**Remove:**
- `cortex/orchestrators/domain_orchestrator.py` (88 lines)
- `cortex/brain/domain_orchestrators/domain_orchestrator.py` (139 lines)

---

### Task 8: Documentation (P3 - Medium)
**Canonical:** `cortex/cli/commands/documentation.py`  
**Remove:**
- `cortex/intent_router/documentation.py` (124 lines)
- `cortex/brain/intent_router/documentation.py` (47 lines)

---

### Task 9: Batch Audit Logger (P3 - Medium)
**Canonical:** `cortex/brain/intent_router/batch_audit_logger.py`  
**Remove:**
- `cortex/brain/governance_tools/batch_audit_logger.py` (42 lines)
- `cortex/brain/domain_orchestrators/batch_audit_logger.py` (43 lines)

---

### Task 10: Orchestrator Rename (P3 - Medium - RENAME, NOT DELETE)
**Action:** Rename for clarity (not consolidation)
- `cortex/orchestrators/documentation/orchestrator.py` → `documentation_orchestrator.py`
- `cortex/orchestrators/onboarding/orchestrator.py` → `onboarding_orchestrator.py`
- `cortex/brain/core/decorators/orchestrator.py` → `orchestrator_decorator.py`

---

## 📊 Impact Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Duplicate Groups** | 10 | 0 | -10 (100%) |
| **Total Files** | 30 | 10 | -20 (67% reduction) |
| **Lines of Code** | ~4,500 | ~3,000 | -1,500 (33% reduction) |
| **CORE-035 Compliance** | ❌ 10 violations | ✅ 100% compliant | Achieved |

---

## 🧪 Testing Strategy (CORE-008)

**For Each Consolidation:**

1. **Before:** Run existing tests to establish baseline
   ```bash
   pytest tests/ -v --tb=short -k "tier_resolver or routing_engine or registry"
   ```

2. **During:** Fix imports in canonical file first
   ```bash
   # Update all imports to point to canonical location
   find . -name "*.py" -type f -exec sed -i '' 's/from cortex.core.tier_resolver/from cortex.brain.core.tier_resolver/g' {} \;
   ```

3. **Validate:** Run tests again (should still pass)
   ```bash
   pytest tests/ -v --tb=short
   ```

4. **Delete:** Remove duplicate files
   ```bash
   git rm cortex/core/tier_resolver.py
   git rm cortex/mcp/tools/governance/tier_resolver.py
   ```

5. **After:** Run full test suite
   ```bash
   pytest tests/ -v
   ```

---

## 🔧 Automated Consolidation Script

**Script Location:** `_workspaces/docker-plan/consolidate-duplicates.sh`

**Usage:**
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
bash _workspaces/docker-plan/consolidate-duplicates.sh --dry-run  # Preview
bash _workspaces/docker-plan/consolidate-duplicates.sh --execute  # Execute
```

**Safety Features:**
- Dry-run mode (preview changes)
- Git checkpoint before execution
- Rollback on test failure
- Backup of removed files

---

## ⏱️ Execution Timeline

| Task | Duration | Cumulative |
|------|----------|------------|
| Task 1: Tier Resolver | 30 min | 0:30 |
| Task 2: Routing Engine | 30 min | 1:00 |
| Task 3: Registry | 30 min | 1:30 |
| Task 4-6: Performance Files | 1 hour | 2:30 |
| Task 7-9: Remaining Files | 1 hour | 3:30 |
| Task 10: Orchestrator Rename | 30 min | 4:00 |
| Testing & Validation | 1 hour | 5:00 |
| Git Checkpoint & Documentation | 30 min | 5:30 |

**Total:** 5.5 hours

---

## ✅ Success Criteria

- [ ] All 20 duplicate files removed
- [ ] All imports updated to canonical locations
- [ ] Full test suite passes (172+ tests)
- [ ] No import errors or circular dependencies
- [ ] Git checkpoint created (CORE-026)
- [ ] Phase 8 marked COMPLETE
- [ ] CORE-035 100% compliance achieved

---

## 🎯 Next Step

**Ready to create consolidation script?**

- **Type "script"** → Generate automated consolidation script
- **Type "manual"** → Execute tasks manually with guidance
- **Type "task1"** → Start with Task 1 (Tier Resolver) only

**Recommendation:** Generate script for safety and automation.
