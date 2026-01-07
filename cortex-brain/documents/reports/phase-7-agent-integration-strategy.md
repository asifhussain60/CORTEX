# Phase 7: Agent Layer Integration with Master Orchestrator

**Date:** January 3, 2026  
**Status:** 📋 DOCUMENTED (Implementation deferred to Phase 10)  
**Author:** Asif Hussain

---

## 🎯 Integration Strategy

### Current Agent Architecture

CORTEX has three specialist agents:
1. **IntentRouter** - Routes user requests to appropriate agents
2. **ErrorCorrector** - Automatically detects and corrects errors  
3. **LearningLibrarian** - (Planned, not yet implemented)

### Integration with Master Orchestrator

**Phase 7 Decision:** Document integration strategy, implement in Phase 10

**Rationale:**
- Master Orchestrator is fully operational and routing all orchestrators
- Agent integration requires careful design to avoid conflicts
- Better to complete all orchestrator migrations first (Phase 6.4-6.5)
- Then integrate agents holistically in Phase 10

---

## 🔄 Proposed Integration Model

### 1. IntentRouter → DEPRECATED (Replaced by Master Orchestrator)

**Current State:**
- IntentRouter used in 25 locations across codebase
- Provides keyword-based intent classification
- Routes to specialist agents

**Phase 10 Migration:**
- Mark IntentRouter as deprecated with clear documentation
- Add deprecation warnings to all IntentRouter methods
- Update callers to use Master Orchestrator routing
- Preserve IntentRouter for backward compatibility (Phase 10.1)
- Full removal in v6.0

**Deprecation Notice Template:**
```python
@deprecated(
    version="5.0",
    reason="Replaced by Master Orchestrator (src/orchestrators/master_orchestrator.py)",
    migration_guide="Use MasterOrchestrator.handle_request() instead"
)
class IntentRouter(BaseAgent):
    """
    DEPRECATED: Use Master Orchestrator for routing.
    
    This agent is maintained for backward compatibility only.
    All new code should use Master Orchestrator.
    
    Migration Guide: https://asifhussain60.github.io/CORTEX/migration/intent-router
    """
```

### 2. ErrorCorrector → Lifecycle Hook Integration

**Current State:**
- Automatically detects and corrects code errors
- Works independently of orchestrators
- Protected paths: CORTEX/tests/, CORTEX/src/cortex_agents/, cortex-brain/

**Phase 10 Integration:**
- Register as `on_error` lifecycle hook in Master Orchestrator
- Trigger on orchestrator execution failures
- Analyze error output and propose fixes
- Respect SKULL rules (TDD_ENFORCEMENT, HOLISTIC_DISCOVERY)

**Integration Points:**
```python
# master-orchestrator.yaml
lifecycle_hooks:
  on_error:
    - name: "error_corrector"
      handler: "src.cortex_agents.error_corrector.ErrorCorrector"
      enabled: true
      priority: 10
      config:
        protected_paths:
          - "CORTEX/tests/"
          - "cortex-brain/"
        auto_fix_enabled: false  # Manual approval required
```

**Workflow:**
1. Orchestrator execution fails
2. Master Orchestrator triggers `on_error` hook
3. ErrorCorrector analyzes error output
4. Proposes fix to user (no auto-apply)
5. User approves → ErrorCorrector applies fix
6. Master Orchestrator retries orchestrator execution

### 3. LearningLibrarian → Post-Execution Tracking

**Planned State:**
- Tracks orchestrator execution patterns
- Learns from successful/failed executions
- Provides recommendations based on history

**Phase 10 Integration:**
- Register as `post_execution` lifecycle hook
- Record orchestrator execution metadata to Tier 1 Working Memory
- Analyze patterns for optimization recommendations
- Feed insights into Master Orchestrator routing decisions

**Integration Points:**
```python
# master-orchestrator.yaml
lifecycle_hooks:
  post_execution:
    - name: "learning_librarian"
      handler: "src.cortex_agents.learning_librarian.LearningLibrarian"
      enabled: true
      priority: 20
      config:
        track_metrics:
          - execution_time
          - artifacts_generated
          - user_satisfaction
        learning_modes:
          - pattern_detection
          - optimization_recommendations
```

**Workflow:**
1. Orchestrator completes execution
2. Master Orchestrator triggers `post_execution` hook
3. LearningLibrarian records execution metadata
4. Analyzes patterns across historical executions
5. Provides optimization recommendations
6. Updates Master Orchestrator routing confidence

---

## 📊 Lifecycle Hook Architecture

### Hook Types

```python
class LifecycleHook(Enum):
    PRE_EXECUTION = "pre_execution"     # Before orchestrator.execute()
    POST_EXECUTION = "post_execution"   # After successful execution
    ON_ERROR = "on_error"               # On execution failure
```

### Hook Registration

```yaml
# cortex-brain/config/master-orchestrator.yaml
lifecycle_hooks:
  pre_execution:
    - name: "validate_dependencies"
      enabled: true
      priority: 10
  
  post_execution:
    - name: "save_artifacts"
      enabled: true
      priority: 10
    
    - name: "learning_librarian"
      handler: "src.cortex_agents.learning_librarian.LearningLibrarian"
      enabled: true
      priority: 20
  
  on_error:
    - name: "log_failure"
      enabled: true
      priority: 10
    
    - name: "error_corrector"
      handler: "src.cortex_agents.error_corrector.ErrorCorrector"
      enabled: true
      priority: 20
```

### Hook Execution Flow

```
Orchestrator Execution Request
  ↓
PRE_EXECUTION Hooks (validation, dependency checks)
  ↓
Orchestrator.execute()
  ↓ (success)          ↓ (failure)
POST_EXECUTION Hooks   ON_ERROR Hooks
  - save_artifacts       - log_failure
  - learning_librarian   - error_corrector
  ↓
Return ExecutionResult
```

---

## 🔧 Implementation Tasks (Phase 10)

### Task 10.1: Deprecate IntentRouter (1 day)
1. Add deprecation decorators to IntentRouter classes
2. Update documentation with migration guide
3. Add warnings to all IntentRouter usage points
4. Create Master Orchestrator migration examples
5. Update tests to use Master Orchestrator

### Task 10.2: ErrorCorrector Integration (1 day)
1. Create `on_error` lifecycle hook interface
2. Implement ErrorCorrector as lifecycle hook handler
3. Add error analysis and fix proposal logic
4. Test with failing orchestrator executions
5. Document error correction workflow

### Task 10.3: LearningLibrarian Implementation (2 days)
1. Design LearningLibrarian architecture
2. Implement execution pattern tracking
3. Create `post_execution` hook handler
4. Build recommendation engine
5. Integrate with Master Orchestrator routing
6. Add Tier 1 Working Memory persistence

### Task 10.4: Lifecycle Hook Framework (1 day)
1. Enhance ExecutionEngine with hook support
2. Add hook registration and discovery
3. Implement hook priority sorting
4. Add hook error handling
5. Create hook configuration validation
6. Document hook development guide

### Task 10.5: Integration Testing (1 day)
1. Test error correction workflow (orchestrator fails → ErrorCorrector proposes fix)
2. Test learning workflow (orchestrator succeeds → LearningLibrarian tracks)
3. Test hook priority ordering
4. Test hook error isolation (one hook fails, others continue)
5. Test Master Orchestrator with full hook pipeline
6. Performance testing (ensure <20ms hook overhead)

---

## ✅ Phase 7 Completion Criteria

**Agent Integration Status:**
- ✅ Integration strategy documented
- ✅ Lifecycle hook architecture designed
- ✅ Implementation tasks defined for Phase 10
- ⏸️ Actual implementation deferred to Phase 10

**Rationale:**
- Master Orchestrator routing is operational
- Agents can integrate via lifecycle hooks without blocking Phase 7
- Better to complete orchestrator migrations first
- Holistic agent integration in Phase 10 ensures consistency

---

## 📚 References

- **Master Orchestrator:** `src/orchestrators/master_orchestrator.py`
- **Lifecycle Hooks:** `src/orchestrators/execution_engine.py`
- **IntentRouter (Legacy):** `src/cortex_agents/intent_router.py`
- **ErrorCorrector:** `src/cortex_agents/error_corrector.py`
- **Configuration:** `cortex-brain/config/master-orchestrator.yaml`

---

**Status:** 📋 DOCUMENTED (Phase 7)  
**Implementation:** Phase 10 (after all orchestrator migrations complete)
