# PHASE 22 Quick Reference: ASK Mode System
**Version:** 1.0 | **Author:** Asif Hussain | **Date:** 2026-02-03

---

## 🎯 ONE-SENTENCE SUMMARY

Educational mode that answers questions about CORTEX with **implementation-verified truth**, progressive disclosure, and intelligent numbered next-step options.

---

## 🚀 QUICK START

### User Experience
```
User: "How does the InteractionOrchestrator work?"

CORTEX ASK:
- Inspects live code in cortex/orchestrators/core/interaction_orchestrator.py
- Verifies against wiring.yaml registration
- Checks test coverage
- Explains at user's knowledge level
- Ends with 5 numbered next steps

User selects: "3. Show me a practical example"

CORTEX ASK:
- Generates example from actual codebase
- Shows real usage patterns
- Highlights integration points
- New set of numbered options
```

### Trigger Patterns
```yaml
Educational Keywords:
  - "ask about {topic}"
  - "explain {concept}"
  - "how does {component} work"
  - "what is {term}"
  - "show me {example}"
  - "walk me through {process}"
  - "why does {behavior}"
  - "difference between {A} and {B}"
```

---

## 📦 CORE COMPONENTS (12 Total)

### Week 1: Foundation (5 components)
```
1. cortex-ask.prompt.md              [Prompt - 400 lines]
2. cortex-ask-coordinator.md         [Agent - 200 lines]
3. truth-verifier.md                 [Agent - 150 lines]
4. EducationalOrchestrator           [Python - 600 lines + 20 tests]
5. TruthVerificationEngine           [Python - 800 lines + 30 tests]
   ImplementationVerifier            [Python - 500 lines + 25 tests]
```

### Week 2: Interaction (4 components)
```
6. NextStepGenerator                 [Python - 400 lines + 20 tests]
7. KnowledgeLevelDetector            [Python - 350 lines + 18 tests]
8. FaultDetectionReporter            [Python - 450 lines + 22 tests]
9. MCP Tools (cortex_ask + verify)   [Python - 550 lines + 27 tests]
```

### Week 3: Enhancement (3 components)
```
10. TutorialSystem                   [Python - 550 lines + 25 tests]
11. ExampleGenerator                 [Python - 400 lines + 20 tests]
12. Integration Tests                [Python - 30 scenarios]
```

---

## 🎨 RESPONSE FORMAT

```markdown
## 🧠 CORTEX ASK
**Author:** Asif Hussain | **Mode:** Educational | **Level:** Intermediate ✅

---

### How InteractionOrchestrator Works

**Implementation Reality:**
InteractionOrchestrator wraps ConversationProtocol and integrates
ChallengeEngine to enforce communication patterns on every turn.

**Evidence:**
- File: `cortex/orchestrators/core/interaction_orchestrator.py` (525 lines)
- Wiring: `cortex/wiring/specifications/wiring.yaml` (line 156)
- Tests: `tests/unit/orchestrators/core/test_interaction_orchestrator.py` (45 tests)
- Integration: MasterOrchestrator (line 372)

**Architecture:**
The InteractionOrchestrator implements a 4-phase cycle:
1. LENS context building (Language→Examination→Navigation→Synthesis)
2. Challenge generation (if CORTEX disagrees with request)
3. Pattern validation (from cortex-registry/interaction/)
4. Response with evidence and options

Key class: InteractionOrchestrator (line 58)
- __init__: Always enables challenges (CORE-029 compliance)
- build_lens_context: Gathers implementation evidence
- generate_challenge: Uses ChallengeEngine for disagreements
- validate_pattern: Checks communication protocol compliance

---

### 🔮 Next Steps

Choose an option to continue learning:

1. **See Real Challenge Flow** - Walk through actual challenge generation with code examples
2. **Understand LENS Context** - Deep dive into how context is built from live code
3. **Explore ChallengeEngine** - Learn the innovation framework for intelligent disagreement
4. **View Integration Pattern** - See how it connects to MasterOrchestrator
5. **Try Building Custom Challenge** - Hands-on tutorial for extending the system

*Tip: Option 3 is perfect if you want to understand CORTEX's innovation capabilities*
```

---

## 🔄 MODE INTEGRATION

### cortex-architect.prompt.md Enhancement
```yaml
Existing Modes:
  AUDIT:  No request / "audit" keyword → Autonomous health scan
  DESIGN: User request → Enhanced + challenge + TDD

NEW Mode:
  ASK:    Educational keywords → Implementation truth + options

Mode Detection:
  if no_request or "audit" in request:
    mode = AUDIT
  elif educational_keyword_detected(request):
    mode = ASK  # NEW
  else:
    mode = DESIGN
```

---

## 🧪 TESTING APPROACH

### Test Categories
```
Unit Tests:       150 tests (90%+ coverage per component)
Integration:      30 tests (end-to-end flows)
Acceptance:       20 tests (user scenarios)
Total:           200 tests
```

### Key Test Scenarios
```python
# Truth Verification
def test_verifies_against_live_code():
    """Ensure claims checked against actual implementation."""
    
# Progressive Disclosure
def test_adapts_to_knowledge_level():
    """Beginner gets simple, Advanced gets detailed."""
    
# Numbered Options
def test_generates_intelligent_next_steps():
    """Context-aware, relevant, actionable options."""
    
# Fault Detection
def test_identifies_implementation_issues():
    """Detects drift, broken wiring, missing tests."""
    
# Integration
def test_works_with_interaction_orchestrator():
    """Seamless integration with existing challenge system."""
```

---

## 📊 KEY METRICS

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Implementation Accuracy** | 95%+ | Truth verification success rate |
| **User Engagement** | 80%+ | % users selecting next step option |
| **Fault Detection** | 90%+ | Issues identified vs total issues |
| **Response Time** | <2s | Simple query latency |
| **Test Coverage** | 90%+ | pytest --cov across all components |

---

## 🛠️ IMPLEMENTATION CHECKLIST

### Day 1-2: Prompts & Agents
- [ ] Create cortex-ask.prompt.md (400 lines)
- [ ] Create cortex-ask-coordinator.md (200 lines)
- [ ] Create truth-verifier.md (150 lines)
- [ ] Integrate into cortex-architect.prompt.md
- [ ] Add ASK mode detection logic

### Day 3-4: Core Orchestrator
- [ ] EducationalOrchestrator (TDD: write 20 tests first)
- [ ] Integration with InteractionOrchestrator
- [ ] Progressive disclosure levels (beginner/intermediate/advanced)
- [ ] Numbered option generation

### Day 5: Truth Verification
- [ ] TruthVerificationEngine (TDD: 30 tests)
- [ ] ImplementationVerifier (TDD: 25 tests)
- [ ] Code vs docs verification
- [ ] Evidence collection system

### Day 6-7: Interactive Features
- [ ] NextStepGenerator (TDD: 20 tests)
- [ ] KnowledgeLevelDetector (TDD: 18 tests)
- [ ] FaultDetectionReporter (TDD: 22 tests)
- [ ] Context tracking across conversation

### Day 8-9: MCP Tools
- [ ] cortex_ask MCP tool (TDD: 15 tests)
- [ ] cortex_verify_claim MCP tool (TDD: 12 tests)
- [ ] MCP catalog registration
- [ ] Integration tests (10 scenarios)

### Day 10-14: Enhancement & Polish
- [ ] TutorialSystem (TDD: 25 tests)
- [ ] ExampleGenerator (TDD: 20 tests)
- [ ] Acceptance tests (20 scenarios)
- [ ] Performance optimization
- [ ] Documentation

---

## 🔗 FILE LOCATIONS

### New Files
```
.github/prompts/cortex-ask.prompt.md
.github/agents/education/cortex-ask-coordinator.md
.github/agents/education/truth-verifier.md

cortex/orchestrators/education/
    __init__.py
    educational_orchestrator.py

cortex/brain/verification/
    __init__.py
    truth_verification_engine.py
    implementation_verifier.py

cortex/brain/education/
    __init__.py
    next_step_generator.py
    knowledge_level_detector.py
    fault_detection_reporter.py
    tutorial_system.py
    example_generator.py

cortex/mcp/tools/
    cortex_ask.py
    cortex_verify_claim.py

tests/unit/orchestrators/education/
    test_educational_orchestrator.py

tests/unit/brain/verification/
    test_truth_verification_engine.py
    test_implementation_verifier.py

tests/unit/brain/education/
    test_next_step_generator.py
    test_knowledge_level_detector.py
    test_fault_detection_reporter.py
    test_tutorial_system.py
    test_example_generator.py

tests/unit/mcp/tools/
    test_cortex_ask.py
    test_cortex_verify_claim.py

tests/integration/education/
    test_ask_mode_flow.py
```

### Modified Files
```
.github/prompts/cortex-architect.prompt.md  (Add ASK mode detection)
cortex/wiring/specifications/wiring.yaml    (Register EducationalOrchestrator)
cortex/mcp/catalog.py                       (Register new MCP tools)
```

---

## 🎯 USAGE EXAMPLES

### Example 1: Simple Question
```
User: "What is the MasterOrchestrator?"

ASK Mode:
1. Inspects cortex/orchestrators/core/master_orchestrator.py
2. Verifies wiring in wiring.yaml
3. Checks test coverage
4. Detects knowledge level: Beginner
5. Responds with simple explanation + evidence
6. Offers 5 next steps:
   - See initialization flow
   - Understand orchestrator registry
   - Learn wiring patterns
   - View practical example
   - Explore related orchestrators
```

### Example 2: Complex Architectural Question
```
User: "How do challenges integrate with the interaction flow?"

ASK Mode:
1. Builds LENS context (InteractionOrchestrator + ChallengeEngine)
2. Inspects both implementations
3. Traces execution flow
4. Detects knowledge level: Advanced
5. Provides detailed architectural explanation with:
   - Class diagrams from live code
   - Sequence flow
   - Integration points
   - Evidence (file paths, line numbers)
6. Offers advanced next steps:
   - Extend challenge types
   - Add custom gates
   - Modify LENS synthesis
   - Build new disagreement detectors
   - Contribute to innovation framework
```

### Example 3: Fault Detection
```
User: "How does the governance system work?"

ASK Mode:
1. Inspects governance components
2. Verifies against documentation
3. DETECTS: 4-layer defense documented but Layer 3 implementation incomplete
4. Responds with:
   - Accurate description of implemented layers
   - Clear identification of gap
   - Recommendation: "Implement Layer 3 post-execution audit"
   - Priority: P1
   - Evidence of missing components
5. Options include:
   - See Layer 1-2 implementations
   - Understand Layer 3 requirements
   - Review governance YAML specifications
   - Help design Layer 3 completion
   - Explore related enforcement patterns
```

---

## 🚨 COMMON PITFALLS

| Pitfall | Mitigation |
|---------|------------|
| **Relying on docs** | Always verify against live code first |
| **Generic options** | Context-aware generation based on user path |
| **Over-correction** | Gentle educational tone, not judgmental |
| **Slow verification** | Cache results, async checking where possible |
| **Knowledge level mismatch** | Track progression, adapt explanations |

---

## 🔮 FUTURE ENHANCEMENTS (Post-Phase 22)

- Interactive quizzes for knowledge validation
- Learning path visualization dashboard
- Progress tracking across topics
- Knowledge graph exploration UI
- Community-contributed tutorials
- AI-generated code examples from live codebase
- Automated drift detection reports
- Predictive next-step recommendations

---

## 📋 APPROVAL CHECKLIST

Before execution:
- [ ] Review PHASE-22-ASK-MODE-SYSTEM.yaml
- [ ] Validate integration with existing phases
- [ ] Confirm resource allocation (2-3 weeks)
- [ ] Approve architectural approach
- [ ] Verify CORE rules compliance
- [ ] Confirm MCP-first design
- [ ] Review testing strategy
- [ ] Validate success metrics

---

## 🎓 LEARNING RESOURCES

**Related Phases:**
- Phase 8: Challenge Orchestrator (innovation framework foundation)
- Phase 19: LENS Unified Intelligence (code inspection capabilities)
- Phase 20: Knowledge Synthesis (company + CORTEX YAMLs)

**Key Files to Study:**
- `cortex/orchestrators/core/interaction_orchestrator.py` (engagement patterns)
- `cortex/orchestrators/core/challenge_engine.py` (innovation framework)
- `.github/prompts/cortex-architect.prompt.md` (mode routing)

**Implementation References:**
- ConversationProtocol for turn-based interaction
- ChallengeEngine for intelligent disagreement
- LENSOrchestrator for code verification

---

**Status:** READY FOR REVIEW ✅  
**Next Action:** Review specification and approve for execution  
**Questions?** Ask in ASK mode! (Once implemented 😊)
