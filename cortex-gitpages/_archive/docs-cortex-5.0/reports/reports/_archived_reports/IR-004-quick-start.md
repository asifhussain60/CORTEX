# IR-004: Intent Router Implementation - Quick Start Guide

## Current Status
- **Phase**: PHASE-07-INTENT-ROUTER (Holistic Intent Router Intelligence)
- **Progress**: 85.7% (12/14 ACs complete)
- **Previous Work**: LENS Protocol fully implemented (IR-001 through IR-003) - 328 tests passing
- **Next Steps**: IR-004-01 and IR-004-02 (Intent Router Integration)

---

## IR-004-01: Intent Router Implementation

### Purpose
Route approved intents from the LENS protocol to appropriate execution orchestrators based on intent type and context.

### Routing Logic

```python
ROUTING_TABLE = {
    "planning": PlanningOrchestrator,      # Strategic planning intents
    "ado": ADOOrchestrator,                # Azure DevOps integration
    "code": TDDOrchestrator,               # Code implementation/fixes
    "implement": TDDOrchestrator,          # Implementation tasks
    "fix": TDDOrchestrator,                # Bug fixes
    "query": DirectResponse,               # Direct answers (no routing)
    "status": DirectResponse,              # Status inquiries
    "default": InteractionOrchestrator,    # Unknown → ask for clarification
}
```

### Expected Components

**Router Engine**:
- Intent type classification
- Handler lookup and registration
- Routing decision logic
- Fallback handling (default → InteractionOrchestrator)

**Handler Registry**:
- Plugin-style handler registration
- Handler lookup by intent type
- Support for multiple handlers per type (priority-based)

**Route Metadata**:
- Intent type
- Target orchestrator
- Handler configuration
- Routing confidence

### Architecture Pattern

```
ReflectionResponse (from LENS)
    │
    ├─ Extract: intent.type
    │
    ▼
┌─────────────────────────────┐
│  Intent Router              │
│  ├─ Classify intent type    │
│  ├─ Look up handler         │
│  ├─ Validate routing rule   │
│  └─ Route to orchestrator   │
└─────────────────────────────┘
    │
    ├─ planning/ado → PlanningOrchestrator/ADOOrchestrator
    ├─ code/implement/fix → TDDOrchestrator
    ├─ query/status → DirectResponse
    └─ unknown → InteractionOrchestrator (clarify)
```

### Key Integration Points

1. **Input Source**: `ReflectionResponse` from LENS protocol
   - Contains: `intent` (type, details), `challenges`, `recommendations`
   - Status: PENDING_CONFIRMATION (user approved)

2. **Output Destination**: 
   - TDDOrchestrator (for code-related intents)
   - PlanningOrchestrator (for planning intents)
   - ADOOrchestrator (for Azure DevOps intents)
   - InteractionOrchestrator (for clarification needed)

3. **Error Handling**:
   - Unknown intent type → Default to InteractionOrchestrator
   - Missing context → Validation error
   - Ambiguous routing → Ask for clarification

### Expected Test Coverage (~20-25 tests)

**Test Categories**:

1. **Basic Routing** (5 tests)
   - Route planning intent → PlanningOrchestrator
   - Route code intent → TDDOrchestrator
   - Route fix intent → TDDOrchestrator
   - Route query → DirectResponse
   - Route unknown → Default handler

2. **Handler Registry** (4 tests)
   - Register handler for intent type
   - Lookup handler by type
   - Override existing handler
   - List registered handlers

3. **Routing Logic** (4 tests)
   - Classification of intent types
   - Confidence scoring
   - Priority handling (multiple handlers)
   - Ambiguity detection

4. **Integration** (4 tests)
   - Accept ReflectionResponse
   - Extract and validate intent
   - Route and pass context
   - Handle routing errors

5. **Edge Cases** (3 tests)
   - Empty/null intent
   - Special characters in intent type
   - Malformed routing requests

---

## IR-004-02: LENS Integration with Router

### Purpose
Complete end-to-end integration: LENS context building through intent routing to orchestrator execution.

### Full Pipeline

```
┌─────────────────────────────────────────────┐
│  STAGE 1: CONTEXT BUILDING (LENS)           │
│  ├─ LENSContextBuilder                      │
│  └─ KnowledgeGraph                          │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  STAGE 2: INTENT REFLECTION (LENS)          │
│  ├─ ReflectionEngine                        │
│  └─ ReflectionResponse                      │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│  STAGE 3: RESPONSE FORMATTING (LENS)        │
│  ├─ LENSResponseFormatter                   │
│  └─ UserApprovalGate                        │
└─────────────────────────────────────────────┘
    │ (User Approves)
    ▼
┌─────────────────────────────────────────────┐
│  STAGE 4: INTENT ROUTING (NEW)              │
│  ├─ IntentRouter                            │
│  └─ HandlerRegistry                         │
└─────────────────────────────────────────────┘
    │
    ├─ planning → PlanningOrchestrator
    ├─ ado → ADOOrchestrator
    ├─ code/fix → TDDOrchestrator
    └─ default → InteractionOrchestrator
```

### Expected Test Coverage (~15-20 tests)

**Test Categories**:

1. **End-to-End Flow** (4 tests)
   - Build → Reflect → Format → Route complete pipeline
   - Multiple routing paths
   - Approval workflow
   - Rejection workflow

2. **Data Integrity** (3 tests)
   - Context preserved through pipeline
   - Intent information maintained
   - Metadata integrity

3. **Cross-Component Integration** (3 tests)
   - LENS → Router handoff
   - Context availability to orchestrator
   - Challenge/recommendation propagation

4. **Workflow Validation** (3 tests)
   - Approval gates work
   - Routing decisions correct
   - Orchestrator receives proper context

5. **Performance** (2 tests)
   - Full pipeline < 2 seconds
   - Router response time acceptable

---

## Development Plan for IR-004

### Phase 1: IR-004-01 Implementation (Est. 45 min)

1. **Create Test Suite** (15 min)
   - Create `tests/unit/core/intent/test_intent_router.py`
   - 20-25 comprehensive test cases
   - Cover all routing paths and edge cases

2. **Implement Router** (20 min)
   - Create `src/core/intent/intent_router.py`
   - `IntentRouter` class with routing logic
   - `HandlerRegistry` for pluggable handlers
   - Support for all required orchestrators

3. **Module Integration** (10 min)
   - Add exports to `src/core/intent/__init__.py`
   - Update module documentation
   - Verify all 25 tests pass

4. **Git Checkpoint** (5 min)
   - Commit with message: "IR-004-01: Intent Router Implementation - XX/XX tests"
   - Update roadmaps

### Phase 2: IR-004-02 Integration (Est. 30 min)

1. **Create Integration Tests** (10 min)
   - Create `tests/unit/core/intent/test_router_integration.py`
   - 15-20 end-to-end test scenarios
   - Full pipeline validation

2. **Integration Code** (10 min)
   - Wire up router to LENS protocol output
   - Validation layer for routing decisions
   - Error handling and fallbacks

3. **Verification & Commit** (10 min)
   - All 20 tests passing
   - Commit: "IR-004-02: LENS Integration with Router - XX/XX tests"
   - Final roadmap update to 100% (14/14 ACs)

### Phase 3: Phase Lock (Est. 5 min)

1. Run complete PHASE-07 test suite: All 350+ tests
2. Verify git history is clean
3. Create final phase completion tag
4. Document completion status

---

## Key Files to Reference

**Completed LENS Components**:
- `src/core/intent/lens_context_builder.py` - Context aggregation
- `src/core/intent/lens_response_formatter.py` - Response formatting
- `src/core/intent/lens_protocol.py` - Core reflection engine
- `tests/unit/core/intent/test_lens_*.py` - Comprehensive test suites

**Orchestrator Locations**:
- `src/orchestrators/` - Look for orchestrator base classes
- Check what orchestrators are already available
- Plan routing targets accordingly

**Module Exports**:
- `src/core/intent/__init__.py` - Current exports
- Will need to add `IntentRouter` and related classes

---

## Quick Reference: TDD Pattern Used

1. **Create test file first** (empty implementation)
2. **Run tests** (all fail - RED)
3. **Implement functionality** (make tests pass - GREEN)
4. **Refactor** (improve code quality - REFACTOR)
5. **Commit** to git with detailed message
6. **Update roadmaps** with progress

---

## Success Criteria

**IR-004-01: Success**:
- ✅ 20-25 tests covering all routing paths
- ✅ All tests passing (100%)
- ✅ Handler registry functional
- ✅ Routing to all 4 target orchestrators works
- ✅ Git commit created

**IR-004-02: Success**:
- ✅ 15-20 end-to-end tests
- ✅ Full pipeline working
- ✅ Data integrity maintained
- ✅ All tests passing (100%)
- ✅ PHASE-07 at 100% (14/14 ACs)

**PHASE-07 Lock**: 
- ✅ 14/14 ACs complete
- ✅ 350+ tests all passing
- ✅ Full governance compliance
- ✅ Clean git history

---

## Notes

- The existing LENS components (IR-001 through IR-003) are well-tested and stable
- Focus on creating a clean, extensible router that integrates smoothly
- Use the same testing patterns as previous ACs for consistency
- Keep routing logic simple and clear for maintainability
- Consider future extensibility for new orchestrators

**Estimated Total Time for IR-004**: 1-1.5 hours  
**Target Completion**: This session if momentum continues  
**Current Test Pass Rate**: 328/328 (100%) ✅
