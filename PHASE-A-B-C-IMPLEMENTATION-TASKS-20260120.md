# CORTEX Architecture Fix - Implementation Task List
**Status:** Phase A/B/C Ready for Execution  
**Date:** 2026-01-20  
**Authority:** ARCHITECTURE-CONFLICT-FIXES-20260120.md

---

## Phase A: Tier Consolidation (1 day)
**Objective:** Eliminate two sources of truth for governance. Consolidate cortex/brain/core/ → cortex_brain/

### Task A1: Delete cortex/brain/core/governance/ directory
**Effort:** 2 hours
**Files to delete:**
- cortex/brain/core/governance/ (entire directory)
- Any imports from cortex.brain.core.governance -> import from cortex_brain.tier0.governance

**Tests:** Run tests to verify governance still works
```bash
pytest tests/ -k governance -v
```

**Acceptance Criteria:**
- [ ] cortex/brain/core/governance/ deleted
- [ ] All imports updated to cortex_brain.tier0.governance
- [ ] Governance tests pass (75+ tests)

---

### Task A2: Move hallucination_prevention to tier2/governance
**Effort:** 3 hours
**Files to move:**
- cortex/brain/core/hallucination_prevention/*.py -> cortex_brain/tier2/hallucination_prevention/*.py (already exists)
- Convert to YAML format for tier system

**Consolidation steps:**
1. Read existing hallucination_prevention Python files from cortex/brain/core/
2. Convert logic to YAML rules format
3. Consolidate to cortex_brain/tier2/governance/safety-rules.yaml
4. Update BrainPopulator to load from tier2/governance/

**Tests:** Run safety/coherence tests
```bash
pytest tests/ -k "hallucination|safety|coherence" -v
```

**Acceptance Criteria:**
- [ ] Python files converted to YAML
- [ ] Consolidated to tier2/governance/safety-rules.yaml
- [ ] BrainPopulator loads safety rules correctly
- [ ] All hallucination prevention tests pass

---

### Task A3: Repoint BrainPopulator imports
**Effort:** 1 hour
**File:** cortex/brain/core/brain_populator.py

**Changes:**
```python
# OLD
from cortex.brain.core.governance import load_rules
from cortex.brain.core.tier_resolver import TierResolver

# NEW
from cortex_brain.tier0.governance import load_rules
from cortex_brain.core.tier_resolver import TierResolver
```

**Tests:** Run orchestrator tests
```bash
pytest tests/ -k "orchestrator|brain_populator" -v
```

**Acceptance Criteria:**
- [ ] All imports in BrainPopulator updated
- [ ] BrainPopulator initializes without errors
- [ ] Orchestrator tests pass (50+ tests)

---

### Task A4: Move tier_resolver.py
**Effort:** 1 hour
**Move:** cortex/brain/core/tier_resolver.py -> cortex_brain/core/tier_resolver.py

**Files to update:**
- Remove from cortex/brain/core/
- Update all imports to new location
- Verify tier system loads correctly

**Tests:** Run tier tests
```bash
pytest tests/ -k "tier" -v
```

**Acceptance Criteria:**
- [ ] tier_resolver.py moved to cortex_brain/core/
- [ ] All imports updated
- [ ] Tier resolution tests pass

---

### Task A5: Verify all tests pass
**Effort:** 1 hour
**Command:**
```bash
pytest tests/ -v --tb=short
```

**Acceptance Criteria:**
- [ ] 4065+ tests collected
- [ ] 100% pass rate (excluding future stubs)
- [ ] 0 import errors
- [ ] No governance-related failures

---

## Phase B: MCP Centralization (2 days)

### Task B1: Create MCP registry.py
**Effort:** 1 day (4-8 hours)
**File to create:** cortex/mcp/registry.py

**Registry structure:**
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {
            # Governance tools (5)
            'query_tool': {'category': 'governance', 'requires_auth': True, 'rules': ['CORE-005']},
            'validate_tool': {'category': 'governance', 'requires_auth': True, 'rules': ['CORE-008']},
            'execute_tool': {'category': 'governance', 'requires_auth': True, 'rules': ['CORE-015']},
            'analyze_tool': {'category': 'governance', 'requires_auth': True, 'rules': ['CORE-020']},
            'report_tool': {'category': 'governance', 'requires_auth': True, 'rules': ['CORE-027']},
            
            # Orchestration tools (4)
            'status_tool': {'category': 'orchestration', 'requires_auth': False},
            'monitor_tool': {'category': 'orchestration', 'requires_auth': False},
            'optimize_tool': {'category': 'orchestration', 'requires_auth': True},
            'diagnose_tool': {'category': 'orchestration', 'requires_auth': True},
            
            # Knowledge tools (3)
            'search_tool': {'category': 'knowledge', 'requires_auth': False},
            'analyze_tool': {'category': 'knowledge', 'requires_auth': False},
            'generate_tool': {'category': 'knowledge', 'requires_auth': True},
            
            # Utility tools (2)
            'echo_tool': {'category': 'utility', 'requires_auth': False},
            'sample_tool': {'category': 'utility', 'requires_auth': False},
        }
    
    def get_tool(self, name: str):
        return self.tools.get(name)
    
    def get_tools_by_category(self, category: str):
        return [name for name, meta in self.tools.items() if meta['category'] == category]
    
    def is_mcp_exposed(self, name: str):
        return name in self.tools
    
    def get_governance_rules(self, name: str):
        tool = self.tools.get(name)
        return tool.get('rules', []) if tool else []
```

**Tests:** Create test_mcp_registry.py
```bash
pytest tests/unit/mcp/test_registry.py -v
```

**Acceptance Criteria:**
- [ ] registry.py created with all 14 tools
- [ ] Tool metadata includes category, auth, governance rules
- [ ] Registry tests pass (10+ tests)
- [ ] Discoverability working

---

### Task B2: Reorganize cortex/mcp/tools/
**Effort:** 4 hours
**Goal:** Organize 14 tools by category

**New structure:**
```
cortex/mcp/tools/
├── governance/
│   ├── __init__.py
│   ├── query_tool.py
│   ├── validate_tool.py
│   ├── execute_tool.py
│   ├── analyze_tool.py
│   └── report_tool.py
├── orchestration/
│   ├── __init__.py
│   ├── status_tool.py
│   ├── monitor_tool.py
│   ├── optimize_tool.py
│   └── diagnose_tool.py
├── knowledge/
│   ├── __init__.py
│   ├── search_tool.py
│   ├── analyze_tool.py
│   └── generate_tool.py
├── utility/
│   ├── __init__.py
│   ├── echo_tool.py
│   └── sample_tool.py
└── __init__.py (imports registry)
```

**Acceptance Criteria:**
- [ ] Tools reorganized by category
- [ ] All 14 tools moved
- [ ] Import paths updated
- [ ] No tools missing

---

### Task B3: Update cortex/mcp/server.py for auto-discovery
**Effort:** 2 hours
**File:** cortex/mcp/server.py

**Changes:**
```python
from cortex.mcp.registry import ToolRegistry

class MCPServer:
    def __init__(self):
        self.registry = ToolRegistry()
        self._load_tools()
    
    def _load_tools(self):
        """Auto-discover and register tools from registry"""
        for tool_name in self.registry.tools:
            tool = self._import_tool(tool_name)
            self.register_tool(tool)
    
    def register_tool(self, tool_name: str):
        tool_meta = self.registry.get_tool(tool_name)
        # Register with MCP protocol
        ...
    
    def get_mcp_exposed_tools(self):
        """Return only MCP-exposed tools (not internal cortex/tools/)"""
        return list(self.registry.tools.keys())
```

**Tests:** Run server tests
```bash
pytest tests/unit/mcp/test_server.py -v
```

**Acceptance Criteria:**
- [ ] Server auto-discovers tools from registry
- [ ] Tool loading working
- [ ] Server tests pass (15+ tests)

---

### Task B4: Separate internal tools (cortex/tools/)
**Effort:** 2 hours
**Goal:** Clearly distinguish internal tools from MCP-exposed tools

**Internal tools to keep (NOT exposed via MCP):**
- cortex/tools/cortex_brain_integration/
- cortex/tools/devx_tools/
- cortex/tools/profiling_tools/
- cortex/tools/other_internal/

**Documentation:**
- Add README to cortex/tools/ explaining these are internal-only
- Add comment to registry explaining which tools are MCP-exposed

**Acceptance Criteria:**
- [ ] Internal tools folder documented as NOT MCP-exposed
- [ ] Clear separation in code comments
- [ ] cortex/mcp/registry.py only includes MCP-exposed tools

---

### Task B5: Verify registry and discovery
**Effort:** 1 hour
**Tests:**
```bash
pytest tests/unit/mcp/ -v
pytest tests/integration/mcp/test_discovery.py -v
```

**Manual verification:**
```python
from cortex.mcp.registry import ToolRegistry
from cortex.mcp.server import MCPServer

registry = ToolRegistry()
assert len(registry.tools) == 14
assert registry.get_tools_by_category('governance') == [5 tools]
assert registry.get_tools_by_category('orchestration') == [4 tools]
assert registry.is_mcp_exposed('query_tool') == True
assert registry.is_mcp_exposed('cortex_brain_integration') == False
```

**Acceptance Criteria:**
- [ ] Registry tests pass (10+ tests)
- [ ] Discovery tests pass (15+ tests)
- [ ] All 14 MCP tools discoverable
- [ ] Internal tools excluded

---

## Phase C: Hardening & Verification (1 day)

### Task C1: Update cortex-impl-map.yaml
**Effort:** 2 hours
**File:** _workspaces/roadmap/cortex-impl-map.yaml

**Updates needed:**
- [ ] Update Phase A completion status
- [ ] Update Phase B completion status
- [ ] Update production_readiness_percent from 36% to 60% (after A) then 95% (after B)
- [ ] Mark impl-arch-011 as UNBLOCKED
- [ ] Mark impl-arch-025 as UNBLOCKED
- [ ] Mark impl-arch-022 as UNBLOCKED
- [ ] Update critical_blockers count: 4 -> 2 (after A) -> 0 (after B)
- [ ] Update blocked_phases count: 3 -> 1 (after A) -> 0 (after B)

---

### Task C2: Verify blocked phases can now proceed
**Effort:** 1 hour
**Action:** Create implementation plans for previously blocked phases

**Phases to verify:**
- [ ] impl-arch-011-hallucination: Can now implement (hallucination_prevention consolidated)
- [ ] impl-arch-022-mcp-compliance: Can now implement (registry created)
- [ ] impl-arch-025-governance-comp: Can now implement (single source of truth)

---

### Task C3: Run full test suite
**Effort:** 2 hours
**Command:**
```bash
pytest tests/ -v --tb=short --co -q | head -20
pytest tests/ -v --tb=short
```

**Verification:**
- [ ] 4065+ tests collected
- [ ] 100% pass rate (excluding design-only stubs)
- [ ] 0 import errors
- [ ] 0 governance errors
- [ ] 0 MCP tool discovery errors

---

### Task C4: Verify production readiness metrics
**Effort:** 1 hour
**Checks:**

```
✅ Single source of truth for governance (Phase A: ✓)
✅ Tier precedence working (Phase A: ✓)
✅ BrainPopulator loads correct location (Phase A: ✓)
✅ MCP tool registry exists (Phase B: ✓)
✅ Tool discovery working (Phase B: ✓)
✅ Tool governance defined (Phase B: ✓)
✅ All blocked phases unblocked (Phase A+B: ✓)
✅ All tests passing (Phase C: ✓)
✅ 100% production readiness (Phase C: ✓)
```

**Acceptance Criteria:**
- [ ] All 9 checks pass
- [ ] production_readiness_percent = 100
- [ ] critical_blockers = 0
- [ ] blocked_phases = 0

---

## Summary of Changes

| Phase | Days | Effort | Deliverables | Result |
|-------|------|--------|--------------|--------|
| **A** | 1 | 8 hrs | Delete duplicates, consolidate tiers | 36% → 60%, 2 phases unblocked |
| **B** | 2 | 16 hrs | Create registry, reorganize tools | 60% → 95%, 1 phase unblocked |
| **C** | 1 | 6 hrs | Update docs, verify tests | 95% → 100%, all ready |
| **TOTAL** | **4** | **30 hrs** | **All architecture fixed** | **100% production ready** |

---

## Success Criteria

### Phase A Complete ✓
- [ ] cortex/brain/core/governance/ deleted
- [ ] hallucination_prevention consolidated to tier2/governance/
- [ ] BrainPopulator repointed to cortex_brain/
- [ ] tier_resolver.py moved to cortex_brain/core/
- [ ] All governance tests pass (75+)
- [ ] Production readiness: 60%
- [ ] Blocked phases: 3 → 1 (impl-arch-022 still blocked)

### Phase B Complete ✓
- [ ] registry.py created with 14 tools
- [ ] Tools organized by category
- [ ] Server auto-discovery working
- [ ] Internal tools separated
- [ ] All MCP tests pass (25+)
- [ ] Production readiness: 95%
- [ ] Blocked phases: 0
- [ ] All 3 previously blocked phases unblocked

### Phase C Complete ✓
- [ ] cortex-impl-map.yaml updated
- [ ] All documents updated
- [ ] Full test suite passes (4065+ tests)
- [ ] Production readiness: 100%
- [ ] Zero architecture conflicts
- [ ] Zero production blockers

---

## Rollback Plan

If any phase fails:
1. Restore from git (all changes tracked)
2. Identify root cause
3. Fix specific issue
4. Retry phase

All changes are incremental and can be rolled back safely.

---

## Execution Notes

- **Sequential:** Must complete Phase A before B, Phase B before C
- **Testing:** Run tests after each task
- **Git commits:** One commit per task (Task A1, A2, etc.)
- **Documentation:** Update ARCHITECTURE-CONFLICT-FIXES-20260120.md as work progresses
- **Communication:** Update cortex-impl-map.yaml after each phase

---

**Status:** Ready to Execute  
**Next Step:** Start Task A1 (Delete cortex/brain/core/governance/)  
**Timeline:** 4 days to 100% production readiness  
**Authority:** Architecture Conflict Analysis + Implementation Review
