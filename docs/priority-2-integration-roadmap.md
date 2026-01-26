# Priority 2 Integration Roadmap - Orchestrator MCP Server

**Created:** 2026-01-26  
**AC-ID:** AC-MCP-ORCHESTRATOR-002  
**Status:** 🟡 IN PROGRESS (80% complete)

---

## Executive Summary

The **Unified Orchestrator MCP Server** has been fully implemented in `/cortex/mcp/orchestrator_mcp_server.py` (550+ LOC, production-ready). This roadmap details the integration work required to wire it into the CORTEX system.

### Timeline
- **Phase 1 (Current):** Foundation + Adapters (~4-5 hours)
- **Phase 2:** API Integration (~3-4 hours)
- **Phase 3:** Testing & Validation (~2-3 hours)
- **Phase 4:** Documentation & SaaS (~1-2 hours)

**Total Estimated Effort:** 10-14 hours over next 2-3 days

---

## Phase 1: Foundation & Orchestrator Adapters (80% Progress)

### ✅ Completed Work

1. **OrchestratorMCPServer Implementation**
   - Location: `cortex/mcp/orchestrator_mcp_server.py`
   - Status: ✅ COMPLETE (550+ LOC, 0 lint errors)
   - Components:
     - `OrchestratorMCPServer` singleton class
     - `IOrchestratorAdapter` interface
     - `ExecutionContext` dataclass with ContextType enum
     - `CapabilityMetadata`, `CapabilityRequest`, `CapabilityResponse` dataclasses
   - Features:
     - Capability registration and discovery
     - Intelligent routing with keyword matching
     - Execution history tracking
     - Health monitoring across all orchestrators
     - Full audit trail support

2. **Module Exports**
   - Location: `cortex/mcp/__init__.py`
   - Status: ✅ COMPLETE
   - Exports: 8 new types
     - `OrchestratorMCPServer`
     - `get_orchestrator_mcp_server`
     - `IOrchestratorAdapter`
     - `ExecutionContext`, `ContextType`
     - `CapabilityMetadata`
     - `CapabilityRequest`, `CapabilityResponse`

3. **Code Quality**
   - Status: ✅ COMPLETE (0 lint errors)
   - Type hints: 100% coverage
   - Google-style docstrings: All public methods
   - Error handling: Complete exception hierarchy
   - Logging: Debug-level instrumentation

### 🟡 Pending Work

#### 1. Create Orchestrator Adapters (5 hours)

Create one adapter for each of the 23 orchestrators implementing `IOrchestratorAdapter`:

**Core Orchestrators (6):**
1. **MasterOrchestrator** → `MasterOrchestratorAdapter`
   - Capabilities: execute_operation, get_status, validate_governance
   - Location: `cortex/orchestrators/core/master_orchestrator.py` (add adapter class)

2. **TDDOrchestrator** → `TDDOrchestratorAdapter`
   - Capabilities: generate_tests, run_tests, validate_tdd
   - Location: `cortex/orchestrators/core/tdd_orchestrator.py` (add adapter class)

3. **IntentRouter** → `IntentRouterAdapter`
   - Capabilities: route_intent, classify_intent, get_routing_stats
   - Location: `cortex/orchestrators/core/intent_router.py` (add adapter class)

4. **InteractionOrchestrator** → `InteractionOrchestratorAdapter`
   - Capabilities: process_user_input, apply_challenge, check_context
   - Location: `cortex/orchestrators/core/interaction_orchestrator.py` (add adapter class)

5. **WorkflowOrchestrator** → `WorkflowOrchestratorAdapter`
   - Capabilities: execute_workflow, define_workflow, monitor_workflow
   - Location: `cortex/orchestrators/core/workflow_orchestrator.py` (add adapter class)

6. **WrappedTDDOrchestrator** → `WrappedTDDOrchestratorAdapter`
   - Capabilities: execute_wrapped_tdd, get_wrapped_status
   - Location: `cortex/orchestrators/core/wrapped_tdd_orchestrator.py` (add adapter class)

**Domain Orchestrators (6):**
7. **RefactoringOrchestrator** → `RefactoringOrchestratorAdapter`
8. **PlanningOrchestrator** → `PlanningOrchestratorAdapter`
9. **DomainOrchestrator** → `DomainOrchestratorAdapter`
10. **ConversationOrchestrator** → `ConversationOrchestratorAdapter`
11. **SeleniumPlaywrightOrchestrator** → `SeleniumPlaywrightOrchestratorAdapter`
12. **(Reserved for future domain orchestrator)**

**Support Orchestrators (11):**
13-23. **OnboardingOrchestrator**, **ToolDiscoveryOrchestrator**, **UpgradeOrchestrator**, **RollbackOrchestrator**, **SetupOrchestrator**, **ComposedOrchestrator**, and 5 more support orchestrators

**Implementation Template:**

```python
# In each orchestrator file, add adapter class

class {Name}OrchestratorAdapter(IOrchestratorAdapter):
    """MCP adapter for {Name}Orchestrator"""
    
    def __init__(self, orchestrator: {OrchestratorClass}):
        self.orchestrator = orchestrator
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Expose orchestrator capabilities"""
        # Return list of CapabilityMetadata for each capability
        pass
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> CapabilityResponse:
        """Execute a capability"""
        # Delegate to orchestrator method
        pass
    
    def is_healthy(self) -> bool:
        """Check health"""
        return True  # or call orchestrator health check
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status"""
        return {"status": "operational"}
```

**Deliverables:**
- [ ] 6 core orchestrator adapters
- [ ] 6 domain orchestrator adapters
- [ ] 11 support orchestrator adapters
- [ ] All adapters registered with MCP server
- [ ] Adapter unit tests (3 tests per adapter)

**Acceptance Criteria:**
- All 23 adapters implement IOrchestratorAdapter interface
- Each adapter exposes 2-5 capabilities
- All adapters properly handle ExecutionContext
- 100% type hints on all adapter methods
- All adapters include error handling

---

#### 2. Wire Adapters into Bootstrap (1.5 hours)

Create bootstrap code that registers all adapters:

**Location:** `cortex/orchestrators/bootstrap.py` (update existing or create new)

**Tasks:**
- [ ] Import all 23 orchestrator adapters
- [ ] Create factory function to instantiate all orchestrators
- [ ] Register each adapter with MCP server in deterministic order
- [ ] Add initialization logging at DEBUG level
- [ ] Add error recovery for failed registrations
- [ ] Return list of registered adapters for validation

**Code Template:**

```python
# cortex/orchestrators/bootstrap.py

from cortex.mcp import get_orchestrator_mcp_server, ExecutionContext, ContextType
from cortex.orchestrators.core import MasterOrchestratorAdapter, TDDOrchestratorAdapter, ...
from cortex.orchestrators.domain import RefactoringOrchestratorAdapter, ...

def bootstrap_orchestrator_mcp_server() -> Dict[str, bool]:
    """Initialize and wire all orchestrators into MCP server"""
    
    mcp_server = get_orchestrator_mcp_server()
    logger = logging.getLogger(__name__)
    
    orchestrators = {
        # Core orchestrators
        "master_orchestrator": (MasterOrchestrator(), MasterOrchestratorAdapter),
        "tdd_orchestrator": (TDDOrchestrator(), TDDOrchestratorAdapter),
        # ... all 23
    }
    
    registration_status = {}
    for name, (orch_instance, adapter_class) in orchestrators.items():
        try:
            adapter = adapter_class(orch_instance)
            success = mcp_server.register_orchestrator(name, adapter)
            registration_status[name] = success
            logger.debug(f"Registered {name}: {success}")
        except Exception as e:
            logger.error(f"Failed to register {name}: {e}")
            registration_status[name] = False
    
    return registration_status
```

**Deliverables:**
- [ ] Bootstrap function with all 23 registrations
- [ ] Error recovery mechanism
- [ ] Registration status reporting
- [ ] Integration with MasterOrchestrator initialization

**Acceptance Criteria:**
- All 23 orchestrators register without errors
- Each registration returns True
- Bootstrap function idempotent (can be called multiple times)
- Comprehensive logging at every step

---

### 3. Update MasterOrchestrator (1.5 hours)

**Location:** `cortex/orchestrators/core/master_orchestrator.py`

**Tasks:**
- [ ] Import OrchestratorMCPServer
- [ ] Add MCP server as instance attribute
- [ ] Call bootstrap_orchestrator_mcp_server() in __init__
- [ ] Update execute_operation() to check MCP server for unknown intents
- [ ] Add `/discover-capabilities` internal endpoint
- [ ] Add error handling for capability execution failures

**Code Snippet:**

```python
class MasterOrchestrator:
    def __init__(self):
        # ... existing initialization
        self.mcp_server = get_orchestrator_mcp_server()
        self._bootstrap_mcp_adapters()
    
    def _bootstrap_mcp_adapters(self):
        """Initialize MCP server with all orchestrators"""
        from cortex.orchestrators.bootstrap import bootstrap_orchestrator_mcp_server
        registration_status = bootstrap_orchestrator_mcp_server()
        logging.info(f"MCP adapters registered: {registration_status}")
    
    def execute_operation(self, intent: str, parameters: Dict[str, Any]):
        """Execute operation - now checks MCP server"""
        # ... existing logic
        
        # If intent not directly handled, check MCP capabilities
        if not self._can_handle_intent(intent):
            capabilities = self.mcp_server.discover_capabilities(
                keyword_filter=[intent]
            )
            if capabilities:
                # Route to best matching capability
                pass
```

**Deliverables:**
- [ ] Updated __init__ method with MCP bootstrap
- [ ] Updated execute_operation with capability routing
- [ ] Error handling for MCP execution
- [ ] Logging at all integration points

---

## Phase 2: API Integration (3-4 hours)

### 1. REST API Endpoints (2 hours)

**Location:** `cortex/api/` (update existing FastAPI setup)

**Endpoints:**
```
GET    /api/mcp/capabilities
       - Discover all available capabilities
       - Params: orchestrator_filter, keyword_filter

GET    /api/mcp/capabilities/{name}
       - Get details of specific capability

POST   /api/mcp/execute
       - Execute a capability
       - Body: CapabilityRequest

GET    /api/mcp/health
       - Get server and orchestrator health status

GET    /api/mcp/history
       - Get execution history
       - Params: limit, orchestrator_filter, success_only

GET    /api/mcp/history/{request_id}
       - Get specific execution record
```

**Implementation:**
- [ ] Create `cortex/api/mcp_routes.py` with FastAPI router
- [ ] Implement all 5 endpoint handlers
- [ ] Add request/response validation
- [ ] Add error handling and status codes
- [ ] Add OpenAPI documentation

---

### 2. CLI Commands (1 hour)

**Location:** `cortex/cli/` (update existing Click setup)

**Commands:**
```
cortex mcp list
  - List all available capabilities

cortex mcp discover <keyword>
  - Discover capabilities by keyword

cortex mcp call <capability_name> <--params JSON>
  - Execute a capability

cortex mcp health
  - Check server health

cortex mcp history <--limit N> <--orchestrator NAME>
  - Show execution history
```

**Deliverables:**
- [ ] CLI command group for MCP operations
- [ ] All 5 commands implemented with Click
- [ ] Help text and examples for each command
- [ ] JSON output formatting option

---

## Phase 3: Testing & Validation (2-3 hours)

### 1. Integration Tests (1.5 hours)

**Location:** `tests/orchestrators/test_mcp_integration.py`

**Test Coverage:**
- [ ] Test adapter registration (all 23)
- [ ] Test capability discovery
- [ ] Test capability execution for each orchestrator
- [ ] Test multi-repo context switching
- [ ] Test health monitoring
- [ ] Test execution history
- [ ] Test error handling
- [ ] Test concurrent executions

**Minimum Test Count:** 30+ tests

---

### 2. End-to-End Tests (1 hour)

**Location:** `tests/e2e/test_mcp_e2e.py`

**Scenarios:**
- [ ] Discover capabilities → Execute capability → Verify result
- [ ] Execute across multiple orchestrators
- [ ] Switch repository contexts
- [ ] Verify audit trail completeness
- [ ] Verify health monitoring accuracy

**Minimum Test Count:** 10+ scenarios

---

### 3. Performance Benchmarks (0.5 hours)

**Metrics:**
- [ ] Capability discovery time (< 100ms)
- [ ] Capability execution latency (< 50ms overhead)
- [ ] Health check time (< 50ms)
- [ ] Memory usage (< 10MB overhead)

---

## Phase 4: Documentation & SaaS (1-2 hours)

### 1. Integration Guide (Already Created)
✅ Location: `docs/ac-mcp-orchestrator-integration-guide.md`

### 2. API Documentation (0.5 hours)
- [ ] Add OpenAPI/Swagger documentation
- [ ] Create API reference with examples
- [ ] Document request/response schemas
- [ ] Add error code reference

### 3. SaaS Architecture Document (1 hour)
- [ ] Location: `docs/04-architecture/saas-orchestrator-deployment.md`
- [ ] Multi-tenancy design
- [ ] ExecutionContext for tenant isolation
- [ ] Deployment topology
- [ ] Security boundaries
- [ ] Scaling strategies

---

## File Modifications Summary

### New Files to Create
1. `cortex/orchestrators/bootstrap.py` - Bootstrap function
2. `cortex/api/mcp_routes.py` - REST API routes
3. `cortex/cli/mcp_commands.py` - CLI commands
4. `tests/orchestrators/test_mcp_integration.py` - Integration tests
5. `tests/e2e/test_mcp_e2e.py` - End-to-end tests
6. `docs/04-architecture/saas-orchestrator-deployment.md` - SaaS documentation

### Files to Modify
1. `cortex/orchestrators/core/master_orchestrator.py` - Add MCP initialization
2. `cortex/orchestrators/core/*.py` - Add adapter classes (21 files)
3. `cortex/api/__init__.py` - Add MCP routes
4. `cortex/cli/__init__.py` - Add MCP commands
5. `cortex/mcp/orchestrator_mcp_server.py` - Already complete ✅

### Total Lines of Code
- New adapters: ~30-40 LOC each × 23 = 700-920 LOC
- Bootstrap: ~150 LOC
- API routes: ~200 LOC
- CLI commands: ~150 LOC
- Tests: ~800 LOC
- **Total New Code: ~2000-2100 LOC**

---

## Success Criteria

### Code Quality
- [ ] 0 lint errors (Pylance strict mode)
- [ ] 100% type hints on public APIs
- [ ] Google-style docstrings on all public methods
- [ ] No code duplication (CORE-035 compliance)

### Functional Requirements
- [ ] All 23 orchestrators discoverable via MCP
- [ ] execute_capability() successfully routes to correct orchestrator
- [ ] Multi-repo context switching functional
- [ ] Execution history accurately tracks all invocations
- [ ] Health status reflects actual orchestrator state

### Performance Requirements
- [ ] Capability discovery < 100ms
- [ ] Capability execution latency < 50ms overhead
- [ ] Health check < 50ms
- [ ] Memory usage < 10MB additional

### Test Coverage
- [ ] 30+ integration tests (all passing)
- [ ] 10+ end-to-end scenarios (all passing)
- [ ] 95%+ code coverage on new code
- [ ] 100% adapter coverage (all 23 adapters tested)

### Documentation
- [ ] Integration guide complete ✅
- [ ] API documentation complete
- [ ] SaaS architecture documented
- [ ] README updated with new capabilities

---

## Risks & Mitigation

### Risk 1: Complex Adapter Implementation
**Mitigation:** Use template, pair-program first 3 adapters, then automate rest

### Risk 2: Integration with MasterOrchestrator
**Mitigation:** Start with minimal changes, add logging at every step, test in isolation first

### Risk 3: Backward Compatibility
**Mitigation:** Keep existing APIs unchanged, add MCP as wrapper, zero breaking changes

### Risk 4: Performance Impact
**Mitigation:** Profile early, optimize routing algorithm, implement caching if needed

---

## Next Immediate Steps (For Next Session)

1. **Start Phase 1.1: Create Adapters**
   - Begin with 3 core adapters (Master, TDD, IntentRouter)
   - Use template provided above
   - Get feedback on first adapter design

2. **Parallel: Create Bootstrap Function**
   - Register all 3 core adapters
   - Add error handling
   - Test registration process

3. **Wire into MasterOrchestrator**
   - Add MCP server import
   - Call bootstrap in __init__
   - Test initialization

4. **Create Basic Integration Test**
   - Test adapter registration
   - Test capability discovery
   - Test single execution

**Estimated Time for Next Session:** 3-4 hours to complete Phase 1 core work

---

## References

- Implementation: `/cortex/mcp/orchestrator_mcp_server.py`
- Module Exports: `/cortex/mcp/__init__.py`
- Integration Guide: `/docs/ac-mcp-orchestrator-integration-guide.md`
- Orchestrators: `/cortex/orchestrators/*/`

---

## Approval & Sign-Off

- **Author:** CORTEX Assistant
- **Status:** 🟡 AWAITING EXECUTION (Phase 1.1: Adapters)
- **Next Review:** After Phase 1 completion
