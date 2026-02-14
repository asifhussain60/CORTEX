# Wave 7 Track 4 Phase 2.1: Detailed Refactoring Plan

**Authority:** Wave 7 Track 4 - Orchestrator Migration  
**Status:** 📋 PLANNED (Ready to Execute)  
**Timeline:** ~15-20 hours (TBD based on prioritization)  
**Start Date:** 2026-02-12 (estimated)

---

## 🎯 Executive Summary

Phase 2.1 addresses complex files that require detailed refactoring rather than simple adapter replacement. Identified during Week 1 of Phase 2 (conservative discovery approach).

**Key Challenge:** ChallengeEngine and similar orchestrators have fundamentally different APIs from their unified replacements, requiring bridge classes rather than simple delegation.

---

## 📊 File Priority Matrix

| File | Module | Priority | Complexity | API Mismatch Severity | Est. Time | ROI Score |
|------|--------|----------|-----------|----------------------|-----------|-----------|
| **recommendation_adapter.py** | MCP Adapters | P2-HIGH | 4/5 | SEVERE (new methods) | 3-4h | 7.5/10 |
| **challenge_engine_plugins.py** | Core Orchestrator | P2-HIGH | 5/5 | SEVERE (architectural) | 4-5h | 8.5/10 |
| **interaction_orchestrator.py** | Core Orchestrator | P2-MED | 4/5 | HIGH (method sigs) | 3-4h | 7/10 |
| **orchestrator_base_protocol.py** | Core Base | P2-MED | 4/5 | MEDIUM (mixins) | 2-3h | 6/10 |
| **challengeengine_adapter.py** | MCP Generated | P3-LOW | 3/5 | HIGH (same module) | 2h | 5/10 |
| **cortex_tools.py** | MCP Tools | P3-LOW | 2/5 | MEDIUM (call sigs) | 1.5h | 4/10 |

---

## 📁 Detailed Analysis

### File 1: recommendation_adapter.py (HIGHEST PRIORITY)

**Location:** `cortex/mcp/adapters/recommendation_adapter.py`  
**Size:** 566 LOC  
**Deprecated Module:** ChallengeEngine → UnifiedQualityAssuranceOrchestrator

**Current API Methods:**
```python
engine.recommend_for_security(cwe_id)       # Security recommendations
engine.recommend_for_solid(violation_type)  # SOLID principle fixes
engine.recommend_for_performance(issue)     # Performance optimizations
engine.recommend_for_compliance(framework)  # Compliance advisories
```

**New API Methods (Unified Orchestrator):**
```python
orchestrator.check_recommendation_safety(recommendation)
orchestrator.generate_challenge(safety_result, challenge_type)
orchestrator.perform_meta_audit(scope, rules)
```

**Mismatch Analysis:**
- ❌ No 1:1 method mapping
- ❌ Input/output structures completely different
- ❌ RecommendationEngine uses specialized Advisor classes
- ❌ Unified orchestrator focuses on safety checks + challenges

**Refactoring Strategy:**
1. Create `RecommendationEngineAdapter` bridge class
2. Map each `recommend_for_*` method to unified equivalents
3. Build result transform layer (old → new format)
4. Use RecommendationEngine for specialized recommendations still
5. Fallback: Keep RecommendationEngine as secondary system

**Timeline:** 3-4 hours  
**Risk:** HIGH (API mismatch is severe)  
**ROI:** 7.5/10 (critical for MCP tool operability)

---

### File 2: challenge_engine_plugins.py (HIGHEST PRIORITY)

**Location:** `cortex/orchestrators/core/challenge_engine_plugins.py`  
**Size:** 350 LOC  
**Deprecated Module:** ChallengeEngine → UnifiedQualityAssuranceOrchestrator

**Current Architecture:**
```python
class DisagreementType(Enum):
    ASSUMPTION_VIOLATION
    EDGE_CASE_MISSED
    PERFORMANCE_CONCERN
    SECURITY_THREAT
    BUSINESS_LOGIC_ERROR

class ChallengePlugin:
    def generate_challenge_for_disagreement(disagreement)
    def get_challenge_context(disagreement)
```

**New Architecture (Unified):**
```python
class ChallengeType(Enum):
    ASSUMPTION
    EDGE_CASE
    PERFORMANCE
    SECURITY
    BUSINESS_LOGIC

def _generate_assumption_challenge(safety_result, context)
def _detect_challenge_type(safety_result)
```

**Refactoring Strategy:**
1. Create enum mapping (DisagreementType → ChallengeType)
2. Build challenge generator bridge class
3. Implement plugin adapters for each challenge type
4. Update integration points in orchestrators
5. Create comprehensive test suite

**Timeline:** 4-5 hours  
**Risk:** CRITICAL (orchestrator core component)  
**ROI:** 8.5/10 (foundational for quality orchestration)

---

### File 3: interaction_orchestrator.py (MEDIUM PRIORITY)

**Location:** `cortex/orchestrators/core/interaction_orchestrator.py`  
**Size:** 280 LOC  
**Deprecated Module:** ChallengeEngine → UnifiedQualityAssuranceOrchestrator

**Current Pattern:**
```python
class InteractionOrchestrator:
    def __init__(self):
        self.challenge_engine = ChallengeEngine()
        self.master = MasterOrchestrator()
    
    def handle_user_interaction(user_response):
        challenge = self.challenge_engine.generate_challenge(...)
        # Process user response based on challenge
```

**Refactoring Approach:**
1. Replace ChallengeEngine with unified orchestrator
2. Update method call signatures
3. Map response handling logic
4. Create compatibility layer for existing code

**Timeline:** 3-4 hours  
**Risk:** MEDIUM (user-facing component)  
**ROI:** 7/10 (improves interaction pattern)

---

### File 4: orchestrator_base_protocol.py (MEDIUM PRIORITY)

**Location:** `cortex/orchestrators/core/orchestrator_base_protocol.py`  
**Size:** 400 LOC  
**Deprecated Module:** ChallengeEngine (used in protocol definitions)

**Issue:** Protocol mixin includes ChallengeEngine methods

**Refactoring Strategy:**
1. Create new protocol mixin for unified challenge API
2. Update base classes to use new protocol
3. Implement backward compatibility wrapper
4. Update all subclasses incrementally

**Timeline:** 2-3 hours  
**Risk:** MEDIUM (architectural impact)  
**ROI:** 6/10 (protocol-level change)

---

### File 5: challengeengine_adapter.py (LOW PRIORITY)

**Location:** `cortex/mcp/adapters/generated/challengeengine_adapter.py`  
**Size:** 300 LOC  
**Type:** Generated adapter code

**Refactoring Strategy:**
1. Regenerate from unified orchestrator template
2. Update method names to new API
3. Minimal manual code changes needed

**Timeline:** 1.5-2 hours  
**Risk:** LOW (generated code)  
**ROI:** 5/10 (auto-generated)

---

## 🔧 Bridge Class Pattern

For complex files, implement this pattern:

```python
class LegacyOrchestrationBridge:
    """
    Bridge between old ChallengeEngine API and new UnifiedQualityAssuranceOrchestrator.
    
    Provides:
    1. Old method signatures (backward compat)
    2. Input/output transformation layer
    3. Fallback to RecommendationEngine where needed
    4. Comprehensive logging for migration tracking
    """
    
    def __init__(self):
        self.unified = get_unified_quality_orchestrator()
        self.fallback_engine = get_recommendation_engine()
        self.deprecation_warnings = 0
    
    def generate_challenge(self, user_request, lens_context=None):
        """OLD API - maps to unified orchestrator"""
        # Transform inputs
        safety_result = self._transform_to_safety_result(user_request)
        
        # Call new API
        challenge = self.unified.generate_challenge(safety_result)
        
        # Transform outputs back to old format
        return self._transform_from_challenge(challenge)
    
    def _transform_to_safety_result(self, user_request):
        """Input transformation"""
        # Map old input → new input structure
        pass
    
    def _transform_from_challenge(self, challenge):
        """Output transformation"""
        # Map new output → old output structure
        pass
```

---

## 📋 Implementation Phases

### Phase 2.1a: Foundation (Hours 1-4)
- ✅ recommendation_adapter.py bridge class
- ✅ Input/output transformation layer
- ✅ Comprehensive test suite
- ✅ Deprecation warning integration

### Phase 2.1b: Core Orchestrator Updates (Hours 5-12)
- ✅ challenge_engine_plugins.py refactoring
- ✅ interaction_orchestrator.py updates
- ✅ orchestrator_base_protocol.py migration
- ✅ Integration tests

### Phase 2.1c: Cleanup & Polish (Hours 13-20)
- ✅ challengeengine_adapter.py regeneration
- ✅ cortex_tools.py import updates
- ✅ Test file migrations
- ✅ Full test suite validation (100% passing)

---

## ✅ Success Criteria

| Criterion | Target |
|-----------|--------|
| **Test Pass Rate** | 99%+ (all Phase 2.1 files) |
| **Deprecation Warnings** | Emit on old API usage |
| **Backward Compatibility** | 100% (old code still works) |
| **Documentation** | Bridge patterns documented |
| **Sunset Readiness** | Ready for 2026-03-31 deprecation removal |

---

## 🚀 Execution Readiness

**Decision Points (Before Starting):**
1. ✅ API incompatibilities analyzed
2. ✅ Bridge class pattern defined
3. ✅ Test approach documented
4. ✅ Timeline estimates validated
5. ✅ ROI scores calculated

**Ready to Execute?** ✅ YES

**Recommended Next Action:** 
Start with recommendation_adapter.py (File 1) for fastest ROI validation, then proceed to challenge_engine_plugins.py for core orchestrator updates.

---

**Prepared:** 2026-02-11  
**Authority:** Wave 7 Track 4 - Phase 2 Conservative Discovery  
**Status:** Ready for Phase 2.1 Execution

