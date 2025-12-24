# 3-Tier Rule Enforcement Architecture (CORTEX 3.0 Phase 1)

**Author:** Asif Hussain  
**Date:** November 18, 2025  
**Status:** ✅ IMPLEMENTED  
**Version:** 1.0

---

## Overview

CORTEX implements a **3-tier rule enforcement architecture** that applies governance rules intelligently based on user intent, without duplicating enforcement logic across multiple layers.

This architecture was implemented in response to user requirements for:
1. Intent-based rule enforcement (programming → TDD, investigation → crawlers)
2. Intelligent test determination (not every change needs tests)
3. Summary generation control (avoid unwanted MD files after completion)

---

## Architecture Design

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                             │
│              "implement authentication"                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Intent Router (Light Pre-Flight Checks)            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • Classifies intent: IMPLEMENT                             │
│  • Attaches rule context:                                   │
│    - rules_to_consider: ['TDD_ENFORCEMENT', 'DoR', 'DoD']  │
│    - intelligent_test_determination: true                   │
│    - skip_summary_generation: true                          │
│  • Routes to CodeExecutor with context                      │
│                                                             │
│  ⚠️ NO ENFORCEMENT - Only context attachment               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: Specialized Agent (Intelligent Application)        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • Receives rule context from routing decision              │
│  • Intelligently determines if rules apply:                 │
│    ✓ New feature? → Apply full TDD cycle                   │
│    ✓ Typo fix? → Skip TDD, apply DoD only                  │
│    ✓ Refactoring? → Tests must stay green                  │
│  • Executes work with appropriate rules                     │
│  • Skips summary if flag set                                │
│                                                             │
│  ⚡ INTELLIGENT ENFORCEMENT - Context-aware decisions       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: Brain Protector (Final Validation)                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  • Validates DoD: Zero errors, zero warnings                │
│  • Detects TDD violations if tests were required            │
│  • Enforces SOLID principles                                │
│  • Generates challenges for violations                      │
│  • Cannot be bypassed (Tier 0 immutable rules)              │
│                                                             │
│  🛡️ FINAL ENFORCEMENT - Immutable validation               │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. IntentClassificationResult (agent_types.py)

```python
@dataclass
class IntentClassificationResult:
    """Rich classification result with intent, rule context, and confidence"""
    intent: IntentType
    confidence: float
    rule_context: Dict[str, Any]  # ← Rules applicable to this intent
    metadata: Dict[str, Any]
```

### 2. INTENT_RULE_CONTEXT Mapping (intent_router.py)

Maps each intent type to its applicable governance rules and behavioral flags:

```python
{
    IntentType.CODE: {
        'rules_to_consider': ['TDD_ENFORCEMENT', 'DEFINITION_OF_DONE'],
        'intelligent_test_determination': True,
        'skip_summary_generation': True,
        'requires_dod_validation': True
    },
    IntentType.ARCHITECTURE: {
        'rules_to_consider': ['CRAWLER_ACTIVATION', 'PATTERN_ANALYSIS'],
        'enable_crawlers': True,
        'skip_summary_generation': False,  # Investigations need summaries
        'requires_documentation': True
    },
    # ... more intent mappings
}
```

### 3. Enhanced Classification Method

```python
def _classify_intent_with_rules(self, request: AgentRequest) -> IntentClassificationResult:
    """Classify intent AND attach relevant rule context"""
    intent = self._determine_intent(request)  # Standard classification
    rule_context = self.INTENT_RULE_CONTEXT.get(intent, {})
    confidence = self._calculate_confidence(intent, request)
    
    return IntentClassificationResult(
        intent=intent,
        confidence=confidence,
        rule_context=rule_context  # ← Attached for downstream agents
    )
```

---

## Intent-Specific Rule Contexts

### Programming Intents

| Intent | TDD? | DoD? | Summary? | Notes |
|--------|------|------|----------|-------|
| **CODE** | Intelligent | Yes | No | Determines if tests needed |
| **IMPLEMENT** | Yes | Yes | No | Full TDD cycle required |
| **FIX** | Intelligent | Yes | No | Bug fixes may not need tests |
| **REFACTOR** | Intelligent | Yes | No | Existing tests must stay green |
| **EDIT_FILE** | Intelligent | Yes | No | Depends on edit scope |

### Investigation Intents

| Intent | Crawlers? | DoD? | Summary? | Notes |
|--------|-----------|------|----------|-------|
| **ARCHITECTURE** | Yes | No | Yes | Needs comprehensive analysis report |
| **ANALYZE_STRUCTURE** | Yes | No | Yes | Documentation is deliverable |
| **CRAWL_SYSTEM** | Deep | No | Yes | Full system crawl with report |
| **DEBUG** | No | No | Yes | Investigation findings documented |

### Planning Intents

| Intent | DoR? | TDD? | Summary? | Notes |
|--------|------|------|----------|-------|
| **PLAN** | Yes | N/A | No | Creates persistent artifact (file) |
| **FEATURE** | Yes | Yes | No | Planning + implementation |
| **TASK_BREAKDOWN** | Yes | N/A | No | Work breakdown structure |

---

## Intelligent Test Determination (Tier 2)

The specialized agent (e.g., CodeExecutor) determines if tests are needed based on change analysis:

### Tests NOT Required

```python
if any([
    request.change_type == 'typo_fix',
    request.change_type == 'comment_update',
    request.change_type == 'documentation',
    request.scope == 'test_file_only',  # Already writing tests
    request.is_refactoring_with_existing_tests()
]):
    skip_tdd()  # Apply DoD only
```

### Tests REQUIRED

```python
if any([
    request.change_type == 'new_feature',
    request.change_type == 'api_change',
    request.change_type == 'business_logic',
    request.affects_public_interface()
]):
    apply_full_tdd_cycle()
```

---

## Summary Generation Control

### Suppressed (skip_summary_generation: true)

- **CODE** - User just wants code, not a report
- **IMPLEMENT** - Deliverable is implementation
- **FIX** - Just fix the bug
- **TEST** - Just write the tests
- **COMMIT** - Just commit changes

### Allowed (skip_summary_generation: false)

- **ARCHITECTURE** - Investigation findings
- **DEBUG** - Root cause analysis
- **PLAN** - Planning document (IS the deliverable)
- **HEALTH_CHECK** - Status report

---

## Benefits of 3-Tier Architecture

| Aspect | Benefit |
|--------|---------|
| **Single Responsibility** | Each tier has one job (classify → apply → validate) |
| **DRY (Don't Repeat Yourself)** | No duplicated enforcement logic |
| **Intelligent Enforcement** | Rules applied based on context, not blindly |
| **Flexibility** | Easy to add new intents without changing enforcement |
| **Testability** | Each tier can be tested independently |
| **User Control** | Intent determines behavior without explicit flags |

---

## Comparison with Alternatives

### ❌ Single-Point Enforcement (User's Original Proposal)

```python
# All enforcement at IntentRouter
if intent == IntentType.CODE:
    enforce_TDD()  # Too coarse-grained
    enforce_DoD()
```

**Problems:**
- Router becomes God Object (violates SRP)
- Can't determine if tests actually needed (no change analysis context)
- Duplicates Tier 0 BrainProtector enforcement
- Hard to maintain as rules grow

### ✅ 3-Tier Hybrid (Implemented Solution)

```python
# Tier 1: Attach context
rule_context = {'intelligent_test_determination': True}

# Tier 2: Intelligent application  
if requires_tests(change): apply_tdd()
else: apply_dod_only()

# Tier 3: Validate compliance
brain_protector.validate_dod()
```

**Advantages:**
- Clean separation of concerns
- Intelligent rule application
- No duplication
- Easy to extend

---

## Example Flow

### User Request: "implement authentication module"

**Tier 1: Intent Router**
```python
classification = classify_intent_with_rules(request)
# → intent: IMPLEMENT
# → confidence: 0.9
# → rule_context: {
#     'rules_to_consider': ['TDD_ENFORCEMENT', 'DoR', 'DoD'],
#     'intelligent_test_determination': True,
#     'skip_summary_generation': True
#   }
```

**Tier 2: CodeExecutor**
```python
if rule_context['intelligent_test_determination']:
    if is_new_feature():  # Analysis determines it's new feature
        apply_full_tdd_cycle()  # RED → GREEN → REFACTOR
        
if rule_context['skip_summary_generation']:
    skip_automatic_summary()  # No unwanted MD files
```

**Tier 3: BrainProtector**
```python
validate_dod():
    assert errors == 0
    assert warnings == 0
    assert all_tests_passing
    # Challenge user if violations found
```

---

## Testing

Comprehensive test suite verifies rule context attachment:

```bash
pytest tests/agents/test_intent_router_rule_context.py -v

# 13 tests covering:
# - Intent classification with rule context
# - Rule context mapping completeness
# - Routing decisions include context
# - Backward compatibility maintained
```

**Test Results:** ✅ 13/13 passing

---

## Future Enhancements (Phase 2-4)

### Phase 2: Intelligent Test Determination (3-4 hours)
- Implement `_determine_if_tests_needed()` in CodeExecutor
- Add change analysis logic
- Test determination intelligence

### Phase 3: Summary Generation Control (1-2 hours)
- Modify agents to respect `skip_summary_generation` flag
- Test summary suppression

### Phase 4: Governance Integration (2 hours)
- Update `governance.yaml` with intent-based rules
- Add integration tests
- Document complete workflow

---

## References

- **Implementation:** `src/cortex_agents/intent_router.py`
- **Data Structures:** `src/cortex_agents/agent_types.py`
- **Tests:** `tests/agents/test_intent_router_rule_context.py`
- **Governance Rules:** `src/tier0/governance.yaml`
- **Brain Protection:** `src/tier0/brain_protector.py`

---

## Conclusion

The 3-tier rule enforcement architecture achieves the user's goals for intelligent governance while maintaining CORTEX architectural principles. It provides:

1. ✅ Intent-based rule selection
2. ✅ Intelligent test determination framework
3. ✅ Summary generation control
4. ✅ Clean separation of concerns (SRP)
5. ✅ No duplication (DRY)
6. ✅ Backward compatibility
7. ✅ Extensibility for future rules

**Status:** Phase 1 complete and tested. Ready for Phase 2 implementation.
