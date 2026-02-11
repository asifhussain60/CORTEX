# Wave 7 Track 3: Support Layer Elimination
**Status:** READY FOR EXECUTION  
**Planned Duration:** 6-8 days  
**Target Completion:** 18-24 day Wave 7 timeline  
**Author:** CORTEX Architecture | **Timestamp:** 2026-02-11

---

## 🎯 Executive Summary

**Objective:** Eliminate orphan/specialized support orchestrators and consolidate remaining functionality into unified frameworks

**Track 2 Completed ✅:**
- EnhancedRefactoringOrchestrator: Consolidated 3 orchestrators (Extract, CodeReview, SecurityReview)
- DebuggerOrchestrator: New unified debugging capability
- 46/48 tests passing (2 intentionally skipped), 96%+ coverage
- 3 → 2 orchestrators in domain layer

**Track 3 Scope:**
- Identify 11 orphan/specialized support orchestrators (from 26 total)
- Consolidate into 3-4 unified support frameworks
- Target: 26 → 15 orchestrators (42% reduction)
- Create behavioral contracts for all consolidations

**Quality Gates:**
- ✅ CORE-008: TDD (tests before code)
- ✅ CORE-011: 100% type hints
- ✅ CORE-012: 100% docstrings
- ✅ CORE-013: Specific exception handling
- ✅ CORE-026/027: Git checkpoints + AC markers
- ✅ CORE-030: Implementation truth
- ✅ CORE-035: No duplication

---

## 📊 Current Orchestrator Inventory

### Core Orchestrators (8 - PROTECTED)
```
✅ MasterOrchestrator         - Intent routing, workflow orchestration
✅ TDDOrchestrator            - Test-driven development execution
✅ LENSSynthesis              - Code analysis (L.E.N.S. framework)
✅ IntentRouter               - Intent classification
✅ EnforcementOrchestrator    - Governance rule enforcement (7 agents)
✅ InteractionOrchestrator    - User interaction patterns
✅ WorkflowOrchestrator       - State machine workflows
✅ IncrementalTaskDecomposer  - Task decomposition

CONSOLIDATION IMPACT: 0/8 (core layer stable)
```

### Domain Orchestrators (6 AFTER Track 2 - TARGET 4)
```
✅ EnhancedRefactoringOrchestrator (NEW)   - Unified refactoring engine
✅ DebuggerOrchestrator (NEW)              - Zero-friction debugging
⚪ PlanningOrchestrator                    - Phase lifecycle management
⚪ DocumentationOrchestrator               - Knowledge synthesis
⚪ RefactoringOrchestrator (old)           - DEPRECATED → Merge into Enhanced
⚪ DomainKnowledgeOrchestrator             - Domain inference

CONSOLIDATION IMPACT: 2/6 → 4/6 target (RefactoringOrchestrator + 1 other)
```

### Support Orchestrators (12 - TARGET 3-4)
**These are the focus of Track 3:**

```
1. RepositoryOnboardingOrchestrator       - Repository profiling/onboarding
2. ToolDiscoveryOrchestrator              - Tool catalog + discovery
3. LENSOrchestrator                       - LENS pipeline orchestration
4. RecommendationGate                     - Challenge generation, disagreement detection
5. EducationalOrchestrator                - Prompt engineering, learning
6. PlanOrchestrator                       - Phase planning (NEW - duplicate?)
7. OnboardingOrchestrator                 - User onboarding (vs RepositoryOnboarding?)
8. DashboardGenerationOrchestrator        - Dashboard creation
9. MetaAuditOrchestrator                  - Holistic validation auditing
10. ChallengeEngine                       - Challenge generation (vs RecommendationGate?)
11. CodeReviewOrchestrator (old)          - DEPRECATED → Merged into Enhanced v2
12. SecurityReviewEngine (old)            - DEPRECATED → Merged into Enhanced v2

CONSOLIDATION TARGETS:
- Group 1 (Onboarding): RepositoryOnboardingOrchestrator + OnboardingOrchestrator
- Group 2 (Analysis): LENSOrchestrator + (Analysis utilities)
- Group 3 (Quality): RecommendationGate + ChallengeEngine + MetaAuditOrchestrator
- Group 4 (Discovery): ToolDiscoveryOrchestrator + EducationalOrchestrator
- Deprecate: CodeReviewOrchestrator, SecurityReviewEngine (moved to Enhanced v2)
- Clarify: PlanOrchestrator vs PlanningOrchestrator (merge into 1)

CONSOLIDATION IMPACT: 12 → 4 target (67% reduction)
```

---

## 🔄 Track 3 Execution Plan

### Phase 1: Analysis & Planning (1 day)
**Goal:** Identify consolidation opportunities and create behavioral contracts

**Tasks:**
1. ✅ Audit orchestrator dependencies (grep for imports, inheritance)
2. ✅ Identify redundant capabilities (RecommendationGate vs ChallengeEngine)
3. ✅ Create consolidation groups (see above)
4. ✅ Map public API surfaces (what methods are used externally)
5. ✅ Write consolidation proposal document
6. ✅ Create 4 behavioral contract test files (1 per consolidation group)

**Deliverable:** 4 test suites with RED-phase tests (tests before code)

### Phase 2: RED → GREEN Consolidation (4-5 days)
**Goal:** Implement each consolidation group iteratively

#### Consolidation Group 1: OnboardingOrchestrator (1 day)
```
MERGE: RepositoryOnboardingOrchestrator + OnboardingOrchestrator
NEW: UnifiedOnboardingOrchestrator

Public API:
  • onboard_repository(repo_path) → RepositoryProfile
  • onboard_user(user_config) → UserProfile
  • validate_onboarding(profile) → ValidationResult

Tests: 12 behavioral contracts
  ✓ Repository profiling + validation
  ✓ User profile creation
  ✓ Conflict resolution
  ✓ Error handling

Status: ⏳ PENDING
```

#### Consolidation Group 2: AnalysisOrchestrator (1 day)
```
MERGE: LENSOrchestrator + Analysis utilities
NEW: UnifiedAnalysisOrchestrator

Public API:
  • analyze(code, scope) → LENSResult
  • detect_patterns(code) → PatternList
  • validate_analysis(result) → QualityScore

Tests: 14 behavioral contracts
  ✓ All LENS analysis modes (complexity, security, dependencies)
  ✓ Pattern detection
  ✓ Caching behavior
  ✓ Error scenarios

Status: ⏳ PENDING
```

#### Consolidation Group 3: QualityAssuranceOrchestrator (1-2 days)
```
MERGE: RecommendationGate + ChallengeEngine + MetaAuditOrchestrator
NEW: UnifiedQualityAssuranceOrchestrator

Public API:
  • challenge_proposal(request) → ChallengeResult
  • generate_recommendations(code) → RecommendationList
  • audit_holistically(target) → AuditReport

Tests: 16 behavioral contracts
  ✓ Challenge generation (LENS analysis)
  ✓ Disagreement detection
  ✓ Recommendation ranking
  ✓ Holistic audit validation
  ✓ Integration with enforcement

Status: ⏳ PENDING
```

#### Consolidation Group 4: DiscoveryOrchestrator (1 day)
```
MERGE: ToolDiscoveryOrchestrator + EducationalOrchestrator
NEW: UnifiedDiscoveryOrchestrator

Public API:
  • discover_tools(query) → ToolList
  • learn_feature(topic) → LearningModule
  • recommend_learning_path(goal) → CoursePath

Tests: 10 behavioral contracts
  ✓ Tool discovery + caching
  ✓ Learning module synthesis
  ✓ Path recommendations
  ✓ Knowledge graph traversal

Status: ⏳ PENDING
```

#### Deprecate Old Orchestrators (0.5 days)
```
DEPRECATE: CodeReviewOrchestrator, SecurityReviewEngine (moved to Enhanced v2)
           RefactoringOrchestrator (moved to Enhanced v2)
           PlanningOrchestrator (clarify vs PlanOrchestrator)

ACTION:
  1. Create deprecation notices (move to deprecated/ folder)
  2. Add warnings to __init__.py
  3. Update imports in wiring contract
  4. Document migration paths

Status: ⏳ PENDING
```

### Phase 3: REFACTOR & Optimization (1-2 days)
**Goal:** Optimize consolidations and boost coverage to 85%+

**Tasks:**
1. Add 20+ edge case tests (empty inputs, error paths, performance)
2. Optimize complexity detection and pattern matching
3. Cache validation strategies
4. Performance tuning (target: <200ms latency)
5. Verify governance compliance (CORE-008/011/012/013/026/027/030/035)

**Coverage Target:** 85%+ (benchmark: Track 2 achieved 96%+)

### Phase 4: Validation & Commit (0.5 days)
**Goal:** Final validation and atomic commit

**Tasks:**
1. Run combined test suite (all Track 1-3 tests)
2. Verify orchestrator count: 26 → 15 (42% reduction)
3. Check no regressions (Track 1-2 tests still passing)
4. Commit with comprehensive message
5. Prepare Track 4 execution (Orphan cleanup)

**Success Criteria:**
- ✅ 60+ new tests (4 consolidation groups)
- ✅ 4 new unified orchestrators
- ✅ 8 deprecated orchestrators
- ✅ 85%+ coverage
- ✅ 0 regressions
- ✅ All governance rules compliant

---

## 📈 Consolidation Metrics

### Before Track 3
| Layer | Count | Purpose |
|-------|-------|---------|
| Core | 8 | Foundation |
| Domain | 6 | Refactoring + Debugging |
| Support | 12 | Specialized functions |
| **Total** | **26** | - |

### After Track 3 (Target)
| Layer | Count | Purpose |
|-------|-------|---------|
| Core | 8 | Foundation (unchanged) |
| Domain | 4 | Refactoring + Debugging + Planning + Docs |
| Support | 3-4 | Onboarding + Analysis + QA + Discovery |
| **Total** | **15-16** | 42% reduction |

### Efficiency Gains
```
Orchestrator Count Reduction: 26 → 15 (42%)
Code Duplication Elimination: ~200 LOC removed
Maintenance Surface Area: -23 files (estimate)
Test Coverage: 55 → 120+ tests across all layers
Cognitive Load: Reduced (fewer integration points)
```

---

## 🚀 Ready-to-Execute Checklist

**Prerequisites for Track 3:**
- [x] Track 1 Complete (55/55 tests, 100% coverage) ✅
- [x] Track 2 Complete (46/48 tests, 96%+ coverage) ✅
- [x] Git repository clean (all commits staged) ✅
- [x] Orchestrator audit complete ✅
- [x] Consolidation groups identified ✅
- [x] Test templates prepared ✅

**When to Start:**
- User issues: `continue autonomously and silently`
- Or: `/implement Track 3: Support Layer Elimination`

**Execution Mode:**
- Silent autonomous (progress via ASCII bars)
- TDD: Tests before code (RED → GREEN → REFACTOR)
- Atomic commits after each consolidation group
- Holistic validation after REFACTOR phase

---

## 📝 References

- **Wave 7 Plan:** REPRIORITIZATION-SUMMARY-2026-02-11.md
- **Track 2 Results:** commit 6489c8e8f
- **Domain Consolidation Tests:** tests/integration/orchestrators/test_domain_consolidation_track_2.py
- **Governance Rules:** cortex/governance/rules/
- **Orchestrator Registry:** cortex-registry/_cortex-master/

---

## ⏱️ Timeline Projection

| Phase | Duration | Cumulative |
|-------|----------|-----------|
| Phase 1: Analysis | 1d | 1d |
| Phase 2: Implementation | 4-5d | 5-6d |
| Phase 3: REFACTOR | 1-2d | 6-8d |
| Phase 4: Validation | 0.5d | 6.5-8.5d |
| **Total Track 3** | **6-8 days** | - |
| **Wave 7 Cumulative** | - | **12-16 days** (+ Tracks 4-5) |

---

**Status:** READY FOR EXECUTION ✅  
**Next:** Await user directive to proceed with Track 3
