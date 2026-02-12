# Phase 54: MCP Unified Routing & Tool Completion

**Version:** 1.0  
**Created:** 2026-02-10  
**Status:** PLANNED  
**Priority:** P0 - CRITICAL  
**Authority:** cortex-architect.prompt.md v15.3

---

## Executive Summary

**Mission:** Wire ALL CORTEX capabilities through MCP server with MasterOrchestrator as central hub. Ensure 100% tool availability, fix missing dependencies, and update prompts/agents to enforce MCP-FIRST routing.

**Current State:**
- ✅ MCP server running (Pylance-style)
- ✅ 35 tools registered
- ✅ Response format fixed (MCP protocol compliant)
- ⚠️ Only subset accessible via VS Code
- ❌ Missing dependencies (total_recall_agent, etc.)
- ❌ Prompts/agents not enforcing MCP routing

**Target State:**
- ✅ All 35 tools accessible and functional
- ✅ All dependencies resolved
- ✅ All prompts/agents enforce MCP-FIRST
- ✅ Environment checks validate MCP availability
- ✅ Master Orchestrator routes all operations

---

## Phase Overview

| Stage | Focus | Effort | Priority |
|-------|-------|--------|----------|
| **S1** | Fix Missing Dependencies | 8h | P0 |
| **S2** | Complete Tool Implementation | 12h | P0 |
| **S3** | Update Environment Checks | 6h | P0 |
| **S4** | Wire Prompts → MCP | 8h | P0 |
| **S5** | Wire Agents → MCP | 8h | P1 |
| **S6** | Testing & Validation | 10h | P0 |

**Total Effort:** 52 hours  
**Duration:** 2 weeks (with testing)

---

## Stage 1: Fix Missing Dependencies (P0)

### Objective
Resolve all tool dependency issues so 35/35 tools execute successfully.

### Issues Identified

| Tool | Error | Root Cause | Fix |
|------|-------|------------|-----|
| `cortex_total_recall` | No module 'cortex.tools.total_recall_agent' | Missing module | Create or import correct module |
| `cortex_process_request` | 'Err' object has no attribute 'unwrap_err' | Error handling bug | Fix Result type usage |
| `cortex_lens_analyze` | Tool not found | Not exposed to VS Code | Fix tool registration |
| `echo_tool` | Tool not found | Not exposed to VS Code | Fix tool registration |
| `transform_tool` | Tool not found | Not exposed to VS Code | Fix tool registration |

### Tasks

#### Task 1.1: Fix cortex_total_recall Dependencies
**File:** `cortex/mcp/cortex_tools.py`
**Issue:** Line 130 imports missing `cortex.tools.total_recall_agent`

**Resolution Options:**
1. **Option A:** Create `cortex/tools/total_recall_agent.py` wrapper
2. **Option B:** Update import to use existing `TotalRecallAgent` from agents module
3. **Option C:** Implement inline feature discovery

**Recommended:** Option B (use existing agent)

```python
# Change from:
from cortex.tools.total_recall_agent import TotalRecallAgent

# To:
from cortex.agents.intelligence.total_recall_agent import TotalRecallAgent
```

**Testing:**
```python
# Test: mcp_cortex_cortex_total_recall
result = tool.execute(query="MCP tools", scope="all")
assert result["status"] == "success"
```

---

#### Task 1.2: Fix cortex_process_request Error Handling
**File:** `cortex/mcp/cortex_tools.py`  
**Issue:** Lines 60-70 use incorrect Result type methods

**Current Code:**
```python
if result.is_ok():
    output = result.unwrap()
else:
    return {"status": "error", "error": str(result.unwrap_err())}
```

**Problem:** Result object doesn't have `unwrap_err()` method

**Fix:**
```python
if result.is_ok():
    output = result.unwrap()
else:
    error = result.err() if hasattr(result, 'err') else str(result)
    return {"status": "error", "error": error}
```

**Testing:**
```python
# Test: mcp_cortex_cortex_process_request
result = tool.execute(user_request="test", enable_challenge=False)
assert "error" not in result or "unwrap_err" not in result["error"]
```

---

#### Task 1.3: Fix Tool Registry Exposure
**File:** `cortex/mcp/server.py` (tool registration)  
**Issue:** Some tools registered but not exposed to VS Code MCP interface

**Investigation Needed:**
1. Check if VS Code has tool name filters
2. Verify all tools in `list_tools()` output
3. Test tool invocation via JSON-RPC directly

**Potential Fix:**
- Ensure all tools inherit from `Tool` base class correctly
- Verify tool definition schema matches MCP spec
- Add logging to see which tools VS Code queries

---

### Stage 1 Deliverables

- [ ] `cortex_total_recall` executes without import errors
- [ ] `cortex_process_request` executes without Result errors
- [ ] All 35 tools return valid responses (no ImportError/AttributeError)
- [ ] Test suite: 35 tests (one per tool) all passing

---

## Stage 2: Complete Tool Implementation (P0)

### Objective
Ensure all 35 registered tools have complete, tested implementations.

### Tool Audit Matrix

| Tool | Status | Implementation | Tests |
|------|--------|----------------|-------|
| sample_tool | ✅ COMPLETE | Working | ✅ Passes |
| cortex_process_request | ⚠️ PARTIAL | Error handling issue | ❌ Fails |
| cortex_total_recall | ⚠️ PARTIAL | Missing import | ❌ Fails |
| cortex_challenge | ⚪ UNKNOWN | Not tested | ⚪ None |
| cortex_lens_analyze | ⚪ UNKNOWN | Not accessible | ⚪ None |
| ... | | | |

### Tasks

#### Task 2.1: Master Orchestrator Integration
**Objective:** Wire all tools through MasterOrchestrator for unified execution

**Current State:**
- Tools call orchestrators directly
- No unified entry point
- Inconsistent error handling

**Target State:**
- All tools route through MasterOrchestrator
- Consistent error wrapping
- Unified audit logging

**Implementation:**
```python
# In cortex/mcp/cortex_tools.py

class CORTEXProcessRequestTool(Tool):
    def execute(self, user_request: str, context: Optional[Dict] = None, **kwargs):
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        
        master = MasterOrchestrator.instance()
        
        # Route through master orchestrator
        result = master.route_request(
            request_type="PROCESS",
            payload={
                "user_request": user_request,
                "context": context or {},
                "source": "MCP"
            }
        )
        
        return self._wrap_response(result)
```

---

#### Task 2.2: Add Missing Tools
**Tools to implement:**

1. **cortex_validate_holistically** (Phase 48 integration)
   - Calls HolisticValidationOrchestrator
   - Returns validation report + challenge gate

2. **cortex_plan_execute_autonomous** (Phase 49 integration)
   - Multi-stage autonomous execution
   - Progress tracking + checkpointing

3. **cortex_digest_session** (DIGEST mode)
   - Auto-detects chat markers
   - Extracts learnings
   - Updates CORTEX intelligence

---

### Stage 2 Deliverables

- [ ] All 35 tools route through MasterOrchestrator
- [ ] Missing tools implemented (validate_holistically, plan_execute, digest)
- [ ] 100% tool test coverage (35/35 tests passing)
- [ ] Tool catalog documentation updated

---

## Stage 3: Update Environment Checks (P0)

### Objective
Update cortex-environment-setup agent to validate MCP comprehensively.

### File Updates

#### Update 1: `.github/agents/core/cortex-environment-setup.md`

**Add MCP Tool Catalog Check:**
```markdown
### MCP Tool Catalog Validation

After MCP activation check, verify tool catalog:

1. **Query Tool Count:**
   - Expected: 35+ tools (Phase 54 baseline)
   - Critical if: < 30 tools (missing implementations)

2. **Verify Core Tools:**
   - cortex_process_request ✅
   - cortex_challenge ✅
   - cortex_lens_analyze ✅
   - cortex_total_recall ✅

3. **Test Tool Execution:**
   - Run sample_tool as smoke test
   - Verify response format (MCP protocol compliance)
```

**Add Dependency Validation:**
```markdown
### Python Module Dependencies

**MCP-Specific:**
- cortex.agents.intelligence.total_recall_agent
- cortex.orchestrators.core.master_orchestrator
- cortex.governance.enforcement.enforcement_orchestrator

**Check Script:**
```python
python -c "
from cortex.agents.intelligence.total_recall_agent import TotalRecallAgent
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
print('✅ All MCP dependencies available')
"
```
```

---

#### Update 2: `.github/prompts/cortex-architect.prompt.md`

**Add MCP Pre-Flight Section:**
```markdown
## 🚨 MCP PRE-FLIGHT CHECK (ENHANCED - Phase 54)

**BEFORE processing ANY IMPLEMENT/FIX/REFACTOR/AUDIT request:**

```python
# Step 1: Classify intent
intent = classify_user_request()

# Step 2: Verify MCP activation (3-method detection)
is_available, message = verify_mcp_availability(intent)

if not is_available:
    STOP ❌
    Display: MCP setup instructions
    DO NOT PROCEED

# Step 3: Verify tool catalog completeness (NEW)
tool_count = query_mcp_tool_count()

if tool_count < 35:
    WARN ⚠️
    Display: Missing tools report
    Offer: Auto-fix or manual investigation

# Step 4: Test tool execution (NEW)
smoke_test = execute_mcp_sample_tool()

if smoke_test.status != "success":
    STOP ❌
    Display: MCP malfunction detected
    Suggest: Restart MCP server
```
```

---

### Stage 3 Deliverables

- [ ] Updated cortex-environment-setup.md with tool catalog checks
- [ ] Updated cortex-architect.prompt.md with enhanced MCP pre-flight
- [ ] Updated MCP-SETUP-GUIDE.md with troubleshooting section
- [ ] Test: Environment check catches missing tools

---

## Stage 4: Wire Prompts → MCP (P0)

### Objective
Update all prompt files to enforce MCP-FIRST routing.

### Prompt Update Matrix

| Prompt | Current | Target | Priority |
|--------|---------|--------|----------|
| cortex-architect.prompt.md | Partial MCP refs | Full MCP enforcement | P0 |
| CORTEX.prompt.md | Partial MCP refs | Full MCP enforcement | P0 |
| cortex-doc.prompt.md | No MCP refs | Add MCP routing | P1 |
| response-format-standards.md | No MCP refs | Add MCP examples | P2 |

### Tasks

#### Task 4.1: Update cortex-architect.prompt.md

**Sections to Update:**

1. **Quick Commands** (line ~100)
   ```markdown
   | Command | Action | MCP Tool |
   |---------|--------|----------|
   | `/audit` | Autonomous codebase health scan | `cortex_audit_repository` |
   | `/plan` | Phase lifecycle management | `cortex_plan_execute_autonomous` |
   | `/implement {feature}` | TDD implementation | `cortex_process_request` |
   | `/analyze {scope}` | LENS analysis | `cortex_lens_analyze` |
   ```

2. **Interaction Protocol** (line ~800)
   ```markdown
   ### MCP-FIRST Routing (MANDATORY)

   ALL user requests MUST route through MCP tools:
   
   ```
   User Request
         ↓
   Intent Classification
         ↓
   MCP Tool Selection
         ↓
   cortex_process_request(intent, payload)
         ↓
   MasterOrchestrator.route_request()
         ↓
   Specific Orchestrator
         ↓
   MCP Response (content format)
   ```
   ```

3. **FORBIDDEN Operations** (line ~1200)
   ```markdown
   ❌ FORBIDDEN (MCP-FIRST Violations):
   - Direct file operations without MCP
   - Orchestrator imports in prompt context
   - Bypassing cortex_process_request for IMPLEMENT intents
   - Using create_file/replace_string_in_file directly
   ```

---

#### Task 4.2: Update CORTEX.prompt.md

**Add MCP Routing Section:**
```markdown
## 🌐 MCP-FIRST Architecture

**ALL operations route through MCP server:**

| Intent | MCP Tool | Orchestrator |
|--------|----------|--------------|
| IMPLEMENT | cortex_process_request | TDDOrchestrator |
| ANALYZE | cortex_lens_analyze | LENSSynthesis |
| AUDIT | cortex_audit_repository | RepositoryOnboardingOrchestrator |
| CHALLENGE | cortex_challenge | ChallengeEngine |
```

---

### Stage 4 Deliverables

- [ ] cortex-architect.prompt.md: Full MCP enforcement documented
- [ ] CORTEX.prompt.md: MCP routing mandatory
- [ ] All quick commands reference correct MCP tools
- [ ] FORBIDDEN patterns clearly listed

---

## Stage 5: Wire Agents → MCP (P1)

### Objective
Update all agent files to reference and use MCP tools.

### Agent Update Strategy

**Core Agents (P0):**
1. `cortex-mcp-gateway.md` → Already updated (Phase 53)
2. `cortex-environment-setup.md` → Update with tool catalog checks (Stage 3)
3. `cortex-executor.md` → Add MCP tool invocation patterns
4. `cortex-holistic-validator.md` → Reference cortex_validate_holistically tool

**Support Agents (P1):**
5. `cortex-debugger.md` → Add MCP debug tool references
6. `cortex-vacuum.md` → Reference cortex_vacuum tool
7. `cortex-documentation-architect.md` → Add MCP tool catalog generation

### Task 5.1: Update Core Agents

**File:** `.github/agents/core/cortex-executor.md`

**Add Section:**
```markdown
## MCP Tool Invocation Patterns

**Execute implementation via MCP:**
```python
# Pattern 1: Direct tool invocation
result = cortex_process_request(
    user_request="Implement feature X",
    context={"file_path": "cortex/module.py"},
    enable_challenge=True
)

# Pattern 2: Autonomous execution
result = cortex_plan_execute_autonomous(
    phase_id="phase-54",
    stages=[1, 2, 3],
    checkpoint_interval=2
)
```

**Tool Response Handling:**
```python
# MCP returns content format
if "content" in result:
    for item in result["content"]:
        if item["type"] == "text":
            print(item["text"])
```
```

---

### Stage 5 Deliverables

- [ ] Core agents (4) updated with MCP tool references
- [ ] Support agents (3) updated with specific tool usage
- [ ] Agent examples use cortex_* tools consistently
- [ ] Agent index updated with MCP tool mappings

---

## Stage 6: Testing & Validation (P0)

### Objective
Comprehensive testing of all MCP tools and routing workflows.

### Test Suite Structure

```
tests/integration/mcp/
├── test_mcp_tool_catalog.py          # All 35 tools registered
├── test_mcp_tool_execution.py        # All tools execute
├── test_mcp_master_routing.py        # MasterOrchestrator integration
├── test_mcp_error_handling.py        # Error scenarios
└── test_mcp_protocol_compliance.py   # Response format validation
```

### Test Matrix

| Test Category | Tests | Priority |
|---------------|-------|----------|
| **Tool Registration** | 5 | P0 |
| **Tool Execution** | 35 | P0 |
| **Master Routing** | 10 | P0 |
| **Error Handling** | 15 | P0 |
| **Protocol Compliance** | 8 | P1 |
| **Total** | **73 tests** | |

### Task 6.1: Create Tool Catalog Tests

**File:** `tests/integration/mcp/test_mcp_tool_catalog.py`

```python
"""MCP Tool Catalog Integration Tests."""

import pytest
from cortex.mcp.server import MCPServer


class TestMCPToolCatalog:
    """Test MCP tool registration and catalog completeness."""
    
    @pytest.fixture
    def server(self):
        """Create MCP server instance."""
        return MCPServer()
    
    def test_tool_count_complete(self, server):
        """Verify all 35+ tools registered."""
        tools = server.list_tools()
        assert len(tools) >= 35, f"Expected ≥35 tools, got {len(tools)}"
    
    def test_core_tools_registered(self, server):
        """Verify core tools present."""
        tools = server.list_tools()
        tool_names = {t["name"] for t in tools}
        
        core_tools = [
            "sample_tool",
            "cortex_process_request",
            "cortex_total_recall",
            "cortex_challenge",
            "cortex_lens_analyze",
            "cortex_detect_duplicates",
        ]
        
        for tool in core_tools:
            assert tool in tool_names, f"Core tool missing: {tool}"
    
    def test_tool_schemas_valid(self, server):
        """Verify all tools have valid parameter schemas."""
        tools = server.list_tools()
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert isinstance(tool["parameters"], list)
```

---

### Task 6.2: Create Tool Execution Tests

**File:** `tests/integration/mcp/test_mcp_tool_execution.py`

```python
"""MCP Tool Execution Integration Tests."""

import pytest
from cortex.mcp.server import MCPServer


class TestMCPToolExecution:
    """Test all MCP tools execute successfully."""
    
    @pytest.fixture
    def server(self):
        return MCPServer()
    
    def test_sample_tool_execution(self, server):
        """Test sample_tool executes."""
        result = server.call_tool(
            "sample_tool",
            {"input": "test", "mode": "test"},
            "test-001"
        )
        
        assert result.result is not None
        assert "content" in result.result
        assert result.result["isError"] is False
    
    def test_cortex_process_request_execution(self, server):
        """Test cortex_process_request executes without errors."""
        result = server.call_tool(
            "cortex_process_request",
            {"user_request": "test", "enable_challenge": False},
            "test-002"
        )
        
        assert result.result is not None
        # Should not have unwrap_err error
        if "content" in result.result:
            text = result.result["content"][0]["text"]
            assert "unwrap_err" not in text.lower()
    
    # Add 33 more tool-specific tests...
```

---

### Task 6.3: Create Master Routing Tests

**File:** `tests/integration/mcp/test_mcp_master_routing.py`

```python
"""MCP Master Orchestrator Routing Tests."""

import pytest
from cortex.mcp.server import MCPServer
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator


class TestMCPMasterRouting:
    """Test MCP tools route through MasterOrchestrator."""
    
    def test_process_request_routes_to_master(self):
        """Verify cortex_process_request uses MasterOrchestrator."""
        master = MasterOrchestrator.instance()
        
        # Mock master to verify it's called
        called = []
        original_route = master.route_request
        
        def mock_route(*args, **kwargs):
            called.append(True)
            return original_route(*args, **kwargs)
        
        master.route_request = mock_route
        
        # Execute via MCP
        server = MCPServer()
        server.call_tool(
            "cortex_process_request",
            {"user_request": "test"},
            "test-master-001"
        )
        
        # Verify master was invoked
        assert len(called) > 0, "MasterOrchestrator not invoked"
```

---

### Stage 6 Deliverables

- [ ] 73 integration tests created and passing
- [ ] Test coverage ≥ 90% for MCP module
- [ ] CI/CD pipeline includes MCP tests
- [ ] Performance benchmarks for tool execution (< 500ms avg)

---

## Success Metrics

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| **Tools Registered** | 35 | 35 | ✅ 0 |
| **Tools Accessible** | 35 | ~10 | ❌ 25 |
| **Tools Functional** | 35 | 1 | ❌ 34 |
| **Dependencies Resolved** | 100% | ~60% | ❌ 40% |
| **Prompts Updated** | 4 | 0 | ❌ 4 |
| **Agents Updated** | 7 | 2 | ❌ 5 |
| **Tests Passing** | 73 | 0 | ❌ 73 |
| **MCP Pre-Flight Checks** | 100% enforce | ~30% | ❌ 70% |

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **VS Code tool exposure** | High | High | Test JSON-RPC directly, bypass VS Code layer |
| **Missing dependencies** | Medium | High | Audit all imports, create dependency map |
| **Master routing breaks existing** | Low | High | Feature flag, parallel paths during migration |
| **Performance degradation** | Medium | Medium | Benchmark before/after, optimize if > 20% slower |

---

## Implementation Timeline

### Week 1: Foundation (S1-S3)
| Day | Tasks | Owner |
|-----|-------|-------|
| Mon | S1.1: Fix total_recall import | CORTEX |
| Tue | S1.2: Fix process_request error handling | CORTEX |
| Wed | S1.3: Investigate tool exposure | CORTEX |
| Thu | S2.1: Master orchestrator routing | CORTEX |
| Fri | S3: Update environment checks | CORTEX |

### Week 2: Integration (S4-S6)
| Day | Tasks | Owner |
|-----|-------|-------|
| Mon | S4: Update prompts (cortex-architect, CORTEX) | CORTEX |
| Tue | S5: Update core agents (4 agents) | CORTEX |
| Wed | S6.1-S6.2: Create test suite (73 tests) | CORTEX |
| Thu | S6.3: Run full validation | CORTEX |
| Fri | Integration testing + documentation | CORTEX |

---

## Approval & Execution

**Status:** ⏳ Awaiting approval

**Next Steps:**
1. Review plan for completeness
2. Approve Stage 1-3 (P0) for immediate execution
3. Execute Week 1 tasks autonomously
4. Checkpoint after S3, report progress
5. Approve Week 2 execution based on Week 1 success

---

**Authority:** cortex-architect.prompt.md v15.3  
**Mode:** ARCHITECT  
**Phase:** 54 - MCP Unified Routing & Tool Completion
