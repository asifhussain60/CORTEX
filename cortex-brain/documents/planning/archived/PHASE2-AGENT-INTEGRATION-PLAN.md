# Phase 2: Agent Integration Plan
**CORTEX Context Management - Agent Integration**  
**Date:** 2025-11-20  
**Author:** Asif Hussain  
**Status:** IN PROGRESS

---

## Executive Summary

Phase 2 integrates the Phase 1 context management foundation with CORTEX's 10 agents and main entry point. This ensures ALL agent responses include standardized context displays showing T1/T2/T3 data, relevance scores, and token usage.

**Goal:** 100% agent coverage with context injection  
**Duration:** 3-4 hours  
**Priority:** P0 (Core functionality)

---

## Agent Integration Matrix

| Agent | Location | Integration Type | Context Priority | Estimated Time |
|-------|----------|------------------|------------------|----------------|
| **IntentRouter** | `cortex_agents/strategic/intent_router.py` | Entry point | T1 (history), T2 (patterns) | 30 min |
| **CodeExecutor** | `cortex_agents/tactical/code_executor.py` | Response wrapper | T1, T3 (metrics) | 20 min |
| **TestGenerator** | `cortex_agents/test_generator/agent.py` | Response wrapper | T2, T3 (coverage) | 20 min |
| **WorkPlanner** | `cortex_agents/work_planner/agent.py` | Response wrapper | T1, T2 | 20 min |
| **Architect** | `cortex_agents/strategic/architect.py` | Response wrapper | T2, T3 | 20 min |
| **ErrorCorrector** | `cortex_agents/error_corrector/agent.py` | Response wrapper | T1, T3 | 20 min |
| **HealthValidator** | `cortex_agents/health_validator/agent.py` | Response wrapper | T3 | 15 min |
| **CommitHandler** | `cortex_agents/tactical/commit_handler.py` | Response wrapper | T1, T3 | 15 min |
| **BrainProtector** | `tier0/brain_protector.py` | Response wrapper | T2 (rules) | 15 min |
| **ScreenshotAnalyzer** | `cortex_agents/screenshot_analyzer.py` | Response wrapper | T1 | 15 min |
| **CortexEntry** | `entry_point/cortex_entry.py` | Orchestration | ALL TIERS | 30 min |

**Total:** 11 components × ~20 min = 3.7 hours

---

## Integration Strategy

### Pattern 1: Entry Point Integration (CortexEntry)

**Location:** `src/entry_point/cortex_entry.py`

**Changes:**
```python
# ADD: Import unified context manager
from src.core.context_management.unified_context_manager import UnifiedContextManager

class CortexEntry:
    def __init__(self, ...):
        # ... existing initialization ...
        
        # NEW: Initialize unified context manager
        self.context_manager = UnifiedContextManager(
            tier1=self.tier1,
            tier2=self.tier2,
            tier3=self.tier3,
            default_token_budget=500
        )
    
    def process(self, user_message, ...):
        # BEFORE routing: Build unified context
        context_data = self.context_manager.build_context(
            query=user_message,
            conversation_id=conversation_id,
            token_budget=500
        )
        
        # Pass context_data to router
        request.context['unified_context'] = context_data
        
        # ... route and execute ...
```

**Why at entry point:**
- Single orchestration point for ALL requests
- Context available before routing decision
- Can influence routing based on context quality
- Centralized token budget enforcement

---

### Pattern 2: Agent Response Wrapper (All Agents)

**Example: IntentRouter**

```python
from src.core.context_management.context_injector import ContextInjector

class IntentRouter(BaseAgent):
    def __init__(self, ...):
        super().__init__(...)
        self.context_injector = ContextInjector(format_style='detailed')
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # ... existing routing logic ...
        
        # NEW: Get unified context from request
        context_data = request.context.get('unified_context', {})
        
        # Build response message
        response_message = self._format_routing_message(routing_decision)
        
        # NEW: Inject context summary
        if context_data:
            response_message = self.context_injector.format_for_agent(
                agent_name="Intent Router",
                response_text=response_message,
                context_data=context_data
            )
        
        return AgentResponse(
            success=True,
            result=routing_decision,
            message=response_message,  # NOW includes context summary
            ...
        )
```

**Apply pattern to:**
- ✅ IntentRouter (entry point)
- ✅ CodeExecutor (tactical)
- ✅ TestGenerator (tactical)
- ✅ WorkPlanner (strategic)
- ✅ Architect (strategic)
- ✅ ErrorCorrector (tactical)
- ✅ HealthValidator (operational)
- ✅ CommitHandler (operational)
- ✅ BrainProtector (tier0)
- ✅ ScreenshotAnalyzer (strategic)

---

### Pattern 3: Agent-Specific Context Filtering

**The ContextInjector already implements this!**

```python
# In context_injector.py:format_for_agent()
agent_contexts = {
    'Code Executor': ['tier1', 'tier3'],     # Recent work + metrics
    'Test Generator': ['tier2', 'tier3'],    # Patterns + coverage
    'Validator': ['tier2', 'tier3'],         # Patterns + metrics
    'Work Planner': ['tier1', 'tier2'],      # History + patterns
    'Architect': ['tier2', 'tier3'],         # Patterns + architecture
}
```

**Result:** Each agent sees the MOST RELEVANT context for their role automatically.

---

## Implementation Phases

### Phase 2.1: Entry Point (30 min)

1. ✅ Update `CortexEntry.__init__()` - Add UnifiedContextManager
2. ✅ Update `CortexEntry.process()` - Build context before routing
3. ✅ Update `CortexEntry._execute_agent()` - Pass context to agents
4. ✅ Add context quality logging
5. ✅ Test basic flow (user message → context → routing → response)

**Success Criteria:**
- Context data available in `AgentRequest.context['unified_context']`
- Token budget enforced (warnings for violations)
- Context summary logged for debugging

---

### Phase 2.2: Strategic Agents (1 hour)

**IntentRouter (30 min):**
- Import ContextInjector
- Add context summary to routing responses
- Show T1 (past routing decisions) + T2 (routing patterns)

**WorkPlanner (15 min):**
- Add context summary to plan responses
- Show T1 (past plans) + T2 (plan patterns)

**Architect (15 min):**
- Add context summary to design responses
- Show T2 (architecture patterns) + T3 (codebase metrics)

---

### Phase 2.3: Tactical Agents (1 hour)

**CodeExecutor (20 min):**
- Add context summary to execution responses
- Show T1 (recent edits) + T3 (file hotspots)

**TestGenerator (20 min):**
- Add context summary to test generation
- Show T2 (test patterns) + T3 (coverage gaps)

**ErrorCorrector (20 min):**
- Add context summary to fix responses
- Show T1 (past errors) + T3 (error patterns)

---

### Phase 2.4: Operational Agents (45 min)

**HealthValidator (15 min):**
- Add context summary to health reports
- Show T3 (metrics + trends)

**CommitHandler (15 min):**
- Add context summary to commit responses
- Show T1 (commit history) + T3 (change patterns)

**BrainProtector (15 min):**
- Add context summary to validation responses
- Show T2 (protection rules)

---

### Phase 2.5: Support Agents (30 min)

**ScreenshotAnalyzer (15 min):**
- Add context summary to analysis
- Show T1 (past screenshots)

**Session Resumer (15 min):**
- Add context summary to resumed sessions
- Show T1 (session history)

---

## Testing Strategy

### Unit Tests (Per Agent)

```python
def test_agent_includes_context_summary():
    """Verify agent response includes context display"""
    agent = IntentRouter(...)
    
    # Mock unified context data
    context_data = {
        'tier1_context': {'recent_conversations': 2},
        'tier2_context': {'matched_patterns': 3},
        'relevance_scores': {'tier1': 0.85, 'tier2': 0.72},
        'token_usage': {'total': 234, 'budget': 500, 'within_budget': True}
    }
    
    request = AgentRequest(
        intent="CODE",
        user_message="Add button",
        context={'unified_context': context_data}
    )
    
    response = agent.execute(request)
    
    # Verify context summary present
    assert "Context Used" in response.message
    assert "Quality:" in response.message
    assert "Recent Work (Tier 1): 2" in response.message
    assert "Learned Patterns (Tier 2): 3" in response.message
    assert "234/500 tokens" in response.message
```

**Apply to all 10 agents.**

---

### Integration Test (End-to-End)

```python
def test_context_flows_through_entire_system():
    """Verify context propagates from entry → router → agent → response"""
    entry = CortexEntry()
    
    response = entry.process("Create tests for auth.py")
    
    # Context should appear in final response
    assert "Context Used" in response
    assert "Quality:" in response
    assert "tokens" in response
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Agent Coverage** | 100% (10/10 agents) | All agents use ContextInjector |
| **Context Visibility** | 100% of responses | Context summary in EVERY response |
| **Token Budget Compliance** | 95% | Warnings for violations, no silent failures |
| **Quality Score** | 8.0+/10 avg | Context quality across 50 test requests |
| **User Satisfaction** | 90%+ | Users understand WHAT context was used |

---

## Rollout Plan

### Week 1: Core Integration
- Day 1: CortexEntry + IntentRouter
- Day 2: Strategic agents (Planner, Architect)
- Day 3: Tactical agents (Executor, Tester, ErrorCorrector)

### Week 2: Operational + Testing
- Day 4: Operational agents (Health, Commit, BrainProtector)
- Day 5: Support agents (Screenshot, Session)
- Day 6: Integration testing + bug fixes
- Day 7: Documentation + user training

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Agent response formatting breaks** | High | Medium | Add unit tests before changes, validate output format |
| **Token budget too restrictive** | Medium | Low | Make budget configurable per agent (500-1000 tokens) |
| **Context summary too verbose** | Medium | Medium | Support 3 formats (detailed/compact/minimal) |
| **Performance degradation** | Low | Low | Use caching from Phase 1, monitor timing |

---

## Next Actions

**Immediate (Starting now):**
1. ✅ Update CortexEntry (entry point integration)
2. ✅ Update IntentRouter (first agent integration)
3. ✅ Run integration test (user message → full flow)
4. ✅ Validate context appears in response

**After validation:**
5. Apply pattern to remaining 9 agents
6. Create unit tests for each agent
7. Run full integration test suite
8. Generate Phase 2 completion report

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Repository:** https://github.com/asifhussain60/CORTEX
