# PHASE 22 Implementation Summary: ASK Mode System
**Generated:** 2026-02-03  
**Status:** SPECIFICATION COMPLETE ✅  
**Ready for:** Review and Approval

---

## 🎯 EXECUTIVE SUMMARY

**PHASE 22** introduces **ASK Mode** — an educational interaction system that provides **implementation-verified truth** about CORTEX architecture with progressive disclosure and intelligent next-step guidance.

**Key Innovation:** Unlike traditional documentation, ASK mode ALWAYS verifies claims against live code, detects documentation drift, and guides users through numbered learning paths.

---

## 📦 DELIVERABLES CREATED

### Documentation (3 files)

| File | Lines | Purpose |
|------|-------|---------|
| `PHASE-22-ASK-MODE-SYSTEM.yaml` | 850 | Complete specification |
| `PHASE-22-QUICK-REFERENCE.md` | 600 | Implementation guide |
| `.github/prompts/cortex-ask.prompt.md` | 850 | ASK mode prompt |

### Agent Specifications (2 files)

| File | Lines | Purpose |
|------|-------|---------|
| `.github/agents/education/cortex-ask-coordinator.md` | 450 | Query routing agent |
| `.github/agents/education/truth-verifier.md` | 500 | Implementation verification agent |

### Total Documentation: **3,250 lines** of comprehensive specifications

---

## 🏗️ ARCHITECTURE OVERVIEW

### Mode Integration

```
cortex-architect.prompt.md
    ├── AUDIT Mode (autonomous health scan)
    ├── DESIGN Mode (enhanced request + challenge + TDD)
    └── ASK Mode (NEW - educational truth-based interaction)
```

### Component Stack

```
┌─────────────────────────────────────────────┐
│         cortex-ask.prompt.md                │  ← User-facing prompt
├─────────────────────────────────────────────┤
│  cortex-ask-coordinator.md (Agent)          │  ← Query routing
├─────────────────────────────────────────────┤
│  EducationalOrchestrator (Python)           │  ← Core logic
│    ├── KnowledgeLevelDetector               │
│    ├── NextStepGenerator                    │
│    └── FaultDetectionReporter               │
├─────────────────────────────────────────────┤
│  TruthVerificationEngine (Python)           │  ← Implementation checks
│    └── ImplementationVerifier               │
├─────────────────────────────────────────────┤
│  InteractionOrchestrator (Existing)         │  ← Challenge system
│  ChallengeEngine (Existing)                 │  ← Innovation framework
│  LENSOrchestrator (Existing)                │  ← Code inspection
├─────────────────────────────────────────────┤
│  MCP Tools                                  │
│    ├── cortex_ask                           │
│    └── cortex_verify_claim                 │
└─────────────────────────────────────────────┘
```

---

## 🚀 IMPLEMENTATION PLAN

### Week 1: Foundation (100 hours)
- **Days 1-2:** Prompt + Agent Specs (DONE ✅)
- **Days 3-4:** EducationalOrchestrator (TDD)
- **Day 5:** TruthVerificationEngine (TDD)

### Week 2: Interaction (100 hours)
- **Days 1-2:** NextStepGenerator, KnowledgeLevelDetector, FaultDetectionReporter (TDD)
- **Days 3-4:** MCP tools (cortex_ask, cortex_verify_claim)
- **Day 5:** Integration tests

### Week 3: Enhancement (40 hours)
- **Days 1-2:** TutorialSystem, ExampleGenerator
- **Days 3-4:** End-to-end testing, optimization
- **Day 5:** Documentation, deployment

**Total Effort:** 240 hours (2-3 weeks)

---

## 🎯 KEY FEATURES

### 1. Implementation Truth ✅

**Problem:** Documentation drifts, users get outdated information  
**Solution:** Always verify against live code before responding

```python
# Every ASK response includes:
verification = truth_engine.verify_claim(user_query)
if verification.accurate:
    respond_with_evidence()
else:
    correct_with_actual_truth()
```

### 2. Progressive Disclosure ✅

**Problem:** One-size-fits-all explanations overwhelm or bore users  
**Solution:** Adapt explanation depth to knowledge level

```yaml
Beginner: Simple language, analogies, high-level
Intermediate: Technical detail, integration patterns
Advanced: Deep architecture, trade-offs, extensions
```

### 3. Numbered Next Steps ✅

**Problem:** Users don't know what to explore next  
**Solution:** Every response ends with 3-5 intelligent options

```markdown
### 🔮 Next Steps

Choose an option to continue learning:

1. **Deeper Dive** - More detail on current topic
2. **Related Concept** - Connected architecture
3. **Practical Example** - Hands-on demonstration
4. **Common Pitfall** - What to avoid
5. **Advanced Topic** - Next level learning
```

### 4. Fault Detection ✅

**Problem:** Issues hide in docs/code mismatch  
**Solution:** Proactively detect drift, broken wiring, missing tests

```yaml
Detected Issues:
  - Documentation drift (P1)
  - Broken wiring (P0)
  - Missing tests (P1)
  - Implementation gaps (P0-P2)
```

### 5. Evidence-Based ✅

**Problem:** Users can't verify claims  
**Solution:** Include file paths, line numbers, test references

```markdown
**Evidence:**
- File: `cortex/orchestrators/core/master_orchestrator.py` (lines 140-180)
- Wiring: `cortex/wiring/specifications/wiring.yaml` (line 45)
- Tests: `tests/unit/orchestrators/core/test_master_orchestrator.py` (28 tests)
- Last Modified: 2026-01-28 by Asif Hussain
```

---

## 📊 COMPONENTS TO IMPLEMENT

### Python Components (9 modules, 150 tests)

| Component | Lines | Tests | Coverage |
|-----------|-------|-------|----------|
| EducationalOrchestrator | 600 | 20 | 90%+ |
| TruthVerificationEngine | 800 | 30 | 95%+ |
| ImplementationVerifier | 500 | 25 | 90%+ |
| NextStepGenerator | 400 | 20 | 90%+ |
| KnowledgeLevelDetector | 350 | 18 | 90%+ |
| FaultDetectionReporter | 450 | 22 | 90%+ |
| cortex_ask (MCP) | 300 | 15 | 95%+ |
| cortex_verify_claim (MCP) | 250 | 12 | 95%+ |
| TutorialSystem | 550 | 25 | 90%+ |
| ExampleGenerator | 400 | 20 | 90%+ |

**Total:** ~4,600 lines of production code + ~2,000 lines of tests

### Integration Tests (30 scenarios)
- End-to-end ASK mode flows
- InteractionOrchestrator integration
- ChallengeEngine coordination
- MCP tool invocation
- Progressive disclosure validation

### Acceptance Tests (20 scenarios)
- Beginner → Intermediate → Advanced progression
- Truth verification accuracy
- Fault detection effectiveness
- Next-step intelligence
- User engagement patterns

---

## 🔄 INNOVATION FRAMEWORK ENHANCEMENT

### Current (Phase 8)
```python
ChallengeEngine:
  - Detects disagreement with user
  - Generates alternatives
  - Presents options
```

### Enhanced (Phase 22)
```python
ChallengeEngine + EducationalOrchestrator:
  - Detects disagreement OR knowledge gap
  - Generates alternatives OR educational content
  - Presents options with numbered next steps
  - Verifies against implementation truth
  - Detects faults proactively
  - Progressive disclosure based on user level
```

**Integration Pattern:**
```python
# In InteractionOrchestrator:
if user_has_misconception:
    # Use ChallengeEngine for gentle correction
    challenge = challenge_engine.generate(request, context)
    educational_response = enhance_with_evidence(challenge)

elif user_asks_question:
    # Use EducationalOrchestrator for truth-based learning
    verification = truth_engine.verify(extracted_claims)
    response = educational_orch.generate(
        question=user_query,
        verified_truth=verification,
        knowledge_level=detected_level
    )
```

---

## 🎨 USER EXPERIENCE

### Example Interaction

```
User: "How does the InteractionOrchestrator work?"

CORTEX ASK:
┌────────────────────────────────────────────────────┐
│ 🧠 CORTEX ASK                                      │
│ Author: Asif Hussain | Level: Intermediate ✅      │
├────────────────────────────────────────────────────┤
│ How InteractionOrchestrator Works                  │
│                                                     │
│ Implementation Reality:                            │
│ InteractionOrchestrator wraps ConversationProtocol │
│ and integrates ChallengeEngine to enforce          │
│ communication patterns on every turn.              │
│                                                     │
│ Evidence:                                          │
│ - File: cortex/orchestrators/core/                 │
│         interaction_orchestrator.py (525 lines)    │
│ - Tests: test_interaction_orchestrator.py (45)     │
│                                                     │
│ [Detailed technical explanation...]                │
│                                                     │
│ 🔮 Next Steps:                                     │
│                                                     │
│ 1. See Real Challenge Flow                         │
│ 2. Understand LENS Context                         │
│ 3. Explore ChallengeEngine                         │
│ 4. View Integration Pattern                        │
│ 5. Try Building Custom Challenge                   │
│                                                     │
│ Tip: Option 3 shows CORTEX innovation framework    │
└────────────────────────────────────────────────────┘

User selects: 3

CORTEX ASK:
[Generates deep dive on ChallengeEngine with:
 - Live code examples
 - Design patterns
 - Extension points
 - New set of 5 numbered options]
```

---

## 📋 SUCCESS METRICS

| Metric | Target | Measure |
|--------|--------|---------|
| Implementation Accuracy | 95%+ | Truth verification success rate |
| User Engagement | 80%+ | % users selecting next step |
| Fault Detection | 90%+ | Issues identified vs total |
| Response Time | <2s | Simple query latency |
| Test Coverage | 90%+ | pytest --cov |
| Knowledge Level Match | 85%+ | User satisfaction with depth |
| Drift Detection | 85%+ | Docs vs code mismatches found |

---

## 🛡️ GOVERNANCE COMPLIANCE

| Rule | Implementation |
|------|----------------|
| CORE-002 | No markdown generation (inline only) |
| CORE-008 | TDD for all 12 components (150 tests) |
| CORE-011 | Type hints mandatory (mypy validation) |
| CORE-012 | Google-style docstrings all functions |
| CORE-027 | Audit trail (AC_START → AC_COMPLETE) |
| CORE-029 | Response header mandatory |
| CORE-030 | Implementation truth enforcement |
| CORE-035 | Single canonical implementation |
| MCP-FIRST | All functionality via MCP tools |

---

## 🔗 INTEGRATION WITH EXISTING PHASES

| Phase | Integration |
|-------|-------------|
| **Phase 8** | Uses ChallengeEngine for intelligent disagreement |
| **Phase 19** | Uses LENS for code intelligence |
| **Phase 20** | Integrates company + CORTEX knowledge YAMLs |
| **Phase 20.5** | Knowledge synthesis for educational content |

---

## 🚨 RISK MITIGATION

| Risk | Mitigation |
|------|------------|
| Verification overhead slows responses | Cache verification results, async checking |
| Options too generic/unhelpful | Context-aware generation, user feedback loop |
| Over-correction confuses users | Gentle corrections, evidence-based explanations |
| Documentation maintenance burden | Automated drift detection, proactive alerts |

---

## 📂 FILE STRUCTURE

### New Files (24 total)

```
.github/
  prompts/
    cortex-ask.prompt.md                    ✅ CREATED
  agents/
    education/
      cortex-ask-coordinator.md             ✅ CREATED
      truth-verifier.md                     ✅ CREATED

cortex/
  orchestrators/
    education/
      __init__.py                           ⏳ TODO
      educational_orchestrator.py           ⏳ TODO
  
  brain/
    verification/
      __init__.py                           ⏳ TODO
      truth_verification_engine.py          ⏳ TODO
      implementation_verifier.py            ⏳ TODO
    
    education/
      __init__.py                           ⏳ TODO
      next_step_generator.py                ⏳ TODO
      knowledge_level_detector.py           ⏳ TODO
      fault_detection_reporter.py           ⏳ TODO
      tutorial_system.py                    ⏳ TODO
      example_generator.py                  ⏳ TODO
  
  mcp/
    tools/
      cortex_ask.py                         ⏳ TODO
      cortex_verify_claim.py                ⏳ TODO

tests/
  unit/
    orchestrators/education/
      test_educational_orchestrator.py      ⏳ TODO
    brain/
      verification/
        test_truth_verification_engine.py   ⏳ TODO
        test_implementation_verifier.py     ⏳ TODO
      education/
        test_next_step_generator.py         ⏳ TODO
        test_knowledge_level_detector.py    ⏳ TODO
        test_fault_detection_reporter.py    ⏳ TODO
        test_tutorial_system.py             ⏳ TODO
        test_example_generator.py           ⏳ TODO
    mcp/tools/
      test_cortex_ask.py                    ⏳ TODO
      test_cortex_verify_claim.py           ⏳ TODO
  
  integration/
    education/
      test_ask_mode_flow.py                 ⏳ TODO

_workspaces/cortex-plan/
  PHASE-22-ASK-MODE-SYSTEM.yaml             ✅ CREATED
  PHASE-22-QUICK-REFERENCE.md               ✅ CREATED
```

### Modified Files (2 total)

```
.github/prompts/cortex-architect.prompt.md  ⏳ TODO (Add ASK mode detection)
cortex/wiring/specifications/wiring.yaml    ⏳ TODO (Register EducationalOrchestrator)
```

---

## ✅ DEFINITION OF DONE

### Specification Phase (COMPLETE ✅)
- [x] PHASE-22-ASK-MODE-SYSTEM.yaml created (850 lines)
- [x] PHASE-22-QUICK-REFERENCE.md created (600 lines)
- [x] cortex-ask.prompt.md created (850 lines)
- [x] cortex-ask-coordinator.md created (450 lines)
- [x] truth-verifier.md created (500 lines)
- [x] cortex-plan-index.md updated
- [x] Phase summary document created

### Implementation Phase (PENDING)
- [ ] All 12 Python components implemented with TDD
- [ ] 150 unit tests passing (90%+ coverage)
- [ ] 30 integration tests passing
- [ ] 20 acceptance tests passing
- [ ] MCP tools registered and tested
- [ ] cortex-architect.prompt.md integration
- [ ] wiring.yaml registration
- [ ] Quick reference guide validated
- [ ] Phase completion report
- [ ] Production deployment

---

## 🎯 NEXT ACTIONS

### Immediate (Week 1)
1. **Review Specification** - Stakeholder approval
2. **Update cortex-architect.prompt.md** - Add ASK mode detection
3. **Begin TDD Implementation** - EducationalOrchestrator first
4. **Setup test infrastructure** - Create test directories

### Short-term (Week 2-3)
5. **Implement core components** - Following TDD discipline
6. **Create MCP tools** - cortex_ask, cortex_verify_claim
7. **Integration testing** - End-to-end flows
8. **Documentation** - Inline docstrings, user guides

### Medium-term (Post-implementation)
9. **User testing** - Gather feedback on numbered options
10. **Performance optimization** - Cache verification results
11. **Tutorial content** - Build guided learning paths
12. **Metrics dashboard** - Track engagement and accuracy

---

## 💡 INNOVATION HIGHLIGHTS

### 1. Implementation Truth Enforcement
First educational system that ALWAYS verifies against live code, never trusting docs alone.

### 2. Progressive Disclosure Engine
Adapts explanation complexity based on detected user knowledge level.

### 3. Intelligent Next Steps
Context-aware numbered options that predict user's likely next question.

### 4. Proactive Fault Detection
Identifies drift, broken wiring, missing tests during educational interaction.

### 5. Evidence-Based Learning
Every claim backed by file paths, line numbers, test references.

---

## 📚 RELATED READING

- [cortex-ask.prompt.md](.github/prompts/cortex-ask.prompt.md) - Full prompt specification
- [PHASE-22-QUICK-REFERENCE.md](PHASE-22-QUICK-REFERENCE.md) - Implementation guide
- [PHASE-22-ASK-MODE-SYSTEM.yaml](PHASE-22-ASK-MODE-SYSTEM.yaml) - Complete specification
- [cortex-architect.prompt.md](.github/prompts/cortex-architect.prompt.md) - Parent mode router
- [PHASE-8-CHALLENGE-ORCHESTRATOR.yaml](PHASE-8-CHALLENGE-ORCHESTRATOR.yaml) - Innovation framework foundation

---

## 🎓 LEARNING OBJECTIVES

Users of ASK mode will be able to:

1. **Understand CORTEX Architecture** - From high-level to deep internals
2. **Verify Implementation Claims** - Check what's actually built vs documented
3. **Explore Progressively** - Follow numbered paths to deeper knowledge
4. **Identify Issues Early** - Learn about drift and gaps proactively
5. **Contribute Confidently** - Understand extension points and patterns

---

**Status:** ✅ SPECIFICATION COMPLETE  
**Phase:** PHASE-22  
**Priority:** P1 High  
**Duration:** 2-3 weeks (240 hours)  
**Dependencies:** Phase 8 (Challenge), Phase 19 (LENS), Phase 20 (Knowledge)

**Ready for:** Review and Approval 🚀

---

*"The beautiful thing about learning is that no one can take it away from you." - B.B. King*  
*CORTEX ASK makes learning beautiful with implementation truth. ✨*
