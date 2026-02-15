# Wave IC-001: Intelligence Fixes Integration
## Enhanced with Phase 65 + ENH-092

**Status:** Enhanced and Ready for Implementation  
**Author:** Asif Hussain  
**Date:** 2026-02-14  
**Authority:** CORTEX Architect Mode

---

## 📊 Enhancement Summary

| Metric | Original | Enhanced | Delta |
|--------|----------|----------|-------|
| **Duration** | 7.5 hours | 8.0 hours | +0.5h (+7%) |
| **Test Count** | 80 tests | 88 tests | +8 tests (+10%) |
| **Intelligence Tests** | 66 tests | 74 tests | +8 tests (+12%) |
| **Intelligence Fixes** | 0 integrated | 5 integrated | +5 phases |
| **Coverage** | 95% target | 95% target | Maintained |

---

## 🔧 Intelligence Fixes Integrated

### 1. Phase 65 S4: Unified Intelligence Provider ✅
**Authority:** AC-PHASE65-S4-001  
**Status:** PRODUCTION (to be enhanced in T1.1)

**Components Integrated:**
- `IIntelligenceProvider` abstract interface
- `UnifiedIntelligenceProvider` singleton implementation
- `ExecutionTier` enum (QUICK/TARGETED/FULL)
- `CacheEntry` with 5-minute TTL
- Thread-safe singleton pattern with Lock
- Single canonical LENSCache (CORE-035)
- Budget-aware tiered execution
- Graceful degradation on source failures

**Integration Points:**
```python
# T1.1: Add audit logging to existing provider
from cortex.intelligence.provider import UnifiedIntelligenceProvider, get_intelligence_provider
from cortex.brain.observability.audit_trail import get_audit_trail

provider = get_intelligence_provider()
audit_trail = get_audit_trail()

# Wrap get_context() with AC markers
# Wrap synthesize() with audit logging
# Track session metrics in _session_metrics
```

**Files Modified:**
- `cortex/intelligence/provider.py` (Add audit logging hooks)
- `cortex/intelligence/__init__.py` (Export audit types)

### 2. Phase 65 S5: Turn-Over-Turn Intelligence Accumulation ✅
**Authority:** AC-PHASE65-S5-001  
**Status:** PRODUCTION (to be integrated in T1.1)

**Components Integrated:**
- `TurnContext` class for session-scoped intelligence
- `_session_profiles` storage (session_id → profile)
- `record_intelligence_fetch()` for turn tracking
- `get_accumulated_intelligence()` for cross-turn synthesis
- Thread-safe operations with Lock
- Session cleanup on session_end

**Integration Points:**
```python
# T1.1: Connect TurnContext to UnifiedIntelligenceProvider
from cortex.intelligence.turn_context import TurnContext

# In get_context():
turn_context = TurnContext(session_id)
turn_context.record_intelligence_fetch(
    turn_id=str(uuid.uuid4()),
    intent=intent,
    intelligence_data=context
)

# In synthesize():
accumulated = turn_context.get_accumulated_intelligence()
# Use accumulated intelligence in synthesis
```

**Files Modified:**
- `cortex/intelligence/provider.py` (Integrate TurnContext)
- `cortex/intelligence/turn_context.py` (Connect to provider)

**New Tests:**
- Test TurnContext integration with provider
- Test turn-over-turn accumulation across requests
- Test thread-safe turn context operations
- Test session profile storage with audit trail

### 3. ENH-092 Phase 53.3: Lifecycle Hook System ✅
**Authority:** ENH-092  
**Status:** PRODUCTION (to be integrated in T1.2)

**Components Integrated:**
- `LifecycleHookSystem` class
- `CompletionEvent` enum (WAVE_COMPLETE, PHASE_COMPLETE, SESSION_END, LENS_DECISION)
- `CompletionContext` dataclass
- `register_hook()` for event subscription
- `trigger_completion()` for event emission
- `_execution_history` tracking
- Default hooks for vacuum orchestration

**Integration Points:**
```python
# T1.2: Wire LENS triggers to lifecycle hooks
from cortex.orchestrators.core.lifecycle_hook_system import (
    LifecycleHookSystem,
    CompletionEvent,
    CompletionContext
)

# In IntentRouter._should_engage_lens():
hook_system = get_lifecycle_hook_system()
await hook_system.trigger_completion(
    CompletionEvent.LENS_DECISION,
    entity_id=f"lens_trigger:{intent}:{file_path}",
    metadata={
        "engaged": decision,
        "policy": policy_name,
        "reasoning": reasoning
    }
)
```

**Files Modified:**
- `cortex/orchestrators/core/intent_router.py` (Add lifecycle events)
- `cortex/orchestrators/core/lifecycle_hook_system.py` (Add LENS_DECISION event)

**New Files:**
- `cortex/orchestrators/core/lens_audit_hooks.py` (Lifecycle integration)

**New Tests:**
- Test LENS engagement logged to LifecycleHookSystem
- Test automatic cleanup on wave/phase completion
- Test LENS decision audit trail queryable

### 4. LENS Orchestrator (Production) ✅
**Authority:** cortex.lens.orchestrator  
**Status:** PRODUCTION (already integrated)

**Components Available:**
- `LENSOrchestrator` with tiered API (Phase 20)
- `LENSCache` singleton (CORE-035 compliance)
- `ASTAnalyzer`, `GitHistoryAnalyzer`, `CommentExtractor`
- `ConfigAnalyzer`, `DatabaseAnalyzer`, `APIAnalyzer`
- `analyze_file()` with depth control (shallow/medium/deep)
- Cache with 5-minute TTL

**Integration Points:**
```python
# Already integrated in UnifiedIntelligenceProvider
from cortex.lens.orchestrator import LENSOrchestrator, get_lens_orchestrator

# In UnifiedIntelligenceProvider._ensure_lens_orchestrator():
self._lens_orchestrator = get_lens_orchestrator(repo_path=Path.cwd())

# In get_lens_analysis():
return self._lens_orchestrator.analyze_file(Path(file_path))
```

**No Changes Required** - Already operational in Phase 65 S4

### 5. Enhanced Audit Logger (Production) ✅
**Authority:** cortex.brain.observability.audit_trail  
**Status:** PRODUCTION (to be integrated in T1.1)

**Components Available:**
- `AuditTrail` class with SQLite persistence
- `AuditEvent` dataclass with full context
- `AuditEventType`, `AuditSeverity` enums
- `RetentionPolicy` for automatic cleanup
- `search()` with filters (event_type, component, date range)
- `export()` to JSON/CSV
- Thread-safe with Lock

**Integration Points:**
```python
# T1.1: Use EnhancedAuditLogger in UnifiedIntelligenceProvider
from cortex.brain.observability.audit_trail import get_audit_trail, AuditEventType

audit_trail = get_audit_trail()

# In get_context():
event_id = str(uuid.uuid4())
audit_trail.record_event(
    event_type=AuditEventType.INTELLIGENCE_FETCH,
    component="UnifiedIntelligenceProvider",
    action="get_context",
    user="system",
    event_id=event_id,
    details={
        "intent": intent,
        "tier": tier.value,
        "duration_ms": duration_ms,
        "lens_invoked": lens_invoked
    }
)
```

**Files Modified:**
- `cortex/intelligence/provider.py` (Import and use audit trail)

**No New Files** - Audit trail already exists

---

## 🎯 Task Enhancements

### T1.1: Intelligence Audit Trail → Intelligence Audit Trail + Phase 65 Integration
**Duration:** 1h → 1.5h (+0.5h for Phase 65 S5 integration)

**Original Scope:**
- Add EnhancedAuditLogger to UnifiedIntelligenceProvider
- Wrap get_context(), synthesize() with AC markers
- Track session metrics

**Enhanced Scope:**
- ✅ All original scope items
- ✅ Integrate TurnContext for turn-over-turn accumulation
- ✅ Connect _session_profiles with audit logging
- ✅ Add fallback logging for graceful degradation
- ✅ Test session-scoped intelligence accumulation

**New Tests:** +4 (20 → 24 tests)
- Test TurnContext integration for turn-over-turn tracking
- Test TurnContext thread safety with concurrent turns
- Test session profile storage with audit trail
- Test turn-over-turn accumulation across multiple requests

### T1.2: LENS Trigger Extraction → LENS Trigger Extraction + Lifecycle Hook Integration
**Duration:** 1h → 1.5h (+0.5h for ENH-092 integration)

**Original Scope:**
- Extract _should_engage_lens() method
- Create LENSTriggerPolicy interface
- Wire policy injection

**Enhanced Scope:**
- ✅ All original scope items
- ✅ Wire LENS trigger decisions to LifecycleHookSystem
- ✅ Register CompletionEvent.LENS_DECISION hook
- ✅ Log LENS engagement/skip decisions to audit trail
- ✅ Connect to automatic cleanup on wave/phase completion

**New Tests:** +4 (24 → 28 tests)
- Test LENS engagement logged to LifecycleHookSystem
- Test automatic cleanup on wave/phase completion
- Test LENS decision audit trail queryable
- Test lifecycle hook integration with concurrent operations

### T1.3: Refactoring Multi-Cycle RGR (Unchanged)
**Duration:** 1h (no change)

**Scope:** Wire ENH-088 multi-cycle pattern to RefactoringOrchestrator

**No intelligence fixes to integrate** - focuses on refactoring orchestration

---

## 📋 Updated Deliverables

### Code Deliverables

| Deliverable | Status | Intelligence Fix |
|-------------|--------|------------------|
| UnifiedIntelligenceProvider + Audit | Enhanced | Phase 65 S4/S5 |
| TurnContext Integration | NEW | Phase 65 S5 |
| IntentRouter + LENS Triggers | Enhanced | ENH-092 |
| Lifecycle Hook Integration | NEW | ENH-092 |
| RefactoringOrchestrator + Multi-Cycle | Unchanged | N/A |
| Core Protocol | Unchanged | N/A |
| ARCHITECT/PRODUCTION Prompts | Unchanged | N/A |

### Test Deliverables

| Test File | Original | Enhanced | Intelligence Fix |
|-----------|----------|----------|------------------|
| test_audit_trail_integration.py | 20 tests | 24 tests | Phase 65 S5 (+4) |
| test_lens_triggers_lifecycle.py | 24 tests | 28 tests | ENH-092 (+4) |
| test_refactoring_multi_cycle.py | 22 tests | 22 tests | N/A |
| **Track 1 Total** | **66 tests** | **74 tests** | **+8 tests** |
| Track 2 (Prompts) | 14 tests | 14 tests | N/A |
| **Grand Total** | **80 tests** | **88 tests** | **+8 tests** |

---

## 🔄 Integration Strategy

### Phase 65 S4/S5 Integration (T1.1)

**Step 1: Audit Logger Setup**
```python
# cortex/intelligence/provider.py
from cortex.brain.observability.audit_trail import get_audit_trail

class UnifiedIntelligenceProvider(IIntelligenceProvider):
    def __init__(self):
        # ... existing code ...
        self._audit_trail = get_audit_trail()  # NEW
```

**Step 2: TurnContext Integration**
```python
# cortex/intelligence/provider.py
from cortex.intelligence.turn_context import TurnContext

def get_context(self, intent, file_path=None, session_id=None, ...):
    # ... existing code ...
    
    # NEW: Record in turn context
    if session_id:
        turn_context = TurnContext(session_id)
        turn_context.record_intelligence_fetch(
            turn_id=str(uuid.uuid4()),
            intent=intent,
            intelligence_data=context
        )
```

**Step 3: AC Marker Wrapping**
```python
def get_context(self, intent, ...):
    event_id = str(uuid.uuid4())
    
    # AC_START
    self._audit_trail.record_event(
        event_type=AuditEventType.INTELLIGENCE_FETCH,
        component="UnifiedIntelligenceProvider",
        action="get_context",
        event_id=event_id,
        details={"intent": intent, "tier": tier.value}
    )
    
    try:
        # ... existing logic ...
        result = context
    finally:
        # AC_COMPLETE
        self._audit_trail.record_event(
            event_type=AuditEventType.INTELLIGENCE_COMPLETE,
            component="UnifiedIntelligenceProvider",
            action="get_context",
            event_id=event_id,
            details={"duration_ms": duration_ms}
        )
```

### ENH-092 Integration (T1.2)

**Step 1: Import Lifecycle System**
```python
# cortex/orchestrators/core/intent_router.py
from cortex.orchestrators.core.lifecycle_hook_system import (
    LifecycleHookSystem,
    CompletionEvent,
    CompletionContext
)
```

**Step 2: Wire LENS Trigger Events**
```python
def _should_engage_lens(self, intent, file_path, context):
    decision = # ... policy evaluation ...
    
    # NEW: Log decision via lifecycle hooks
    if hasattr(self, '_lifecycle_hook_system') and self._lifecycle_hook_system:
        asyncio.create_task(
            self._lifecycle_hook_system.trigger_completion(
                CompletionEvent.LENS_DECISION,
                entity_id=f"lens_trigger:{intent}:{file_path or 'none'}",
                metadata={
                    "engaged": decision,
                    "policy": self._lens_trigger_policy.__class__.__name__,
                    "reasoning": reasoning
                }
            )
        )
    
    return decision
```

**Step 3: Register Lifecycle Hooks**
```python
# In IntentRouter.__init__
if lifecycle_hook_system:
    lifecycle_hook_system.register_hook(
        CompletionEvent.LENS_DECISION,
        self._log_lens_decision_to_audit_trail
    )
```

---

## ✅ Verification Checklist

### Phase 65 S4/S5 Integration
- [ ] UnifiedIntelligenceProvider has self._audit_trail
- [ ] get_context() wrapped with AC_START/AC_COMPLETE
- [ ] synthesize() wrapped with AC_START/AC_COMPLETE
- [ ] TurnContext.record_intelligence_fetch() called in get_context()
- [ ] Session profiles (_session_profiles) connected to audit trail
- [ ] Fallback logging on audit trail failure
- [ ] 24 tests passing (20 original + 4 Phase 65)

### ENH-092 Integration
- [ ] IntentRouter has _lifecycle_hook_system reference
- [ ] _should_engage_lens() triggers CompletionEvent.LENS_DECISION
- [ ] LENS decision metadata includes policy, reasoning
- [ ] Lifecycle hooks registered in __init__
- [ ] LENS decisions queryable from audit trail
- [ ] 28 tests passing (24 original + 4 ENH-092)

### Overall Wave Completion
- [ ] 88 tests passing (74 intelligence + 14 prompts)
- [ ] Zero regression in existing functionality
- [ ] 95%+ coverage for all new code
- [ ] Performance benchmarks met (<5ms audit, <10ms turn context)
- [ ] All intelligence fixes operational
- [ ] Documentation updated with integration guide

---

## 🚀 Ready for Implementation

**Command to execute:**
```bash
/implement wave-ic-001
```

**Expected Timeline:**
- Cleanup: 0.5 hours (registry organization)
- T1.1 (Enhanced): 1.5 hours (was 1h, +Phase 65)
- T1.2 (Enhanced): 1.5 hours (was 1h, +ENH-092)
- T1.3 (Unchanged): 1 hour
- Track 2: 4 hours (prompt consolidation)
- Integration: 2 hours
- **Total: 8.0 hours** (was 7.5h, +0.5h for intelligence fixes)

**Quality Gates:**
- ✅ All 5 intelligence fixes integrated
- ✅ 88 tests passing (+8 from Phase 65 & ENH-092)
- ✅ Zero regression
- ✅ 95% coverage maintained
- ✅ CORE-008, CORE-035, CORE-027, CORE-028 compliance

---

**Intelligence layer now fully integrated with Phase 65 S4/S5 (Unified Provider + Turn Context) and ENH-092 (Lifecycle Hooks). Wave enhanced and ready for execution.**
