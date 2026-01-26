# Phase 2 Quick Reference Card - Adapter Creation

**Last Updated:** 2026-01-26 | **Status:** 🟡 Ready to Implement

---

## 📋 Your Implementation Order (Recommended)

### Tier 1: Core Orchestrators (Start Here - 3 hours)
```
1. ✅ MasterOrchestratorAdapter
   File: cortex/orchestrators/core/master_orchestrator.py
   Capabilities: 3 (execute_operation, get_status, validate_operation)
   Complexity: Medium
   Reference: See PHASE-2-ADAPTER-IMPLEMENTATION-GUIDE.md

2. TDDOrchestratorAdapter
   File: cortex/orchestrators/core/tdd_orchestrator.py
   Capabilities: 2 (generate_tests, run_tests)
   Complexity: Low
   Reference: See PHASE-2-ADAPTER-IMPLEMENTATION-GUIDE.md

3. IntentRouterAdapter
   File: cortex/orchestrators/core/intent_router.py
   Capabilities: 2 (route_intent, get_routing_stats)
   Complexity: Low
   Reference: Follow MasterOrchestrator pattern
```

### Tier 2: Remaining Core (Next 3 adapters - 2 hours)
```
4. InteractionOrchestratorAdapter
5. WorkflowOrchestratorAdapter
6. WrappedTDDOrchestratorAdapter
```

### Tier 3: Domain & Support (Remaining 17 adapters - 4-5 hours)
```
7-12: Domain Orchestrators (6)
      RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator,
      ConversationOrchestrator, SeleniumPlaywrightOrchestrator, Reserved

13-23: Support Orchestrators (11)
       OnboardingOrchestrator, ToolDiscoveryOrchestrator, UpgradeOrchestrator,
       RollbackOrchestrator, SetupOrchestrator, ComposedOrchestrator, + 5 more
```

---

## 🎯 Minimal Adapter Template (Copy & Paste)

```python
from typing import List, Dict, Any
from datetime import datetime
import time
import logging

from cortex.mcp import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext
)


class {ORCHESTRATOR_NAME}Adapter(IOrchestratorAdapter):
    """MCP adapter for {ORCHESTRATOR_NAME}"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Expose capabilities"""
        return [
            CapabilityMetadata(
                name="{name}/{capability}",
                orchestrator="{orchestrator_slug}",
                description="...",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                routing_keywords=["keyword1", "keyword2"],
                confidence_threshold=0.9,
                tags={"category"}
            ),
            # ... more capabilities
        ]
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> CapabilityResponse:
        """Execute capability"""
        start = time.time()
        try:
            # Call orchestrator method
            result = self.orchestrator.some_method(**parameters)
            return CapabilityResponse(
                request_id=context.session_id,
                success=True,
                result=result,
                duration_ms=(time.time() - start) * 1000,
                orchestrator="{orchestrator_slug}",
                execution_timestamp=datetime.now()
            )
        except Exception as e:
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000,
                orchestrator="{orchestrator_slug}",
                execution_timestamp=datetime.now()
            )
    
    def is_healthy(self) -> bool:
        """Check health"""
        try:
            return self.orchestrator.is_healthy()
        except:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status"""
        try:
            return self.orchestrator.get_status()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
```

---

## 🔧 Implementation Checklist (Per Adapter)

- [ ] **Class Definition**
  - [ ] Class name: `{Name}Adapter(IOrchestratorAdapter)`
  - [ ] Docstring explaining purpose
  - [ ] Proper imports at file top

- [ ] **get_capabilities()**
  - [ ] Returns List[CapabilityMetadata]
  - [ ] 2-5 capabilities minimum
  - [ ] All required fields: name, orchestrator, description, schemas, keywords
  - [ ] Confidence threshold 0.7-0.95
  - [ ] Proper tags for categorization

- [ ] **execute_capability()**
  - [ ] Routes by capability_name
  - [ ] Calls appropriate orchestrator method
  - [ ] Wraps result in CapabilityResponse
  - [ ] Handles exceptions gracefully
  - [ ] Measures execution time
  - [ ] Returns response with all required fields

- [ ] **is_healthy()**
  - [ ] Returns boolean
  - [ ] Calls orchestrator.is_healthy() if available
  - [ ] Exception handling (return False on error)

- [ ] **get_status()**
  - [ ] Returns Dict[str, Any]
  - [ ] Includes health status
  - [ ] Calls orchestrator.get_status() if available
  - [ ] Error handling

- [ ] **Code Quality**
  - [ ] 100% type hints on all method signatures
  - [ ] Google-style docstrings on all methods
  - [ ] 0 lint errors (Pylance strict)
  - [ ] Proper error handling
  - [ ] Execution logging

---

## 🧪 Quick Test Pattern

```python
# In tests/orchestrators/test_mcp_adapters.py

def test_{name}_adapter_capabilities():
    """Test capability discovery"""
    orch = {OrchestratorClass}()
    adapter = {AdapterClass}(orch)
    
    caps = adapter.get_capabilities()
    assert len(caps) >= 2
    assert all(hasattr(c, 'name') for c in caps)

def test_{name}_adapter_execute():
    """Test capability execution"""
    orch = {OrchestratorClass}()
    adapter = {AdapterClass}(orch)
    
    from cortex.mcp import ExecutionContext, ContextType
    context = ExecutionContext(
        context_type=ContextType.SINGLE_REPO,
        repository_path="/tmp"
    )
    
    response = adapter.execute_capability(
        "{name}/{capability}",
        {"key": "value"},
        context
    )
    
    assert isinstance(response.success, bool)
    assert response.orchestrator == "{orchestrator_slug}"

def test_{name}_adapter_health():
    """Test health check"""
    orch = {OrchestratorClass}()
    adapter = {AdapterClass}(orch)
    
    assert isinstance(adapter.is_healthy(), bool)
    assert isinstance(adapter.get_status(), dict)
```

---

## 📊 Capability Naming Convention

```
{orchestrator_slug}/{capability_name}

Examples:
  master/execute_operation
  tdd/generate_tests
  intent/route
  refactor/extract_function
  planning/create_plan
  conversation/process_input
```

---

## ⚡ Quick Wins to Get Started

### Option A: Copy-Paste Approach (Fastest)
1. Copy MasterOrchestratorAdapter code (from guide)
2. Paste at end of master_orchestrator.py
3. Fix orchestrator method names to match actual API
4. Run tests
5. Repeat for next adapter

**Time per adapter:** 10-15 minutes  
**Total for 23:** ~4-6 hours

### Option B: Pattern Recognition Approach (Cleanest)
1. Understand the 4-method pattern
2. Examine target orchestrator class
3. Identify 2-5 main public methods
4. Create capabilities for those methods
5. Wire execute_capability to call them
6. Repeat for next adapter

**Time per adapter:** 15-20 minutes  
**Total for 23:** ~6-8 hours

### Option C: Batch Creation (Most Efficient)
1. Create adapters for 6 core orchestrators
2. Get team feedback on patterns
3. Create adapters for 6 domain orchestrators
4. Create adapters for 11 support orchestrators
5. Do one group review per batch

**Time per adapter:** 10-12 minutes (with momentum)  
**Total for 23:** ~4-5 hours

---

## 🎓 Files You'll Reference Most

```
📖 PHASE-2-ADAPTER-IMPLEMENTATION-GUIDE.md
   ↳ Complete examples with 250+ LOC per orchestrator
   ↳ MasterOrchestratorAdapter fully implemented
   ↳ TDDOrchestratorAdapter pattern example

📖 ac-mcp-orchestrator-integration-guide.md
   ↳ Architecture overview
   ↳ IOrchestratorAdapter interface definition
   ↳ Multi-repo & SaaS examples

📖 priority-2-integration-roadmap.md
   ↳ Overall Phase 2 plan
   ↳ 4 phases of work
   ↳ Success criteria

💻 cortex/mcp/orchestrator_mcp_server.py
   ↳ Reference implementation of MCP server
   ↳ Shows how adapters will be used

💻 cortex/orchestrators/core/master_orchestrator.py
   ↳ Add MasterOrchestratorAdapter here (first adapter)
```

---

## 🚀 Next Actions

### TODAY (Now - 2 hours)
1. Read PHASE-2-ADAPTER-IMPLEMENTATION-GUIDE.md (30 min)
2. Create MasterOrchestratorAdapter (copy-paste + modify, 30 min)
3. Test it with simple pytest (30 min)
4. Commit to git (5 min)

### TOMORROW (4-5 hours)
1. Create TDDOrchestratorAdapter (15 min)
2. Create IntentRouterAdapter (15 min)
3. Create InteractionOrchestratorAdapter (20 min)
4. Create WorkflowOrchestratorAdapter (20 min)
5. Create WrappedTDDOrchestratorAdapter (20 min)
6. Run integration tests (30 min)
7. Create bootstrap function to wire all 6 (30 min)
8. Test bootstrap with pytest (30 min)

### DAY 3 (4-5 hours)
1. Create remaining 17 adapters in batches (3 hours)
2. Run full integration test suite (30 min)
3. Create API endpoints (1-2 hours)
4. Create CLI commands (1 hour)

**Total Time Estimate:** 10-14 hours over 2-3 days

---

## ✅ Success Criteria

After each adapter:
- [ ] 0 lint errors
- [ ] 100% type hints
- [ ] 2+ unit tests passing
- [ ] Docstrings on all methods
- [ ] ExecutionContext properly used

After all 23 adapters:
- [ ] All adapters created & tested
- [ ] 50+ capabilities exposed
- [ ] Bootstrap function wiring all 23
- [ ] Integration tests passing
- [ ] API endpoints created
- [ ] CLI commands created
- [ ] E2E tests passing

---

## 📞 Questions?

See the detailed guides:
- **Implementation:** PHASE-2-ADAPTER-IMPLEMENTATION-GUIDE.md
- **Architecture:** ac-mcp-orchestrator-integration-guide.md
- **Roadmap:** priority-2-integration-roadmap.md
- **Status:** cortex-system-status-report-2026-01-26.md

---

## 🎯 Your Current Progress

```
COMPLETED:
  ✅ OrchestratorMCPServer implementation (550+ LOC)
  ✅ MCP module exports (8 new types)
  ✅ Integration guides (1000+ LOC)
  ✅ Adapter implementation templates (500+ LOC)

IN PROGRESS:
  🟡 Adapter creation (0/23 created)
  
PENDING:
  ⏳ Bootstrap function wiring
  ⏳ API endpoints
  ⏳ CLI commands
  ⏳ Integration testing
  ⏳ E2E testing

EFFORT REMAINING:
  ~ 10-14 hours over 2-3 days
```

---

**Ready? Pick an orchestrator and start with the first adapter!** 🚀
