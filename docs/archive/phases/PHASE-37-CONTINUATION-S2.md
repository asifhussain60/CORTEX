# 🔄 PHASE 37 CONTINUATION - STAGE 2 (S2)

## Status Summary

✅ **COMPLETED: Phase 37 Stage 1 - Persona YAML Schema + Loader**
- TDD RED: Written 22 comprehensive tests
- TDD GREEN: All 22 tests passing ✅
- Implementation: PersonaLoader class fully functional with caching
- YAML Schema: All 6 personas configured with valid depth levels

### Test Results
```
22 PASSED tests in test_persona_loader.py (0.17s)
- T1-T4: Initialization & caching (4/4 ✅)
- T5-T10: Persona retrieval (6/6 ✅)
- T11-T14: Depth level retrieval (4/4 ✅)
- T15-T17: Default persona selection (3/3 ✅)
- T18-T20: YAML validation & error handling (3/3 ✅)
- Integration: Full workflow tests (2/2 ✅)
```

### Files Created/Modified

| File | Status | Lines | Purpose |
|------|--------|-------|---------|
| `cortex/orchestrators/persona/models.py` | ✅ | 105 | 5 dataclasses (PersonaConfig, DepthConfig, etc.) |
| `cortex/orchestrators/persona/persona_loader.py` | ✅ | 199 | PersonaLoader class with 8 methods |
| `cortex/orchestrators/persona/personas.yaml` | ✅ | 191 | All 6 personas + 4 depth levels |
| `cortex/orchestrators/persona/test_persona_loader.py` | ✅ | 320 | 22 comprehensive tests |
| `cortex/orchestrators/persona/__init__.py` | ✅ | 20 | Module imports (S2 imports deferred) |

### Git Status
- Commits: 2
  1. `955d3ce26` - Phase 37 S1: Skeleton + models + loader
  2. `59c66160f` - Phase 37 S1: TDD GREEN - All 22 tests passing
- Working tree: ✅ Clean
- Branch: CORTEX

---

## 📋 PHASE 37 S2: RoleResolver + PersonaInjector

**Duration:** 2-3 hours  
**Test Target:** 25 tests  
**Estimated Tokens:** 40-50k

### S2 Objectives

1. **RoleResolver** — Infer persona from context signals
   - Extract role hints from user messages
   - Confidence scoring (0-1.0)
   - Fallback to default (engineer) if low confidence
   - Memory of previous inferences

2. **PersonaInjector** — Apply persona formatting to responses
   - Apply word limits from depth level
   - Enforce show_code rules
   - Format metrics based on persona preferences
   - BLUF vs. full technical output

3. **MasterOrchestrator Integration** — Wire into response pipeline
   - Load PersonaLoader on init
   - Use RoleResolver to infer persona
   - Use PersonaInjector to format response
   - Cache persona per session

### Implementation Plan

#### Step 1: RoleResolver (8-10 tests)
```python
class RoleResolver:
    """Infer user role from context signals"""
    
    def __init__(self, loader: PersonaLoader):
        self.loader = loader
    
    def infer_role(
        self, 
        message: str,
        context: Optional[SessionContext] = None
    ) -> tuple[PersonaId, float]:
        """
        Infer persona ID and confidence from message.
        
        Returns:
            (persona_id, confidence_score 0-1.0)
        """
        # Parse role hints from message
        # Look for keywords (e.g., "engineer", "product owner")
        # Score confidence based on hint strength
        # Return (PersonaId, confidence)
```

#### Step 2: PersonaInjector (10-12 tests)
```python
class PersonaInjector:
    """Apply persona formatting to response text"""
    
    def __init__(self, loader: PersonaLoader):
        self.loader = loader
    
    def inject_persona(
        self,
        response: str,
        persona_id: PersonaId,
        depth: Optional[DepthLevel] = None
    ) -> str:
        """
        Apply persona-specific formatting to response.
        
        - Truncate per word_limit
        - Filter code blocks per show_code
        - Format metrics per metric_types
        - Return formatted response
        """
        # Get persona config
        # Get depth config
        # Apply word limit truncation
        # Filter code/metrics
        # Return formatted response
```

#### Step 3: MasterOrchestrator Integration (5-7 tests)
```python
# In MasterOrchestrator.__init__():
self.persona_loader = PersonaLoader()
self.role_resolver = RoleResolver(self.persona_loader)
self.persona_injector = PersonaInjector(self.persona_loader)

# In MasterOrchestrator.synthesize_response():
# Before returning response:
persona_id, confidence = self.role_resolver.infer_role(user_message)
response = self.persona_injector.inject_persona(
    response, persona_id, depth
)
```

### Test Breakdown

#### RoleResolver Tests (8)
- T23: Infer engineer from "@engineer" mention
- T24: Infer business_leader from "executive" mention
- T25: Return high confidence for explicit role hints
- T26: Return low confidence for ambiguous messages
- T27: Fallback to engineer on no hints
- T28: Parse multiple role signals
- T29: Confidence score in valid range (0-1.0)
- T30: Consistent inferences for same context

#### PersonaInjector Tests (10)
- T31: Truncate response per word limit
- T32: Remove code blocks for non-engineers
- T33: Keep code blocks for engineers
- T34: Include metrics per persona preferences
- T35: Format BLUF for executives (first sentence only)
- T36: Include diagrams for tech_leads
- T37: Handle null word_limit (no truncation)
- T38: Preserve markdown structure
- T39: Performance: inject in <100ms for 1000-line response
- T40: Graceful degradation on invalid persona

#### Integration Tests (5)
- T41: E2E: Message → RoleResolver → PersonaInjector → Response
- T42: Session context carries persona state
- T43: Multiple sequential requests maintain persona
- T44: Manual /persona override changes inferred persona
- T45: Depth override temporary per session

### Success Criteria

✅ **Code Quality:**
- 100% type hints
- Docstrings (Google style)
- <500 LOC per file
- No bare except clauses

✅ **Tests:**
- 25/25 tests passing (TDD GREEN)
- >90% code coverage
- No performance regressions

✅ **Governance:**
- CORE-008: TDD-first (tests before code) ✅
- CORE-029: Response header present
- CORE-035: Single canonical implementation
- MCP-FIRST: All tools via cortex_process_request

✅ **Integration:**
- PersonaLoader fully operational (Phase 37 S1)
- No import errors in __init__.py
- MasterOrchestrator can import and use

---

## 🎯 Execution Commands

### For Next Session (Phase 37 S2):

```bash
# 1. Verify S1 status
cd /Users/asifhussain/PROJECTS/CORTEX
python -m pytest cortex/orchestrators/persona/test_persona_loader.py -v

# 2. Create S2 tests file
# (Will contain test classes for RoleResolver, PersonaInjector, Integration)

# 3. Run S2 tests (TDD RED)
python -m pytest cortex/orchestrators/persona/test_role_resolver.py -v
python -m pytest cortex/orchestrators/persona/test_persona_injector.py -v
python -m pytest cortex/orchestrators/persona/test_persona_integration.py -v

# 4. Implement RoleResolver class
# → All T23-T30 tests GREEN

# 5. Implement PersonaInjector class
# → All T31-T40 tests GREEN

# 6. Implement MasterOrchestrator integration
# → All T41-T45 tests GREEN

# 7. Commit S2 completion
git commit -m "Phase 37 S2: TDD GREEN - RoleResolver + PersonaInjector (25/25 passing)"
```

---

## 📊 Phase 37 Roadmap (Full Specification)

| Stage | Duration | Tests | Status | Notes |
|-------|----------|-------|--------|-------|
| **S1** | 2h | 22 | ✅ COMPLETE | Persona YAML + Loader |
| **S2** | 2-3h | 25 | ⚪ NEXT | RoleResolver + PersonaInjector |
| **S3** | 2h | 20 | ⚪ Planned | /persona, /detail commands |
| **S4** | 1.5h | 15 | ⚪ Planned | NL inference triggers |
| **S5** | 2h | 15 | ⚪ Planned | Persistent storage (SessionContext) |
| **S6** | 2h | 15 | ⚪ Planned | 5 MCP tools |
| **Total** | ~12h | 112 | 22/112 | High ROI (0.85) |

---

## 🔗 Dependencies

**Ready:**
- ✅ PersonaLoader (S1 complete)
- ✅ Models (PersonaId, DepthLevel enums)
- ✅ personas.yaml (all 6 personas configured)

**Required for S2:**
- cortex/orchestrators/ directory structure
- Python 3.9+ (verified)
- pytest framework (verified)

**Blocks Future Phases:**
- S3 depends on S1 + S2 completion (commands need role/injector)
- S4 depends on S2 (NL inference uses RoleResolver)
- S5 depends on S1 + S2 (storage needs to persist persona state)
- S6 depends on S1 + S2 + S3 (MCP tools expose all classes)

---

## 📝 Registry Update Required

After S2 completion, update:
```yaml
cortex-registry/_cortex-master/index.yaml:
  - id: "phase-37"
    status: "in_progress"
    current_stage: "S2"
    stage_progress: "50%"
    tests_passing: 47  # 22 (S1) + 25 (S2)
```

Then commit with:
```bash
git commit -m "Registry: Phase 37 S2 completion (47/112 tests passing)"
```

---

## 🚀 Next Session Entry Point

```
User: "continue phase 37 stage 2"

Agent: Load this continuation file → Create S2 tests → Implement RoleResolver → Implement PersonaInjector → Verify 25/25 tests passing → Update registry → Create S3 continuation
```

**Estimated Total Time:** 12-14 hours for Phase 37 complete (all 6 stages)  
**Estimated Tokens:** 120-150k for Phase 37 + S2-S6 combined  
**ROI Impact:** 0.85 (role-adaptive responses unlock Phase 38 cohesion)

---

**Last Updated:** 2026-02-08 (Post S1 TDD GREEN)  
**Token Budget Used This Session:** ~15k / 200k  
**Token Budget Remaining:** ~185k  
**Session Status:** Silent autonomous execution ✅ CORTEX-049 compliance
