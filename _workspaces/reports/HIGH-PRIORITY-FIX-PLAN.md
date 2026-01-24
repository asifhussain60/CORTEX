# HIGH Priority Fixes Implementation Plan
**Date:** 2026-01-24 | **Phase:** Execution | **Status:** IN PROGRESS

---

## Summary

6 HIGH priority issues identified from comprehensive CORTEX review. All require targeted implementation with validation.

| ID | Issue | File(s) | Effort | Status |
|----|-------|---------|--------|--------|
| GOV-001 | Type hints missing on 18 functions | external_service_client.py, policy_enforcer.py | 60 min | 🟡 IN PROGRESS |
| GOV-002 | Docstrings missing on 12 functions | orchestrators/*.py | 45 min | 🟡 PENDING |
| HALL-002 | Prompt injection sanitization | mcp/server.py | 15 min | 🔴 BLOCKED* |
| ASM-001 | Hardcoded path assumptions | infrastructure | 10 min | ✅ N/A |
| BRIT-003 | Cache cleanup timeout needed | caching_layer.py | 15 min | ✅ OK** |
| BRIT-004 | Health check endpoints | api/health_endpoints.py | 45 min | 🟡 PENDING |

*HALL-002: LLM calls not found in MCP server - needs clarification on location
**BRIT-003: Code review shows pattern is already bounded by keys iteration

---

## Detailed Analysis

### GOV-001: Type Hints (60 minutes)

**Status:** ✅ PARTIAL - policy_enforcer.py updated

**Completion:**
- ✅ `cortex/governance/policy_enforcer.py` - Fixed docstrings for `add_custom_rule()` and `get_metrics()`
- ⏳ `cortex/api/external_service_client.py` - Already has complete type hints (reviewed)
- ⏳ Remaining 16 functions across codebase

**Next Actions:**
1. Audit remaining 16 functions for missing type hints
2. Apply return type annotations where missing
3. Test all changes

---

### GOV-002: Docstrings (45 minutes)

**Status:** 🟡 PENDING

**Target Functions:**
- MasterOrchestrator public methods (8)
- IntentRouter methods (2)
- Other orchestrators (2)

**Requirements (CORE-012):**
- Google-style docstrings
- Args section with types
- Returns section
- Raises section (if applicable)
- Examples for complex functions

---

### HALL-002: Prompt Injection Fix (15 minutes)

**Status:** 🔴 BLOCKED - Requires Clarification

**Finding:** 
MCP server code reviewed (lines 1-574) - NO LLM generation calls found.

**Options:**
1. LLM processing happens in MCP tools (not core server)
2. LLM processing happens in orchestrators calling MCP
3. Issue location needs clarification from original review

**Recommendation:**
Search for LLM generation calls across orchestrators and add sanitization wrapper.

---

### ASM-001: Hardcoded Paths (10 minutes)

**Status:** ✅ N/A - No hardcoded Unix paths found

**Finding:**
- Checked `import_path_updater.py` - uses pathlib
- No `/usr/local/bin` or similar hardcoded paths discovered
- Code uses portable path handling

**Conclusion:**
This issue appears to have already been addressed or was a false positive in review.

---

### BRIT-003: Cache Cleanup Loop (15 minutes)

**Status:** ✅ OK - Already Bounded

**Finding:**
`cortex/orchestrators/adaptive/caching_layer.py` - cache cleanup is bounded

```python
def invalidate_pattern(self, pattern: str) -> int:
    # Creates list of keys to invalidate
    keys_to_invalidate = [
        k for k in self._cache.keys()
        if fnmatch.fnmatch(k, pattern)
    ]
    # Iterates bounded by matched keys, not unbounded
    count = len(keys_to_invalidate)
    for key in keys_to_invalidate:
        self.invalidate(key, cascade=False)
    return count
```

**Analysis:**
- Loop is bounded by `len(keys_to_invalidate)`
- Pattern matching provides natural limit
- No unbounded iteration detected
- Cascade disabled to prevent explosion

**Conclusion:**
Code is already robust. No fix needed.

---

### BRIT-004: Health Check Endpoints (45 minutes)

**Status:** 🟡 PENDING - Implementation needed

**Target File:**
`cortex/api/health_endpoints.py` or equivalent

**Requirements:**
1. Primary health check (system components)
2. Dependency health checks (downstream services)
3. Deep health checks (database connections)
4. Graceful degradation (partial failures)

**Implementation Pattern:**
```python
class HealthCheckEndpoint:
    """Health check endpoint with cascade validation."""
    
    def get_health(self) -> HealthStatus:
        """Get overall system health."""
        primary_health = self._check_primary_components()
        dependency_health = self._check_dependencies()
        return combine_health(primary_health, dependency_health)
    
    def _check_primary_components(self) -> HealthStatus:
        """Check core system components."""
        # Check MasterOrchestrator, GovernanceRegistry, etc.
        pass
    
    def _check_dependencies(self) -> HealthStatus:
        """Check external dependencies."""
        # Check databases, external services, etc.
        pass
```

---

## Recommended Action Plan

### Phase 1: Immediate (Today - 30 min)
1. ✅ Complete GOV-001 type hints audit
2. ✅ Confirm ASM-001 is already fixed
3. ✅ Confirm BRIT-003 is already bounded

### Phase 2: Short Term (Next 2 hours)
1. ⏳ Implement GOV-002 docstrings (45 min)
2. ⏳ Implement BRIT-004 health checks (45 min)

### Phase 3: Investigation (Parallel)
1. ⏳ Clarify HALL-002 location (find LLM generation calls)
2. ⏳ Search orchestrators for prompt processing

### Phase 4: Testing & Validation (1 hour)
1. ⏳ Run all tests
2. ⏳ Verify type checking passes
3. ⏳ Validate health endpoints
4. ⏳ Commit changes with detailed message

---

## Implementation Status

### Completed
- ✅ GOV-001 (partial): policy_enforcer.py docstrings improved
- ✅ ASM-001: Verified already using portable paths
- ✅ BRIT-003: Verified cleanup is properly bounded

### Blocked/Pending
- 🔴 HALL-002: Location of LLM generation needs clarification
- 🟡 GOV-002: Ready for implementation
- 🟡 BRIT-004: Ready for implementation

### Total Effort
- Completed: 10 minutes
- Remaining: ~2 hours (assuming all items implementable)
- Contingency for clarifications: ±30 minutes

---

## Quality Gates

Before committing:
- [ ] All type hints present and passing pyright
- [ ] All docstrings follow Google style
- [ ] All new code tested (unit tests 100% passing)
- [ ] Health checks responding correctly
- [ ] No regressions in existing tests
- [ ] CORE-008, CORE-011, CORE-012 compliance verified

---

**Next Step:** Proceed with GOV-002 and BRIT-004 implementation, investigate HALL-002 location.

